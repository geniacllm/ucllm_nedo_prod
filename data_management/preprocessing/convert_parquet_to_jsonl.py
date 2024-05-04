# https://www.notion.so/matsuolab-geniac/058ba3281fdf4b08b2d828b834799d27?pvs=4#f0fdbb8b8f6545fe801c6bb15c8c88af

import pyarrow.parquet as pq
import json
import argparse
import time
from tqdm import tqdm


def parquet_to_jsonl_direct(input_path, output_path, batch_size=100000):
    start_time = time.time()
    parquet_file = pq.ParquetFile(input_path)
    num_rows = parquet_file.metadata.num_rows

    with open(output_path, 'w', encoding='utf-8') as output_file:
        processed_rows = 0
        for batch in tqdm(parquet_file.iter_batches(batch_size=batch_size, columns=None), total=(num_rows // batch_size) + 1, desc="Converting Batches"):  # noqa
            table = batch.to_pandas()
            for record in table.to_dict(orient="records"):
                json_record = json.dumps(record, ensure_ascii=False)
                output_file.write(json_record + '\n')
            processed_rows += len(table)
        tqdm.write(f"Processed {processed_rows} rows out of {num_rows}")

    end_time = time.time()
    tqdm.write(f"Conversion completed in {end_time - start_time:.2f} seconds")


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Convert Parquet to JSON Lines')
    parser.add_argument("--input", type=str, required=True,
                        help="Path to the input Parquet file.")
    parser.add_argument("--output", type=str, required=True,
                        help="Path to the output JSON Lines file.")
    parser.add_argument("--batch_size", type=int,
                        default=100000, help="Number of records per batch.")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    parquet_to_jsonl_direct(args.input, args.output, args.batch_size)
