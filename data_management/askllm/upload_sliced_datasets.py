import argparse
import io
import time
from dataclasses import dataclass

from huggingface_hub import HfFileSystem

TOP_PERCENTS = [0.2, 0.4, 0.6, 0.8, 1]

parser = argparse.ArgumentParser()
parser.add_argument("--source", type=str)
parser.add_argument("--destination", type=str)
args = parser.parse_args()

source_file_path = args.source
repo_id = args.destination

epoch = time.time()


@dataclass
class Dataset:
    max_linenum: int
    writer: io.TextIOWrapper


def build_datasets(file_path, percents):
    fs = HfFileSystem()

    with open(file_path, "r") as file:
        total_lines = sum(1 for _ in file)

    datasets = []
    for percent in percents:
        max_linenum = int(percent * total_lines)
        writer = fs.open(
            f"datasets/{repo_id}/{epoch}-{percent * 100}.txt",
            "wb",
        )
        datasets.append(
            Dataset(
                max_linenum=max_linenum,
                writer=writer,
            )
        )
    return datasets


datasets = build_datasets(
    source_file_path,
    TOP_PERCENTS,
)

with open(source_file_path, "rb+") as f:
    for line_count, line in enumerate(f, start=1):
        for dataset in datasets:
            if line_count <= dataset.max_linenum:
                dataset.writer.write(line)

for dataset in datasets:
    dataset.writer.close()
