# https://www.notion.so/matsuolab-geniac/058ba3281fdf4b08b2d828b834799d27?pvs=4#e1fb6d15f1da4b2ca9a47bb28cf0ecbe

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import argparse
import time
from tqdm import tqdm


def jsonl_to_parquet_direct(input_path, output_path, batch_size=100000):
    start_time = time.time()
    reader = pd.read_json(input_path, lines=True, chunksize=batch_size)

    parquet_writer = None
    schema = None

    for batch in tqdm(reader, desc="Converting Batches"):
        # delete columns except "text"
        batch = batch.drop(columns=[col for col in batch.columns if col != "text"])  # noqa: E501

        table = pa.Table.from_pandas(batch)
        if schema is None:
            schema = table.schema
            parquet_writer = pq.ParquetWriter(output_path, schema, compression="snappy")  # noqa: E501

        parquet_writer.write_table(table)

    if parquet_writer:
        parquet_writer.close()

    end_time = time.time()
    tqdm.write(f"Conversion completed in {end_time - start_time:.2f} seconds")


def parse_arguments():
    parser = argparse.ArgumentParser(description="Convert JSON Lines to Parquet")  # noqa: E501
    parser.add_argument(
        "--input", type=str, required=True, help="Path to the input JSON Lines file."  # noqa: E501
    )
    parser.add_argument(
        "--output", type=str, required=True, help="Path to the output Parquet file."  # noqa: E501
    )
    parser.add_argument(
        "--batch_size", type=int, default=100000, help="Number of records per batch."  # noqa: E501
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    jsonl_to_parquet_direct(args.input, args.output, args.batch_size)
