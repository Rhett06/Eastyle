from bs4 import BeautifulSoup
from .utils import locate_token, next_nl


def fixNoWhitespaceAfter(violation: dict, tokens: list, whitespace: list, checkstyleData: BeautifulSoup, **kwargs) -> list:
    # print(violation)
    line = int(violation["line"])
    col = int(violation["column"])
    token_id = locate_token(tokens, line, col)
    token_name = violation["message"].split("'")
    # print(tokens[token_id].value)
    if not token_id or len(token_name) < 2: # TODO: handle error
        return whitespace
    token_name = token_name[1]
    
    if tokens[token_id].value == token_name and whitespace[token_id][:2] != (0,0):
        pass
    elif token_id > 0 and tokens[token_id-1].value == token_name and whitespace[token_id-1][:2] != (0, 0):
        token_id -= 1
    else:
        return whitespace
    

    if whitespace[token_id][0] > 0:
        indent = whitespace[token_id][1]
        whitespace[token_id] = (0, 0, whitespace[token_id][2])
        nl_id = next_nl(whitespace, token_id)
        if nl_id:
            whitespace[nl_id] = (whitespace[nl_id][0], whitespace[nl_id][1]+indent, whitespace[nl_id][2])
    else:
        whitespace[token_id] = (0, 0, whitespace[token_id][2])

    return whitespace
