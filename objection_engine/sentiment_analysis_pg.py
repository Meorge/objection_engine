from random import random
from objection_engine.sentiment_analysis import SentimentAnalyzer
from polyglot.text import Text


class PolyglotAnalyzer(SentimentAnalyzer):
    def __init__(self):
        super().__init__()

    def get_sentiment(self, text: str):
        poly_text = Text(text)
        try:
            polarity = poly_text.polarity
        except:
            polarity = 0

        print(f'Polyglot analyzer result for "{text}": {polarity}')
        if polarity > 0.35:
            print(f"Positive")
            return {"label": "positive", "score": 1.0}

        if polarity < -0.35 and (polarity > -1 or random() > 0.25):
            print(f"Negative")
            return {"label": "negative", "score": 1.0}

        print("Neutral")
        return {"label": "positive", "score": 0.0}
