from bs4 import BeautifulSoup
from .utils import locate_token, next_nl


def fixWhitespaceAfter(violation: dict, tokens: list, whitespace: list, checkstyleData: BeautifulSoup, **kwargs) -> list:
    # print(violation)
    line = int(violation["line"])
    col = int(violation["column"])
    token_id = locate_token(tokens, line, col)
    token_name = violation["message"].split("'")
    if not token_id or len(token_name) < 2: # TODO: handle error
        return whitespace
    token_name = token_name[1]
    if token_name == "typecast":
        token_name = ")"

    
    if tokens[token_id].value == token_name and whitespace[token_id][:2] == (0,0):
        pass
    elif token_id > 0 and tokens[token_id-1].value == token_name and whitespace[token_id-1][:2] == (0, 0):
        token_id -= 1
    elif token_id > 0 and tokens[token_id+1].value == token_name and whitespace[token_id+1][:2] == (0, 0):
        token_id += 1
    else:
        return whitespace
    
    whitespace[token_id] = (0, 1, whitespace[token_id][2])

    return whitespace
