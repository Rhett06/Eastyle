from .utils import locate_token, next_nl

def fixMethodParamPad(violation: dict,tokens: list, whitespace: list, **kwargs) -> list:
    line = int(violation["line"])
    col = int(violation["column"])
    # print(violation)

    token_id = locate_token(tokens, line, col)
    if not token_id or tokens[token_id].value != "(":
        return whitespace
    # print(tokens[token_id])
    if whitespace[token_id-1][0] != 0:
        # indent = whitespace[token_id-1][1]
        # nl = next_nl(whitespace, token_id)
        t = list(whitespace[token_id-1])
        if whitespace[token_id][1] > 0:
            t[1] += whitespace[token_id][1]
        whitespace[token_id] = tuple(t)

        whitespace[token_id-1] = (0, 0, "None")
        # whitespace[nl] = (whitespace[nl][0], whitespace[nl][1] + indent, whitespace[nl][2])
    elif whitespace[token_id-1][1] != 0:
        whitespace[token_id-1] = (0, 0, "None")
    else:
        whitespace[token_id-1] = (0, 1, "SP")


    return whitespace