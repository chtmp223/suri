#!/usr/bin/env python
# coding=utf-8
# Copyright 2023 The HuggingFace Inc. team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import random
import sys
from typing import Any, Dict
from tqdm import trange

import torch
torch.cuda.empty_cache()
import transformers
from transformers import AutoModelForCausalLM, set_seed

# Import the modified alignment and trl libraries
sys.path.append("../lib/")

from alignment_mod import (
    DataArguments,
    H4ArgumentParser,
    ModelArguments,
    apply_chat_template,
    get_checkpoint,
    get_datasets,
    get_kbit_device_map,
    get_peft_config,
    get_quantization_config,
    get_tokenizer,
)
from alignment_mod.configs import ORPOConfig
from trl_mod import ORPOTrainer, setup_chat_format


logger = logging.getLogger(__name__)


def main():
    parser = H4ArgumentParser((ModelArguments, DataArguments, ORPOConfig))
    model_args, data_args, training_args = parser.parse()

    #######
    # Setup
    #######
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    log_level = training_args.get_process_log_level()
    logger.setLevel(log_level)
    transformers.utils.logging.set_verbosity(log_level)
    transformers.utils.logging.enable_default_handler()
    transformers.utils.logging.enable_explicit_format()

    # Log on each process the small summary:
    logger.info(f"Model parameters {model_args}")
    logger.info(f"Data parameters {data_args}")
    logger.info(f"Training/evaluation parameters {training_args}")

    # Check for last checkpoint
    last_checkpoint = get_checkpoint(training_args)
    if last_checkpoint is not None and training_args.resume_from_checkpoint is None:
        logger.info(f"Checkpoint detected, resuming training at {last_checkpoint=}.")

    # Set seed for reproducibility
    set_seed(training_args.seed)

    ###############
    # Load datasets
    ###############
    raw_datasets = get_datasets(
        data_args,
        splits=data_args.dataset_splits,
        configs=data_args.dataset_configs,
        columns_to_keep=[
            "prompt_chosen",
            "prompt_rejected",
            "answer",
        ],
    )
    logger.info(
        f"Training on the following splits: {[split + ' : ' + str(dset.num_rows) for split, dset in raw_datasets.items()]}"
    )
    column_names = list(raw_datasets["train"].features)

    #####################################
    # Load tokenizer and process datasets
    #####################################
    data_args.truncation_side = "left"  # Truncate from left to ensure we don't lose labels in final turn
    tokenizer = get_tokenizer(model_args, data_args)
    tokenizer.model_max_length = training_args.max_length       # Override alignment-handbook's weird setting
    tokenizer.padding_token = tokenizer.unk_token
    tokenizer.padding_side = "right"

    torch_dtype = None
    if model_args.torch_dtype == "auto" or model_args.torch_dtype is None:
        torch_dtype = model_args.torch_dtype
    else:
        try:
            torch_dtype = getattr(torch, model_args.torch_dtype)
        except AttributeError:
            raise ValueError(f"`torch_dtype` can be either `torch.dtype` or `\"auto\"`, but received {model_args.torch_dtype}")

    quantization_config = get_quantization_config(model_args)

    model = AutoModelForCausalLM.from_pretrained(
        model_args.model_name_or_path,
        revision=model_args.model_revision,
        trust_remote_code=model_args.trust_remote_code,
        use_flash_attention_2=model_args.use_flash_attention_2,
        torch_dtype=torch_dtype,
        use_cache=False if training_args.gradient_checkpointing else True,
        device_map=get_kbit_device_map() if quantization_config is not None else None,
        quantization_config=quantization_config,
    )

    # For ChatML we need to add special tokens and resize the embedding layer
    if "<|im_start|>" in tokenizer.chat_template:
        model, tokenizer = setup_chat_format(model, tokenizer)

    #####################
    # Apply chat template
    #####################
    raw_datasets = raw_datasets.map(
        apply_chat_template,
        fn_kwargs={
            "tokenizer": tokenizer,
            "task": "orpo",
            #"auto_insert_empty_system_msg": data_args.auto_insert_empty_system_msg,
            "auto_insert_empty_system_msg": False,
        },
        num_proc=data_args.preprocessing_num_workers,
        #remove_columns=column_names,
        desc="Formatting comparisons with prompt template",
    )

    # Log a few random samples from the training set:
    logger.info(f"Accepted prompt 0 of the raw training set:\n\n{raw_datasets['train'][0]['prompt_chosen']}")
    logger.info(f"Rejected prompt 0 of the raw training set:\n\n{raw_datasets['train'][0]['prompt_rejected']}")
    logger.info(f"First response of the raw training set:\n\n{raw_datasets['train'][0]['answer']}")
    assert raw_datasets['train'][0]['prompt_chosen'] != raw_datasets['train'][0]['prompt_rejected'], "Prompt and chosen are the same"
    
    ##########################
    # Instantiate ORPO trainer
    ##########################
    trainer = ORPOTrainer(
        model,
        args=training_args,
        train_dataset=raw_datasets["train"],
        eval_dataset=raw_datasets["test"] if "test" in raw_datasets else None,
        tokenizer=tokenizer,
        peft_config=get_peft_config(model_args),  # type: ignore
    )

    ###############
    # Training loop
    ###############
    checkpoint = None
    if training_args.resume_from_checkpoint is not None:
        checkpoint = training_args.resume_from_checkpoint
    elif last_checkpoint is not None:
        checkpoint = last_checkpoint
    train_result = trainer.train(resume_from_checkpoint=checkpoint)
    metrics = train_result.metrics
    metrics["train_samples"] = len(raw_datasets["train"])
    trainer.log_metrics("train", metrics)
    trainer.save_metrics("train", metrics)
    trainer.save_state()

    logger.info("*** Training complete ***")

    ##################################
    # Save model and create model card
    ##################################
    logger.info("*** Save model ***")
    if trainer.is_fsdp_enabled:
        trainer.accelerator.state.fsdp_plugin.set_state_dict_type("FULL_STATE_DICT")
    trainer.save_model(training_args.output_dir)
    logger.info(f"Model saved to {training_args.output_dir}")

    # Save everything else on main process
    kwargs = {
        "finetuned_from": model_args.model_name_or_path,
        "dataset": list(data_args.dataset_mixer.keys()),
        "dataset_tags": list(data_args.dataset_mixer.keys()),
        "tags": ["alignment-handbook"],
    }
    if trainer.accelerator.is_main_process:
        trainer.create_model_card(**kwargs)
        # Restore k,v cache for fast inference
        trainer.model.config.use_cache = True
        trainer.model.config.save_pretrained(training_args.output_dir)

    ##########
    # Evaluate
    ##########
    if training_args.do_eval and "test" in raw_datasets:
        logger.info("*** Evaluate ***")
        metrics = trainer.evaluate()
        metrics["eval_samples"] = len(raw_datasets["test"])
        trainer.log_metrics("eval", metrics)
        trainer.save_metrics("eval", metrics)

    if training_args.push_to_hub is True:
        logger.info("Pushing to hub...")
        trainer.push_to_hub(**kwargs)

    logger.info("*** Training complete! ***")


if __name__ == "__main__":
    main()
