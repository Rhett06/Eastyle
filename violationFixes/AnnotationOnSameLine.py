from .utils import locate_token, next_nl
import javalang


def fixAnnotationOnSameLine(violation: dict, tokens: list, whitespace: list, **kwargs) -> list:
    # print(violation)
    line = int(violation["line"])

    token_id = locate_token(tokens, line)
    token_id = next_nl(whitespace, token_id)
    next_id = next_nl(whitespace, token_id)

    if next_id:
        ws = list(whitespace[next_id])
        ws[1] += whitespace[token_id][1]
        whitespace[next_id] = tuple(ws)

    whitespace[token_id] = (0, 1, "SP")

    return whitespace
