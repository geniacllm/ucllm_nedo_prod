from fugashi import Tagger
from hojichar import Document, Filter

tagger = Tagger("-Owakati")

# NOTE:
# トークナイズの必要性が不明だったのでコメントアウトしています
# 必要性がある場合はコメントアウトを解除し、main.py の filters に追加してください
#
# import nltk
# from nltk.tokenize import sent_tokenize
# nltk.download('punkt')
# 
# class EnglishSentenceTokenizer(Filter):
#     """
#     An English sentence tokenizer that uses NLTK's sent_tokenize to split text into sentences.
#     """

#     def apply(self, document: Document) -> Document:
#         """
#         Applies sentence tokenization on the document's text and updates the document's tokens.

#         :param document: A dictionary representing the document, with at least a 'text' key.
#         :return: The updated document with a 'tokens' key containing the list of sentences.
#         """
#         tokens = self.tokenize(document.text)  # document['text'] -> document.text
#         document.set_tokens(tokens)  # document['tokens'] = tokens -> 適切なメソッドを使用
#         return document

#     def tokenize(self, text: str) -> list[str]:
#         """
#         Splits the text into sentences using NLTK's sent_tokenize.

#         >>> tokenizer = EnglishSentenceTokenizer()
#         >>> tokenizer.tokenize("Good morning. How are you? I'm fine, thank you. See you.")
#         ['Good morning.', 'How are you?', "I'm fine, thank you.", 'See you.']
#         """
#         return sent_tokenize(text)


class WakatiTokenizer(Filter):
    """
    Tokenizer の実装例です.
    fugashi を用いて文を分割します.
    """
    def apply(self, document: Document) -> Document:
        tokens = self.tokenize(document.text)
        document.set_tokens(tokens)
        return document

    def tokenize(self, text: str) -> list[str]:
        """
        >>> WakatiTokenizer().tokenize("おはよう。おやすみ。ありがとう。さよなら。")
        ['おはよう。', 'おやすみ。', 'ありがとう。', 'さよなら。']
        """
        return tagger.parse(text).split()


class NewLineSentenceTokenizer(Filter):
    """
    日本語を想定したセンテンス単位のトーカナイザです.
    改行文字で文章を区切ります.
    """

    def apply(self, document: Document) -> Document:
        tokens = self.tokenize(document.text)
        document.set_tokens(tokens)
        return document

    def tokenize(self, text: str) -> list[str]:
        """
        >>> NewLineSentenceTokenizer().tokenize("おはよう。\nおやすみ。\nありがとう。\nさよなら。")
        ['おはよう。', 'おやすみ。', 'ありがとう。', 'さよなら。']
        """
        return text.split("\n")


class MergeTokens(Filter):
    """
    Mergerの実装例です.
    破棄されていないトークンをdelimeterで結合し, Document を更新します.
    """

    def __init__(
        self, delimiter: str = "", before_merge_callback=None, *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.delimiter = delimiter

    def merge(self, tokens: list[str]) -> str:
        """
        >>> MergeTokens("\n").merge(["hoo", "bar"])
        'hoo\nbar'
        """
        return self.delimiter.join(tokens)

    def apply(self, document: Document) -> Document:
        remained_tokens = [
            token.text for token in document.tokens if not token.is_rejected
        ]
        document.text = self.merge(remained_tokens)
        return document
