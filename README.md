# 🦙 Suri: Multi-constraint Instruction Following for Long-form Text Generation

[![arXiV](https://img.shields.io/badge/arxiv-soon-red)]() [![Website](https://img.shields.io/badge/website-link-purple)](https://chtmp223.github.io/suri) [![Dataset](https://img.shields.io/badge/dataset-huggingface-yellow)](https://huggingface.co/datasets/chtmp223/suri) [![Suri-I-ORPO](https://img.shields.io/badge/iorpo-model-green)](https://huggingface.co/chtmp223/suri-i-orpo) [![Suri-SFT](https://img.shields.io/badge/sft-model-blue)](https://huggingface.co/chtmp223/suri-sft)

![TopicGPT Pipeline Overview](assets/img/suri.png)
This repository hosts the code and data for our paper, [Suri: Multi-constraint instruction following for long-form text generation](arxiv). 

In this paper, we release an instruction following dataset with multi-constraint instructions and long-form gold responses (2k-5k words). We also introduce I-ORPO, a variant of Odds Ratio Preference Optimization (ORPO) that is modified to accept (x+, x-, y) as inputs rather than (x, y+, y-). We demonstrate the effectiveness of the dataset by fine-tuning Mistral-7B-Instruct with the SFT and I-ORPO method. 

## 📣 Updates
- **[2024-06-25]**: The code and data for Suri are now available. 

## 📦 Using Suri
### Getting Started
1. Install the requirements for Suri:
    ```
    conda create -n suri python=3.10 
    conda activate suri
    pip install -r requirements.txt
    python -m pip install flash-attn --no-build-isolation
    huggingface-cli login       # Log in to Huggingface using your access token 
    sudo apt-get install git-lfs
    ```
2. Set up the Huggingface cache directory:
    - Open your shell configuration file, which is typically `~/.bashrc` or `~/.bash_profile` for Bash, or `~/.zshrc` for Zsh. 
    - Add `HF_HOME` huggingface cache directory path to your configuration file: `HF_HOME=/path/to/huggingface_cache`.
    - Add `HF_TOKEN` huggingface access token to your configuration file: `HF_TOKEN=<your_token>`. 
    - Save and close the file. Source the file to apply the changes: `source ~/.bashrc` or `source ~/.bash_profile` or `source ~/.zshrc`.
    - Double-check that the environment variable is set correctly: `echo $HF_HOME`. 


### Project Structure
```
.
├── README.md
├── assets
│   ├── img
│   └── styles
├── data
├── eval
│   ├── automatic
│   ├── human
│   └── inference
├── ft
│   ├── README.md
│   ├── deepspeed_zero3.yaml
│   ├── i-orpo
│   ├── lib
│   │   ├── alignment_mod
│   │   └── trl_mod
│   └── sft
├── index.html
├── prompts
├── requirements.txt
└── utils.py
```
- `data` contains `b3.py`, which can be used to reconstruct the gold response of the books3 portion of the dataset. 
- `eval` contains: 
    - `automatic`, which includes code to compute the ranking accuracy metric. 
    - `human`, which includes the XML interface for the human evaluation. 
    - `inference`, which includes code to do inference with the fine-tuned models using either Transformers Huggingface or vLLM.
- `ft` contains code to fine-tune the models using I-ORPO or SFT: 
    - `i-orpo` directory includes `orpo.yaml`, which defines the training hyperparameters; `run_orpo.py`, which contains the training code; and `run_orpo.sh`, which consolidates the training process into a single executable command.
    - `sft` directory includes `sft.yaml`, which defines the training hyperparameters; `run_sft.py`, which contains the training code; and `run_sft.sh`, which consolidates the training process into a single executable command.
    - `deepspeed_zero3.yaml` contains the hyperparameters for deepspeed zero3. 
- `prompts` contains all prompts used in the paper. 


### Dataset 
- The dataset is available on Huggingface: [https://huggingface.co/datasets/suri](https://huggingface.co/datasets/suri). 
- Due to copyright concerns, we only release the path of the sampled data from the Books3 subset. For interested users with access to the Books3 dataset, we include a script (`script/data/b3.py`) to reconstruct this portion of the dataset. 
    - First, make sure to set the DATA_DIR variable to the path of the books3 dataset on your local machine.
    - Next, modify the code to either save the reconstructed dataset to a csv file or push to a new Huggingface repository. 
    - Finally, run the code using `python b3.py`. 


### I-ORPO & SFT implementation 
- The I-ORPO model is available on Huggingface: [https://huggingface.co/chtmp223/suri-i-orpo](https://huggingface.co/chtmp223/suri-i-orpo). The SFT model is available on Huggingface: [https://huggingface.co/chtmp223/suri-sft](https://huggingface.co/chtmp223/suri-sft).
- We include the code for training and evaluation in the `script/ft/` directory. See the README.md file in that folder for more information.


## 📜 Citation
If you find this work useful, please consider citing:
```

```