# Fine-tuning models with I-ORPO and SFT

This directory contains the code for fine-tuning the I-ORPO and SFT models on the Suri dataset. We base our implementation on 🤗 [Alignment Handbook](https://github.com/huggingface/alignment-handbook) and [TRL](https://github.com/huggingface/trl), but modified for I-ORPO. 

## Getting Started
Install the modified version of Alignment Handbook and Trl: 
```
pip install -r requirements.txt
cd ft
python -m pip install .     
```

## I-ORPO Usage
I-ORPO takes in a dataset with three columns:
    - prompt_chosen: Contains system and user chosen prompt (with a single constraint)
    - prompt_rejected: Contains system and user rejected prompt (with a single constraint) 
    - answer: Contains assistant's gold response
To fine-tune using orpo, modify the `i-orpo/run_orpo.py` and `i-orpo/orpo.yml` script with the correct paths and run the script.


## SFT Usage
SFT takes in a dataset with a single column: 
    - messages: Contains user and assistant messages. 
To fine-tune using SFT, modify the `sft/run_sft.py` and `sft/sft.yml` script with the correct paths and run the script.

## Inference
To run inference on the fine-tuned model, modify the `hf.py` script in the `eval` folder with the correct paths and run the script.