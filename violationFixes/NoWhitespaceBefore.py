import javalang.tokenizer
from bs4 import BeautifulSoup
from .utils import locate_token, next_nl


def fixNoWhitespaceBefore(violation: dict, tokens: list, whitespace: list, checkstyleData: BeautifulSoup, **kwargs) -> list:
    # print(violation)
    line = int(violation["line"])
    col = int(violation["column"])
    token_id = locate_token(tokens, line, col)
    token_name = violation["message"].split("'")

    if not token_id or len(token_name) < 2: # TODO: handle error
        return whitespace
    token_name = token_name[1]
    
    if tokens[token_id].value == token_name and whitespace[token_id-1][:2] != (0,0):
        pass
    elif token_id > 0 and tokens[token_id-1].value == token_name and whitespace[token_id-2][:2] != (0,0):
        token_id -= 1
    elif len(tokens) > token_id+1 and tokens[token_id+1].value == token_name and whitespace[token_id][:2] != (0,0):
        token_id += 1
    else:
        return whitespace
    
    # print(tokens[token_id].value, token_name)
    
    whitespace_id = token_id - 1
    if whitespace[whitespace_id][0] > 0:
        if type(tokens[whitespace_id]) == javalang.tokenizer.Comment  and tokens[whitespace_id].value.startswith("//"):
            tokens[whitespace_id], tokens[whitespace_id+1] = tokens[whitespace_id+1], tokens[whitespace_id]
        t = list(whitespace[whitespace_id])
        if whitespace[whitespace_id+1][1] > 0:
            t[1] += whitespace[whitespace_id+1][1]
        whitespace[whitespace_id+1] = tuple(t)
        whitespace[whitespace_id] = (0, 0, "None")
    else:
        whitespace[whitespace_id] = (0, 0, "None")

    return whitespace
