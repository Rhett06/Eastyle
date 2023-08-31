from .utils import locate_token, get_indent_type
import javalang

def fixEmptyLineSeparator(violation: dict,tokens: list, whitespace: list, **kwargs) -> list:
    line = int(violation["line"])
    # col = int(violation["column"])
    # print(violation)

    token_id = locate_token(tokens, line, 0)
    indent_type = get_indent_type(whitespace)
    # print(token_id, tokens[token_id])
    if "';' should be separated from previous statement." in violation["message"]:
        while tokens[token_id].value != ";":
            token_id += 1
        whitespace[token_id-1] = (whitespace[token_id-1][0] + 1, 0, indent_type)

    elif "should be separated from previous statement" in violation["message"] or \
            "should be separated from previous line" in violation["message"]:
        prev_id = token_id - 1
        while isinstance(tokens[prev_id], javalang.tokenizer.Comment):
            prev_id -= 1
        if prev_id < 0:
            prev_id = token_id - 1
        whitespace[prev_id] = (whitespace[prev_id][0] + 1, whitespace[prev_id][1], whitespace[prev_id][2])

    elif "has more than 1 empty lines before" in violation["message"]:
        prev_id = token_id - 1
        while whitespace[prev_id][0] < 2:
            prev_id -= 1
        if prev_id >= 0:
            whitespace[prev_id] = (2, whitespace[prev_id][1], whitespace[prev_id][2])
    else:
        pass


    return whitespace
