from .utils import locate_token, find_rightpar
import javalang

def fixAnnotationLocation(violation: dict, tokens: list, whitespace: list, **kwargs) -> list:
    # print(violation)
    msg = violation["message"]
    line = int(violation["line"])
    
    token_id = locate_token(tokens, line)
    while token_id < len(tokens) and type(tokens[token_id]) != javalang.tokenizer.Annotation:
        token_id += 1
    token_id += 1 
    while token_id < len(tokens)-1 and tokens[token_id+1].value == ".":
        token_id += 2

    if token_id >= len(tokens):
        return whitespace
    
    if token_id < len(tokens) - 1 and tokens[token_id+1].value == "(":
        token_id = find_rightpar(tokens, token_id + 1)
    
    if token_id:
        whitespace[token_id] = (1, 0, "SP")

    return whitespace