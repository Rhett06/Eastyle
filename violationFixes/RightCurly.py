from bs4 import BeautifulSoup
from .utils import locate_token, next_nl


def fixRightCurly(violation: dict, tokens: list, whitespace: list, checkstyleData: BeautifulSoup, **kwargs) -> list:
    print(violation)
    line = int(violation["line"])
    col = int(violation["column"])
    token_id = locate_token(tokens, line, col)

    token_name = "}"
    if not token_id:
        return whitespace
    if tokens[token_id].value != token_name:
        if token_id > 0 and tokens[token_id-1].value == token_name:
            token_id -= 1
        elif token_id < len(tokens)-1 and tokens[token_id+1].value == token_name:
            token_id += 1
        else:
            for i in range(locate_token(tokens, line, 0), len(tokens)):
                if tokens[i].value == token_name:
                    token_id = i
                    break
                if tokens[i].position[0] > line:
                    break

    if tokens[token_id].value != token_name:        
        return whitespace
        
    if whitespace[token_id - 1][0] == 0:
        whitespace[token_id - 1] = (1, 0, "SP")
    if whitespace[token_id][0] == 0:
        whitespace[token_id] = (1, 0, "SP")
    return whitespace
