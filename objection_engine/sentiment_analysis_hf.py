from objection_engine.sentiment_analysis import SentimentAnalyzer
from transformers import pipeline
from os import environ

environ["TOKENIZERS_PARALLELISM"] = "false"  # to make HF Transformers happy

SENTIMENT_MODEL_PATH = "cardiffnlp/twitter-xlm-roberta-base-sentiment"


class HuggingFaceAnalyzer(SentimentAnalyzer):
    def __init__(self):
        super().__init__()
        self.__analyzer = pipeline(
            "sentiment-analysis",
            model=SENTIMENT_MODEL_PATH,
            tokenizer=SENTIMENT_MODEL_PATH,
        )

    def get_sentiment(self, text: str):
        result = self.__analyzer(text)[0]
        return result
