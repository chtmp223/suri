# Script to process books3 dataset and replace assistant 
# content with the processed book
# Usage: python b3.py
# Note: Make sure to set the DATA_DIR variable to the path of the books3 dataset
# This script should take 30 minutes to run.

import os
import concurrent.futures
import regex as re
import traceback
from tqdm import tqdm
import sys

sys.path.append("../")
from utils import *
import numpy as np
import pandas as pd
from datasets import load_dataset, Dataset

DATA_DIR = ""               #TODO: Insert your books3 path here


def process_book(book_path):
    """
    Process and truncate each book
    - book_path: path to the book
    """
    try:
        # Read the book
        with open(book_path, "r", encoding="utf-8") as file:
            text = file.read()

        # Find the first chapter + second chapter
        # such that the difference between them is at least 500 characters
        chapter1_pattern = re.compile(r"chapter\s+(0?1|one|I)[*.\s\n]", re.IGNORECASE)
        chapter2_pattern = re.compile(r"chapter\s+(0?2|two|I)[*.\s\n]", re.IGNORECASE)
        chapter1_match = chapter1_pattern.search(text)
        chapter2_match = chapter2_pattern.search(
            text, chapter1_match.end() if chapter1_match else 0
        )
        diff = -1
        if chapter1_match and chapter2_match:
            diff = chapter2_match.start() - chapter1_match.end()
            while diff < 500:
                chapter1_match = chapter1_pattern.search(text, chapter2_match.end())
                chapter2_match = chapter2_pattern.search(
                    text, chapter1_match.end() if chapter1_match else 0
                )
                if chapter1_match and chapter2_match:
                    diff = chapter2_match.start() - chapter1_match.end()
                else:
                    break

        result_text = ""
        word_count = 0
        result = []

        if chapter1_match and chapter2_match:
            start_index = chapter1_match.start()
            filtered_text = text[start_index : start_index + 60000]
            paragraphs = re.split(r"\n\s*\n*", filtered_text)
        else:
            start_index = int(len(text) * 0.02)
            filtered_text = text[start_index : start_index + 60000]
            paragraphs = re.split(r"\n\s*\n*", filtered_text)
            i = 1
            for i in range(1, len(paragraphs)):  # Skip the first paragraph
                if len(paragraphs[i].split()) >= 20:
                    break
            paragraphs = paragraphs[i:]

        for p in paragraphs:
            result.append(p)
            word_count += len(p.split())
            if word_count > 5024:
                break
        result_text = "\n".join(result)

        # Make sure that the book ends with a full sentence if possible
        result_text = truncating_words(result_text, 5024)
        result_text = strip_trailing_text(result_text)

        return result_text

    except Exception as e:
        print(f"Error processing {book_path.split('/')[-2:]}: {e}\n{traceback.format_exc()}. Make sure that your data directory path is stored in the DATA_DIR variable.")


def retrieve_book(dataset):
    """
    Retrieve book for rows with type 'b3'
    Replace assistant content in 'messages' and 'answer' columns with the processed book
    """
    dataset = dataset.to_pandas()
    for i in tqdm(range(len(dataset))):
        if dataset["type"].tolist()[i] == "b3":
            book_path = os.path.join(DATA_DIR, dataset["id"].tolist()[i])
            book = process_book(book_path)
            # Replace only the assistant content
            if book: 
                for j in range(len(dataset["messages"].tolist()[i])):
                    if dataset["messages"].tolist()[i][j]["role"] == "assistant":
                        dataset["messages"].tolist()[i][j]["content"] = book
                dataset.at[i, "answer"] = [{"role": "assistant", "content": book}]
    dataset = Dataset.from_pandas(dataset)
    return dataset


if __name__ == "__main__":
    # Load the dataset
    dataset = load_dataset("chtmp223/suri", 
                           cache_dir=os.environ["HF_HOME"], 
                           token=os.environ["HF_TOKEN"])
    for split in dataset.keys():
        dataset[split] = retrieve_book(dataset[split])

    # Save the dataset to csv files
    dataset['train'].to_pandas().to_csv("train.csv", index=False)
    dataset['dev'].to_pandas().to_csv("dev.csv", index=False)
    dataset['test'].to_pandas().to_csv("test.csv", index=False)
    
    # Save the dataset to huggingface hub 
    #dataset.push_to_hub("...")
