from .utils import locate_token


def fixGenericWhitespace(violation: dict,tokens: list, whitespace: list, **kwargs) -> list:
    line = int(violation["line"])
    col = int(violation["column"])
    # print(violation)
    token_id = locate_token(tokens, line, col)
    if tokens[token_id].value not in ["<", ">"]:
        token_id -= 1
    # print("--------", token_id, tokens[token_id])
    # TODO: find tabs in multi-line comments

    if tokens[token_id].value == ">":
        if whitespace[token_id-1][0] == 0 and whitespace[token_id-1][1] > 0:
            whitespace[token_id-1] = (0, 0, "None")
        elif "is followed by whitespace" in violation["message"]:
            whitespace[token_id] = (0, 0, "None")
        else:
            whitespace[token_id] = (0, 1, "SP")

    elif tokens[token_id].value == "<":
        if "is preceded with whitespace" in violation["message"]:
            whitespace[token_id-1] = (0, 0, "None")
        elif "is not preceded with whitespace" in violation["message"]:
            whitespace[token_id-1] = (0, 1, "SP")
        elif "is followed by whitespace" in violation["message"]:
            whitespace[token_id] = (0, 0, "None")
        else:
            whitespace[token_id] = (0, 1, "SP")


    return whitespace
