from bs4 import BeautifulSoup
from .utils import locate_token, next_nl


def fixSingleSpaceSeparator(violation: dict, tokens: list, whitespace: list, checkstyleData: BeautifulSoup, **kwargs) -> list:
    # print(violation)
    line = int(violation["line"])
    col = int(violation["column"])
    token_id = locate_token(tokens, line, col)
    # TODO: fix tab chars
    if not token_id or whitespace[token_id-1][1] <= 1:
        for i in range(locate_token(tokens, line, 0), len(tokens)):
            if whitespace[i+1][0] > 0:
                break
            if whitespace[i][1] >= 2:
                token_id = i + 1
                break

    if not token_id or whitespace[token_id-1][1] <= 1:
        return whitespace
    
    whitespace[token_id-1] = (0, 1, "SP")
    return whitespace
