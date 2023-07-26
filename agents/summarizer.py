import openai
from bs4 import BeautifulSoup as bsoup

def html_extract(text: str):
    """
    Extracts the important information from an html page.
    :param text: the text to extract from
    """

    # Remove all css and js
    soup = bsoup(text, "html5lib")
    for script in soup(["script", "style"]):
        script.decompose()
    text = soup.get_text()

    # Remove excessive newlines and whitespaces
    text = text.replace("\t", "")
    text = text.replace("    ", "")
    text = text.replace("\n\n", "\n")

    print(len(text))

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {"role": "system", "content": "Extract the important information from this html page. Summarize when necessary."},
            {"role": "user", "content": text}
        ]
    )
    return response["choices"][0]["message"]["content"]