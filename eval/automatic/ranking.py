import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel, PeftConfig
from tqdm import trange
import pandas as pd

torch.cuda.empty_cache()
from datasets import load_dataset
import sys
import os
import random

torch.cuda.empty_cache()

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def read_file(args):
    """
    Return (prompt_ins, prompt_ins_mod)
    """
    # Load the DataFrame
    df = pd.DataFrame(
        load_dataset("chtmp223/suri", split="test", cache_dir=os.environ["HF_HOME"])
    )
    # Format prompt
    df["prompt_ins"] = df["main_ins"] + "\n" + df["cons_chosen"]
    df["prompt_mod"] = df["main_ins_mod"] + "\n" + df["cons_chosen"]

    return df


def sequence_prob(tokenizer, model, prompt, response):
    """
    Calculate the sum of log probabilities for the predefined output
    sequence p(assistant text|user text)
    - tokenizer, model: Tokenizer and model
    - prompt: User text
    - response: Assistant text
    """
    # Format and tokenize the user text and assistant text
    prompt = [
        {"role": "user", "content": prompt},
        {"role": "assistant", "content": response},
    ]
    input_tokens = tokenizer.apply_chat_template(
        [prompt[0]],
        add_generation_prompt=False,
        return_tensors="pt",
        add_special_tokens=False,
    ).to(model.device)
    tokens = tokenizer.apply_chat_template(
        prompt,
        add_generation_prompt=False,
        return_tensors="pt",
        add_special_tokens=False,
    ).to(model.device)

    with torch.no_grad():
        outputs = model(tokens)
        logits = outputs.logits

    log_sum = 0
    start_index = input_tokens.shape[1] - 1
    end_index = tokens.shape[1] - 1

    for i in range(start_index, end_index):
        past_tok, current_tok = i, i + 1
        token_logit = logits[0, past_tok, :]
        token_log_probs = torch.nn.functional.log_softmax(token_logit, dim=-1)
        log_token_prob = token_log_probs[tokens[0, current_tok]].item()
        log_sum += log_token_prob

    return log_sum


def build_generator(model, tokenizer, max_gen_len=2, use_cache=True):
    def response(prompt):
        text = prompt
        prompt = [{"role": "user", "content": prompt}]
        inputs = tokenizer.apply_chat_template(
            prompt,
            add_generation_prompt=True,
            return_tensors="pt",
            add_special_tokens=False,
        ).to(model.device)

        # Enable output_scores to get logits
        output = model.generate(
            inputs,
            max_new_tokens=max_gen_len,
            use_cache=use_cache,
            output_scores=True,
            return_dict_in_generate=True,
            num_beams=1,
            do_sample=False,
        )

        # Decoding answer
        out = tokenizer.decode(output.sequences[0])
        out = out.split(text.strip(tokenizer.eos_token))[-1].strip()

        # Check if "1" and "2" are in the tokenizer's vocabulary
        token_1 = tokenizer.convert_tokens_to_ids("1")
        token_2 = tokenizer.convert_tokens_to_ids("2")

        if token_1 == tokenizer.unk_token_id or token_2 == tokenizer.unk_token_id:
            print("Not found in the vocab")
            return None, None, None

        # Check if eos token is in the output
        if tokenizer.eos_token_id in output.sequences[0]:
            try:
                logits = output.scores[-2][0]
            except:
                logits = output.scores[-1][0]
        else:
            logits = output.scores[-1][0]

        # Convert logits to probabilities (log softmax)
        log_probs = torch.nn.functional.log_softmax(logits, dim=0)

        log_prob_1 = log_prob_2 = None
        if token_1 != tokenizer.unk_token_id:
            log_prob_1 = log_probs[token_1].item()  # Log probability of "1"
        if token_2 != tokenizer.unk_token_id:
            log_prob_2 = log_probs[token_2].item()  # Log probability of "2"

        return out, log_prob_1, log_prob_2

    return response


if __name__ == "__main__":
    # Map model name to the model path
    model_dict = {
        "mistral": "mistralai/Mistral-7B-Instruct-v0.2",
        "suri_orpo": "chtmp223/suri-i-orpo",
        "suri_sft": "chtmp223/suri-sft",
    }

    assert sys.argv[1] in model_dict.keys(), "Invalid model name!"

    args = {
        "base_model": model_dict[sys.argv[1]],
        "cache_dir": os.environ["HF_HOME"],
        "flash_attn": True,
        "temperature": 0.0,
        "top_p": 0.0,
    }

    if sys.argv[1] in ["suri_orpo", "suri_sft"]:
        base_model_name = model_dict["mistral"]
        config = PeftConfig.from_pretrained(args["base_model"])
        base_model = AutoModelForCausalLM.from_pretrained(
            base_model_name,
            attn_implementation="flash_attention_2",
            torch_dtype="auto",
        ).to(device)
        model = PeftModel.from_pretrained(
            base_model,
            args["base_model"],
            attn_implementation="flash_attention_2",
            torch_dtype="auto",
        ).to(device)
        tokenizer = AutoTokenizer.from_pretrained(base_model_name)
    else:
        # Load model and tokenizer
        model = AutoModelForCausalLM.from_pretrained(
            args["base_model"],
            cache_dir=args["cache_dir"],
            attn_implementation="flash_attention_2",
            torch_dtype="auto",
            device_map="auto",
        )

        tokenizer = AutoTokenizer.from_pretrained(
            args["base_model"],
            cache_dir=args["cache_dir"],
            device_map="auto",
        )
    model.eval()
    torch.cuda.empty_cache()

    with torch.no_grad():
        print(sys.argv[1])
        respond = build_generator(model, tokenizer, use_cache=True)

        df = read_file(args)
        prompt_ins = df.prompt_ins.tolist()
        prompt_mod = df.prompt_mod.tolist()
        text = df.formatted_text.tolist()
        prompt_text = open("prompts/prompt_eval.md", "r").read()

        prex, pref = [], []
        prex_1, prex_2 = [], []
        pref_1, pref_2 = [], []
        for i in trange(len(prompt_ins)):
            output_ins = sequence_prob(tokenizer, model, prompt_ins[i], text[i])
            output_mod = sequence_prob(tokenizer, model, prompt_mod[i], text[i])
            if output_ins > output_mod:
                diff = 1
            else:
                diff = 0
            prex.append(diff)
            prex_1.append(output_ins)
            prex_2.append(output_mod)

            # Format prompt
            prompting = prompt_text.format(
                ins1=prompt_ins[i], ins2=prompt_mod[i], text=text[i]
            )
            prompting_rev = prompt_text.format(
                ins1=prompt_mod[i], ins2=prompt_ins[i], text=text[i]
            )
            out_1, log1_1, log2_1 = respond(prompting)
            out_2, log1_2, log2_2 = respond(prompting_rev)
            if log1_1 > log2_1 and log1_2 < log2_2:
                pref.append(2)
            elif log1_1 < log2_1 and log1_2 > log2_2:
                pref.append(0)
            else:
                pref.append(1)
            pref_1.append((log1_1, log2_1))
            pref_2.append((log1_2, log2_2))

        # Save to dataframe
        df = pd.DataFrame(
            {
                "prefix": prex,
                "pref": pref,
                "prefix_correct": prex_1,
                "prefix_incorrect": prex_2,
                "preference_normal": pref_1,
                "preference_reverse": pref_2,
            }
        )
        df.to_csv(f"ranking_{sys.argv[1]}.csv", index=False)
