from bs4 import BeautifulSoup
from .utils import locate_token, next_nl


def fixLeftCurly(violation: dict, tokens: list, whitespace: list, checkstyleData: BeautifulSoup, **kwargs) -> list:
    # print(violation)
    params = checkstyleData.find(name="module", attrs={"name": "LeftCurly"})

    line = int(violation["line"])
    col = int(violation["column"])
    token_id = locate_token(tokens, line, col)
    if not token_id or tokens[token_id].value != "{":
        for i in range(locate_token(tokens, line, 0), len(tokens)):
            if tokens[i].value == "{":
                token_id = i
                break
            if tokens[i].position[0] > line:
                break
    if not token_id or tokens[token_id].value != "{":  # TODO: handle tab error
        pass
    # print(tokens[token_id].value)
    eol = True  # TODO: deal with nl



    if eol:
        if whitespace[token_id-1][0] > 0:
            indent = whitespace[token_id - 1][0]
            whitespace[token_id - 1] = (0, 1, "SP")
            nl_id = next_nl(whitespace, token_id)
            if nl_id:
                whitespace[nl_id] = (whitespace[nl_id][0], whitespace[nl_id][1]+indent, whitespace[nl_id][2])
    else:  # TODO: solve nl
        pass

    if whitespace[token_id][0] == 0:
        indent_type = whitespace[next_nl(whitespace)][2]
        whitespace[token_id] = (1, 0, indent_type) # indent in the next iteration

    return whitespace
