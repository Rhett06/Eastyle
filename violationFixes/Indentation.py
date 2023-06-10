from bs4 import BeautifulSoup
from itertools import takewhile
from .utils import locate_token, get_indent_type

def fixIndentation(violation: dict,tokens: list, whitespace: list, checkstyleData: BeautifulSoup, **kwargs) -> list:
    line = int(violation["line"])
    # col = int(violation["column"])
    print(violation)
    indentConfig = checkstyleData.find(name="module", attrs={"name": "Indentation"})

    token_id = locate_token(tokens, line, 0) - 1
    indent_type = get_indent_type(whitespace)
    if token_id < 0 or whitespace[token_id][2] != indent_type: 
        return whitespace
    
    
    msg = violation["message"]
    # print(msg)
    indent_prefix = "has incorrect indentation level "
    new_indent_prefix = ["expected level should be one of the following: ", "expected level should be "]
    # expected level should be one of the following: 6, 8, 10.
    pos_indent = msg.find(indent_prefix) + len(indent_prefix)
    pos_new_indent = None
    for s in new_indent_prefix:
        pos_new_indent = msg.find(s)
        if pos_new_indent >= 0:
            pos_new_indent += len(s)
            break
    
    # print(msg[pos_indent:], msg[pos_new_indent:])
    def next_int(s: str) -> int:
        return int(''.join(takewhile(str.isdigit, s)))
    indent = next_int(msg[pos_indent:])
    new_indent = next_int(msg[pos_new_indent:])
    diff = new_indent - indent
    
    if indent_type == "SP":
        ws = whitespace[token_id]
        new_ws = (ws[0], ws[1] + diff, ws[2])
        whitespace[token_id] = new_ws
        
    else: # TODO: handle tab indent
        pass 


    return whitespace