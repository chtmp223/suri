# Inference script for HF models
# %%capture
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import os
import sys

sys.path.append("../")
from utils import *
import sys
import pandas as pd
from tqdm import trange
from peft import PeftModel, PeftConfig
from transformers import AutoModelForCausalLM
from datasets import load_dataset

os.environ["TOKENIZERS_PARALLELISM"] = "False"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
torch.cuda.empty_cache()

# %%capture
if sys.argv[1] == "orpo":
    model_name = "chtmp223/suri-i-orpo"
    base_model_name = "mistralai/Mistral-7B-Instruct-v0.2"
    config = PeftConfig.from_pretrained(model_name)
    base_model = AutoModelForCausalLM.from_pretrained(base_model_name).to(device)
    model = PeftModel.from_pretrained(base_model, model_name).to(device)
    tokenizer = AutoTokenizer.from_pretrained(base_model_name)
    tag_name = "orpo"
    out = "orpo.jsonl"
elif sys.argv[1] == "sft":
    model_name = "chtmp223/suri-sft"
    base_model_name = "mistralai/Mistral-7B-Instruct-v0.2"
    config = PeftConfig.from_pretrained(model_name)
    base_model = AutoModelForCausalLM.from_pretrained(base_model_name).to(device)
    model = PeftModel.from_pretrained(base_model, model_name).to(device)
    tokenizer = AutoTokenizer.from_pretrained(base_model_name)
    tag_name = "sft"
    out = "sft.jsonl"
else:
    raise ValueError("Invalid config specified! Must be either 'orpo' or 'sft'.")

print("_".join(model_name.split("/")[-2:]))
dataset = pd.DataFrame(
    load_dataset("chtmp223/suri", split="test", cache_dir=os.environ["HF_HOME"])
)
print(f"Inference with {sys.argv[1]} model!")

# %%capture
ft = []
for i in trange(len(dataset)):
    prompt = [
        {
            "role": "user",
            "content": dataset.main_ins.tolist()[i]
            + "\n"
            + dataset.cons_chosen.tolist()[i],
        }
    ]
    input_context = tokenizer.apply_chat_template(
        prompt, add_generation_prompt=True, tokenize=False
    )
    input_ids = tokenizer.encode(
        input_context, return_tensors="pt", add_special_tokens=False
    ).to(model.device)
    output = model.generate(
        input_ids, max_length=10000, do_sample=True, use_cache=True
    ).cpu()
    output_text = tokenizer.decode(output[0]).split("[/INST]")[-1].strip("</s>").strip()
    ft.append(output_text)
dataset["response"] = ft
dataset.to_json(out, lines=True, orient="records")
