# VLLM inference script for HF models
from vllm import LLM, SamplingParams
from vllm.lora.request import LoRARequest
from datasets import load_dataset
import os
import pandas as pd
from transformers import AutoTokenizer
import sys
import torch

torch.cuda.empty_cache()
# ------------
#  Model setup
# ------------
model_dict = {
    "mistral": "mistralai/Mistral-7B-Instruct-v0.2",
    "suri_orpo": "chtmp223/suri-i-orpo",
    "suri_sft": "chtmp223/suri-sft",
}

assert len(sys.argv) == 2, "Please provide the model name"
assert sys.argv[1] in model_dict.keys(), "Invalid model name"
model_name = model_dict[sys.argv[1]]
lora = sys.argv[1] in ["suri_orpo", "suri_sft"]

# ------------
#  Inference
# ------------
df = pd.DataFrame(
    load_dataset("chtmp223/suri", split="test", cache_dir=os.environ["HF_HOME"])
)
prompts = [
    df["main_ins"].tolist()[i] + "\n" + df["cons_chosen"].tolist()[i]
    for i in range(len(df))
]
sampling_params = SamplingParams(max_tokens=10000, temperature=1.0, top_p=1.0)

if not lora:
    llm = LLM(model=model_name, enable_lora=lora, tensor_parallel_size=2)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    prompts = [
        tokenizer.apply_chat_template(
            [
                {
                    "role": "user",
                    "content": "You are a helpful writing assistant. Please follow the instruction below and generate at least 5000 words"
                    + prompt,
                }
            ],
            add_generation_prompt=True,
            tokenize=False,
        )
        for prompt in prompts
    ]
    outputs = llm.generate(prompts, sampling_params)
else:  # Lora adapter
    llm = LLM(model=model_dict["mistral"], enable_lora=lora)
    tokenizer = AutoTokenizer.from_pretrained(model_dict["mistral"])
    prompts = [
        tokenizer.apply_chat_template(
            [
                {
                    "role": "user",
                    "content": "You are a helpful writing assistant. Please follow the instruction below and generate at least 5000 words"
                    + prompt,
                }
            ],
            add_generation_prompt=True,
            tokenize=False,
        )
        for prompt in prompts
    ]
    outputs = llm.generate(
        prompts, sampling_params, lora_request=LoRARequest(sys.argv[1], 1, model_name)
    )
output = [out.outputs[0].text for out in outputs]
df[sys.argv[1]] = output
df.to_csv(f"vllm_{sys.argv[1]}.csv", index=False)
