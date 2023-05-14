import os
import openai
from dotenv import load_dotenv

load_dotenv()


def get_chatgpt_text_response(prompt_text: str) -> str:
    openai.api_key = os.getenv("OPENAI_API_KEY")
    response = openai.Completion.create(
        engine="text-davinci-002", prompt=prompt_text, max_tokens=60
    )
    response_text = response.choices[0].text
    return response_text


if __name__ == "__main__":
    prompt_text = """Who is the president of Yemen?"""
    print(get_chatgpt_text_response(prompt_text))
