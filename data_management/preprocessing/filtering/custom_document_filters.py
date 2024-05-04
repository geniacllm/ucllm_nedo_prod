from hojichar import document_filters, Document
from hojichar.core.filter_interface import Filter
from fugashi import Tagger
from faker import Faker

from os import PathLike
from typing import Any, Union
import re

tagger = Tagger("-Owakati")
faker_jp = Faker("ja_JP")


class DiscardAdultContentJa(document_filters.NgWordsFilterJa):
    """
    TokenFilter の実装例です.
    日本語の成人向けコンテンツを閾値に応じて排除します.
    """

    def __init__(
        self,
        dict_path: Union[str, PathLike] = document_filters.BASE_PATH
        / "dict/adult_keywords_ja.txt",
        threshold: float = 0.01,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(dict_path, *args, **kwargs)
        self.threshold = threshold

    def apply(self, doc: Document) -> Document:
        adult_keywords_pattern = self.keyword_pat
        matches = re.findall(adult_keywords_pattern, doc.text)
        adult_content_count = len(matches)
        total_words_count = len(tagger.parse(doc.text).split())

        if (
            total_words_count > 0
            and adult_content_count / total_words_count > self.threshold
        ):
            doc.is_rejected = True

        return doc


class MaskPersonNamesJa(Filter):
    """
    日本語の人名に該当するであろう単語をマスクします.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    def apply(self, doc: Document) -> Document:
        doc.text = self._mask_person_names(doc.text)
        return doc

    def _mask_person_names(self, text: str) -> str:
        parsed = tagger.parseToNodeList(text)

        masked_parsed_word_list = []
        for word in parsed:
            if word.pos.split(",")[2] != "人名":
                masked_parsed_word_list.append(word.surface)
            else:
                masked_parsed_word_list.append(
                    "[MASKED]"
                )  # 人名の部分を"[MASKED]"で置換
        masked_text = "".join(masked_parsed_word_list)

        # faker_jp でマスク箇所を適当な人名に置換するためのパターンを定義
        masked_fullname_pattern = re.compile(r"(\[MASKED\]){2,}")
        masked_single_name_pattern = re.compile(r"\[MASKED\]")

        # "[MASKED][MASKED]..."のように2回以上連続する場合はフルネームと見做し、適当な名前に置換する
        masked_text = re.sub(
            masked_fullname_pattern,
            faker_jp.name(),
            masked_text,
        )

        # "[MASKED]"が1回のみの場合は名前の一部と見做し、適当な苗字に置換する
        masked_text = re.sub(
            masked_single_name_pattern,
            faker_jp.last_name(),
            masked_text,
        )

        return masked_text
