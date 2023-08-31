from bs4 import BeautifulSoup

from .utils import locate_token, next_nl

def fixLineLength(violation: dict,tokens: list, whitespace: list, checkstyleData: BeautifulSoup, **kwargs) -> list:
    line = int(violation["line"])
    # col = int(violation["column"])
    # print(violation)
    lengthConfig = checkstyleData.find(name="module", attrs={"name": "LineLength"})
    maxLength = lengthConfig.find(name="property", attrs={"name": "max"})

    maxLength = 80 if not maxLength else int(maxLength.attrs["value"])


    token_id = locate_token(tokens, line, 0)
    nl = next_nl(whitespace, token_id)
    indent = 0
    for i in range(0, token_id-1):
        if whitespace[i][0] > 0:
            indent += whitespace[i][1]
    
    last_id = token_id
    for i in range(token_id, nl+1):
        if len(tokens[i].value) > maxLength - indent:
            return whitespace
        r, c = tokens[i].position
        if r == line and c < maxLength - 4: # TODO: check token type
            last_id = i-1
    
    relative_indent = 4 # TODO: get relative indent
    whitespace[last_id] = (1, relative_indent, "SP")
    whitespace[nl] = (whitespace[nl][0], whitespace[nl][1] - relative_indent, whitespace[nl][2])


    return whitespace