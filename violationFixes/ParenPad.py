from bs4 import BeautifulSoup
from .utils import locate_token, next_nl


def fixParenPad(violation: dict, tokens: list, whitespace: list, checkstyleData: BeautifulSoup, **kwargs) -> list:
    # print(violation)
    # params = checkstyleData.find(name="module", attrs={"name": "LeftCurly"})
    # "'(' is followed by whitespace."
    line = int(violation["line"])
    col = int(violation["column"])
    token_id = locate_token(tokens, line, col)
    token_name = violation["message"].split("'")
    if not token_id or len(token_name) < 2: # TODO: handle error
        return whitespace
    token_name = token_name[1]

    if not token_id:
        return whitespace
    if tokens[token_id].value != token_name:
        if token_id > 0 and tokens[token_id-1].value == token_name:
            token_id -= 1
        elif token_id < len(tokens)-1 and tokens[token_id+1].value == token_name:
            token_id += 1
        else:
            for i in range(locate_token(tokens, line, 0), len(tokens)):
                temp = (token_name == "(" and whitespace[i][1] != 0) or (token_name == ")" and whitespace[i-1][1] != 0)
                if tokens[i].value == token_name and temp:
                    token_id = i
                    break
                if tokens[i].position[0] > line:
                    break

    if tokens[token_id].value != token_name:        
        return whitespace
        
    if token_name == "(":
        whitespace[token_id] = (0, 0, "None")
    else:
        whitespace[token_id-1] = (0, 0, "None")
    return whitespace
