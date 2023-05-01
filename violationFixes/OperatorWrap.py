from .utils import locate_token, next_nl, get_indent_type


def fixOperatorWrap(violation: dict,tokens: list, whitespace: list, **kwargs) -> list:
    line = int(violation["line"])
    col = int(violation["column"])
    # print(violation)

    token_id = locate_token(tokens, line, col)
    token_name = violation["message"].split("'")
    if not token_id or len(token_name) < 2: # TODO: handle error
        return whitespace
    token_name = token_name[1]

    if not token_id:
        return whitespace
    if tokens[token_id].value != token_name:
        if tokens[token_id-1].value == token_name:
            token_id -= 1
        elif tokens[token_id+1].value == token_name:
            token_id += 1
        else:
            return whitespace
    # print(tokens[token_id])

    nl = next_nl(whitespace, token_id)
    relative_indent = 4 # TODO: get relative indent
    indent_type = get_indent_type(whitespace)
    whitespace[token_id-1] = (1, relative_indent, indent_type)
    whitespace[nl] = (whitespace[nl][0], whitespace[nl][1] - relative_indent, whitespace[nl][2])


    return whitespace
