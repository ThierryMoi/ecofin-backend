import os
from dotenv import load_dotenv
import tiktoken
import openai

load_dotenv()

openai.api_key  = os.getenv('OPENAI_API_KEY')

#MAX_TOKENS = 4096
#ENCODING = tiktoken.get_encoding("cl100k_base")
LIMIT_TOKEN = 10000


CLIENT_OPENAI = openai.OpenAI()


def split_string_with_limit(text: str, limit: int, encoding: tiktoken.Encoding):
    tokens = encoding.encode(text)
    parts = []
    text_parts = []
    current_part = []
    current_count = 0
    
    
    for token in tokens:
        current_part.append(token)
        current_count += 1

        if current_count >= limit:
            parts.append(current_part)
            current_part = []
            current_count = 0

    if current_part:
        parts.append(current_part)

    for part in parts:
        text = [
            encoding.decode_single_token_bytes(token).decode("utf-8", errors="replace")
            for token in part
        ]
        text_parts.append("".join(text))

    return text_parts




