from bs4 import BeautifulSoup
import javalang
from .utils import locate_token, next_nl


def fixTrailingComment(violation: dict, tokens: list, whitespace: list, checkstyleData: BeautifulSoup, **kwargs) -> list:
    # print(violation)
    line = int(violation["line"])
    # col = int(violation["column"])
    token_id = locate_token(tokens, line + 1, 0)
    if not token_id:
        token_id = len(tokens)
    token_id -= 1

    if not isinstance(tokens[token_id], javalang.tokenizer.Comment):
        return whitespace
    
    whitespace[token_id-1] = whitespace[token_id]
    whitespace[token_id] = (1, 0, "SP")

    return whitespace
