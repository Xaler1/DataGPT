import secret.keys as keys
from src.gpt_function import gpt_function
import json
import requests
import datetime

@gpt_function
def get_news_headlines(topic: str):
    """
    Useful for getting the news headlines for a particular topic
    :param topic: the topic to get the news headlines for
    """

    url = f"https://newsdata.io/api/1/news?apikey={keys.news_key}&q={topic}"
    response = requests.get(url)
    json_data = json.loads(response.text)

    articles = []
    for article in json_data["results"]:
        articles.append({
            "headline": article["title"],
            "source": article["source_id"],
            "country": article["country"][0],
        })

    filtered = {
        "articles": articles
    }

    return filtered


@gpt_function
def get_full_article(headline: str):
    """
    Useful for getting the full article for a particular headline
    :param headline: the exact headline to get the full article for
    """

    url = f"https://newsdata.io/api/1/news?apikey={keys.news_key}&q={headline}"
    response = requests.get(url)
    json_data = json.loads(response.text)

    article = json_data["results"][0]

    return { "article": article["content"]}
