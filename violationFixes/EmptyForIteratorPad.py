
def fixEmptyForIteratorPad(violation: dict,tokens: list, whitespace: list, **kwargs) -> list:
    line = int(violation["line"])
    col = int(violation["column"])
    # print(violation)
    token_id = None
    for i in range(len(tokens)):
        if tokens[i].position[0] == line and tokens[i].position[1] >= col:
            token_id = i
            break
    # print(tokens[1594])
    if token_id is not None:
        whitespace[token_id-1] = (0, 0, "None")
    else:
        pass
        # TODO: tab error from checkstyle to javalang
    return whitespace
