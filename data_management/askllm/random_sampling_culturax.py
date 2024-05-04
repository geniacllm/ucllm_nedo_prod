# randomly sample 50 texts from the CulturaX dataset
# and output them as a CSV file.

# pip install numpy datasets
# python random_sampling_culturax.py > culturax_samples_50_seed_42.csv

import csv
import sys

import numpy as np
from datasets import load_dataset

# TODO: command-line arguments?
seed = 42
num_samples = 50
max_text_length = 50000  # limit for Google Sheets

dataset = load_dataset(
    "uonlp/CulturaX",
    "ja",
    split="train",
    cache_dir="/persistentshare/storage/team_kumagai/datasets",
)

np.random.seed(seed)
indices = np.arange(dataset.num_rows)  # num_rows is 111188475
np.random.shuffle(indices)

writer = csv.writer(sys.stdout)
writer.writerow(["id", "text"])

for index in indices[:num_samples]:
    i = int(index)
    text = dataset[i]["text"]
    if len(text) > max_text_length:
        sys.stderr.write(
            f"Text at index {i} is too long ({len(text)} characters),"
            f" truncating to {max_text_length} characters\n"
        )
        text = text[:max_text_length]
    writer.writerow([i, text])
