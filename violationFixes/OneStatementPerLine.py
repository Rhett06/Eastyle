from .utils import locate_token, get_indent_type


def fixOneStatementPerLine(violation: dict, tokens: list, whitespace: list, **kwargs) -> list:
    line = int(violation["line"])
    # col = int(violation["column"])
    token_id = locate_token(tokens, line, 0)
    indent_type = get_indent_type(whitespace)
    if not indent_type:
        indent_type = "SP"
    for i in range(token_id, len(tokens)):
        if tokens[i].position[0] > line:
            break
        if tokens[i].value == ";" and whitespace[i][0] == 0:
            whitespace[i] = (1, 0, indent_type)

    return whitespace
