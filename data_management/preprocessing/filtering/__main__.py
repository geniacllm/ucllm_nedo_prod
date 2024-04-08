import argparse
import json
import os
from datetime import datetime

from hojichar import Compose, Document, document_filters, tokenization
from preprocessing.filtering import (custom_document_filters,
                                     custom_token_filters, custom_tokenization)


def process_json_lines(lines: list[str], output_base: str, stats: list[dict], lang: str):
    remained_lines = []

    if lang == 'ja':
        print("Japanese filtering...")

        filters = [
            document_filters.JSONLoader(),
            document_filters.DocumentNormalizer(),
            document_filters.DiscardBBSComments(),
            document_filters.DiscardAds(),
            document_filters.DiscardDiscriminationContentJa(),
            custom_document_filters.DiscardAdultContentJa(),
            custom_tokenization.NewLineSentenceTokenizer(),
            custom_token_filters.RemoveOneword(),
            custom_tokenization.MergeTokens(delimiter="\n"),
            custom_tokenization.WakatiTokenizer(),
            custom_token_filters.RemoveDate(),
            tokenization.MergeTokens(),
            document_filters.MaskPersonalInformation(),
            document_filters.JSONDumper(dump_reason=True),
        ]
    elif lang == 'en':
        print("English filtering...")

        filters = [
            document_filters.JSONLoader(),
            document_filters.DocumentNormalizer(),
            custom_document_filters.DiscardAdultContentEn(),
            custom_tokenization.NewLineSentenceTokenizer(),
            custom_token_filters.RemoveOneword(),
            custom_tokenization.MergeTokens(delimiter="\n"),
            custom_token_filters.RemoveDate(),
            document_filters.MaskPersonalInformation(),
            document_filters.JSONDumper(dump_reason=True),

            # TODO: 
            # 以下は日本語のみのフィルターなので、英語に対応する必要がある。
            # 差別表現のフィルターを追加する。
            # 
            # document_filters.DiscardDiscriminationContentEn(),
            # document_filters.DiscardBBSComments(),
            # document_filters.DiscardAds(),
        ]
    else:
        raise ValueError(f"Unsupported language: {lang}")

    cleaner = Compose(filters)

    with open(os.path.join(output_base, "rejected.filtering.jsonl"), "w") as rejected:
        with open(os.path.join(output_base, "result.filtering.jsonl"), "w") as writer:
            for line in lines:
                result = cleaner.apply(Document(line))
                if result.is_rejected:
                    rejected.write(result.text + "\n")
                else:
                    writer.write(result.text + "\n")
                    remained_lines.append(result.text)

    with open(os.path.join(output_base, "stat.filtering.jsonl"), "w") as writer:
        writer.write(json.dumps(cleaner.statistics, ensure_ascii=False) + "\n")

    stats.append(cleaner.statistics)

    return remained_lines


def __readlines(input_file: str):
    with open(input_file) as fp:
        return fp.readlines()


def filtering(input_dir: str, output_base: str, lang: str = 'ja'):
    os.makedirs(output_base, exist_ok=True)

    file_lines = {
        input_file: __readlines(os.path.join(input_dir, input_file))
        for input_file in os.listdir(input_dir)
        if input_file.endswith(".jsonl")
    }

    stats = []
    for input_file, json_lines in file_lines.items():
        range_part = os.path.splitext(input_file)[0].split("_")[-1]
        output_dir_name = f"{lang}_part_{range_part}"
        output_base_for_input: str = os.path.join(output_base, output_dir_name)
        os.makedirs(output_base_for_input, exist_ok=True)

        lines = process_json_lines(json_lines, output_base_for_input, stats, lang)
        file_lines[input_file] = lines

    with open(
        os.path.join(output_base, "results.filtering.jsonl"), "w", encoding="utf8"
    ) as writer:
        for _, lines in file_lines.items():
            for line in lines:
                writer.write(line + "\n")

    with open(
        os.path.join(output_base, "stats.filtering.jsonl"), "w", encoding="utf8"
    ) as writer:
        for stat in stats:
            json.dump(stat, writer, ensure_ascii=False)
            writer.write("\n")


def main():
    parser = argparse.ArgumentParser(description="Process some documents.")
    parser.add_argument(
        "--input_dir",
        type=str,
        help="The input directory containing documents to process",
        required=True,
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        help="The input file containing documents to process",
        required=False,
        default="./tmp/output",
    )
    parser.add_argument(
        "--lang",
        type=str,
        help="The language of the documents to process. ja or en",
        required=False,
        default="ja",
        choices=["ja", "en"],
    )
    args = parser.parse_args()

    start = datetime.now()
    output_base = os.path.join(args.output_dir, start.strftime("%Y%m%d%H%M%S"))

    filtering(input_dir=args.input_dir, output_base=output_base, lang=args.lang)


if __name__ == "__main__":
    main()
