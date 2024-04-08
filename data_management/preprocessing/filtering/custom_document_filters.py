from hojichar import document_filters, Document
from fugashi import Tagger

import spacy

from os import PathLike
from typing import Any, Union
import re

tagger = Tagger("-Owakati")

# spacyの英語モデルをロードする
nlp = spacy.load("en_core_web_sm")

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


class DiscardAdultContentEn(document_filters.NgWordsFilterEn):
    """
    TokenFilter の実装例です.
    英語の成人向けコンテンツを閾値に応じて排除します.
    """

    def __init__(
        self,
        dict_path: Union[str, PathLike] = document_filters.BASE_PATH
        / "dict/adult_keywords_en.txt",
        threshold: float = 0.01,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(dict_path, *args, **kwargs)
        self.threshold = threshold

    def apply(self, doc: Document) -> Document:
        adult_keywords_pattern = self.keyword_pat
        tokens = [token.text for token in nlp(doc.text)]
        matches = re.findall(adult_keywords_pattern, doc.text)
        adult_content_count = len(matches)
        total_words_count = len(tokens)

        if (
            total_words_count > 0
            and adult_content_count / total_words_count > self.threshold
        ):
            doc.is_rejected = True

        return doc
