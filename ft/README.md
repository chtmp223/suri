# Fine-tuning models with I-ORPO and SFT

This directory contains the code for fine-tuning the I-ORPO and SFT models on the Suri dataset. We base our implementation on 🤗 [Alignment Handbook](https://github.com/huggingface/alignment-handbook) and [TRL](https://github.com/huggingface/trl), but modified for I-ORPO. 

## Getting Started
We use the modified versions of alignment and trl packages, which are stored in `ft/lib`. 

## I-ORPO Usage
I-ORPO takes in a dataset with three columns:
    - prompt_chosen: Contains system and user chosen prompt (with a single constraint)
    - prompt_rejected: Contains system and user rejected prompt (with a single constraint) 
    - answer: Contains assistant's gold response
To fine-tune using orpo, modify the `i-orpo/run_orpo.py` and `i-orpo/orpo.yml` script with the correct paths and run the script.
    - Dataset: You need to replaec `chtmp223/suri` with your own version of the dataset, with placeholder text being replaced by books3 text. 
    - Update `output_dir`, `hub_model_id`, `run_name`, and any hyperparameters to fit your compute budget. 
    - Update paths in `run_orpo.sh`. 


## SFT Usage
SFT takes in a dataset with a single column: 
    - messages: Contains user and assistant messages. 
To fine-tune using SFT, modify the `sft/run_sft.py` and `sft/sft.yml` script with the correct paths and run the script.
    - Dataset: You need to replaec `chtmp223/suri` with your own version of the dataset, with placeholder text being replaced by books3 text. 
    - Update `output_dir`, `hub_model_id`, `run_name`, and any hyperparameters to fit your compute budget. 
    - Update paths in `run_sft.sh`. 


## Inference
To run inference on the fine-tuned model, modify the `hf.py` script in the `eval` folder with the correct paths and run the script.