from bs4 import BeautifulSoup
from .utils import locate_token, next_nl


def fixTypecastParenPad(violation: dict, tokens: list, whitespace: list, checkstyleData: BeautifulSoup, **kwargs) -> list:
    # print(violation)
    line = int(violation["line"])
    col = int(violation["column"])
    token_id = locate_token(tokens, line, col)
    # print(tokens[token_id])
    token_name = violation["message"].split("'")
    if not token_id or len(token_name) < 2: # TODO: handle error
        return whitespace
    token_name = token_name[1]
    # if token_name == "typecast":
    #     token_name = ")"

    if tokens[token_id].value == token_name:
        pass
    elif token_id > 0 and tokens[token_id-1].value == token_name:
        token_id -= 1
    elif token_id > 0 and tokens[token_id+1].value == token_name:
        token_id += 1
    else:
        return whitespace
    # print(token_name,tokens[token_id].value, tokens[token_id])

    if "is not followed by whitespace." in violation["message"]:
        whitespace[token_id] = (0, 1, "SP")
    elif "is not preceded with whitespace." in violation["message"]:
        whitespace[token_id-1] = (0, 1, "SP")
    
    # if whitespace[token_id][1] == 0:
    #     whitespace[token_id] = (0, 1, "SP")
    # elif whitespace[token_id-1][1] == 0:
    #     whitespace[token_id-1] = (0, 1, "SP")

    return whitespace
