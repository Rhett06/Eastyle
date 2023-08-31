from typing import Union

def find_rightpar(tokens: list, token_id: int) -> Union[int, None]:
    match_dict = {"{": "}", "(": ")", "[": "]"}
    token_str = tokens[token_id].value
    if token_str not in match_dict:
        return None
    
    rightpar_id = token_id + 1
    while rightpar_id < len(tokens):
        if tokens[rightpar_id].value == match_dict[token_str]:
            return rightpar_id
        if tokens[rightpar_id].value == token_str:
            rightpar_id = find_rightpar(tokens, rightpar_id)

        rightpar_id += 1
        
    return None

def locate_token(tokens: list, line: int, col: int = 0, lowerbound: bool = True) -> Union[int, None]:
    # TODO: binary search
    if line == 1: # fix javalang -1 error in the first line
        col -= 1 
    if lowerbound:
        for i in range(len(tokens)):
            if tokens[i].position[0] > line or (tokens[i].position[0] == line and tokens[i].position[1] >= col):
                return i
    else:  # TODO: exact location
        pass

    return None


def next_nl(whitespace: list, start: int = 0) -> Union[int, None]:
    for i in range(start, len(whitespace)):
        if whitespace[i][0] > 0:
            return i
    return None


def get_indent_type(whitespace: list) -> Union[str, None]:
    for i in whitespace:
        if i[0] > 0 and i[1] > 0:
            return i[2]
    return None
