from .utils import locate_token
import javalang

def fixFileTabCharacter(violation: dict,tokens: list, whitespace: list, **kwargs) -> list:
    line = int(violation["line"])
    col = int(violation["column"])
    # print(violation)
    token_id = locate_token(tokens, line, col-1)


    whitespace_id = token_id - 1
    # print(tokens[token_id], whitespace[whitespace_id])

    # TODO: find tabs in multi-line comments

    if whitespace_id < 0 or whitespace[whitespace_id][2] != "TB": # not found
        return whitespace
    
    for i in range(whitespace_id, len(whitespace)):
        if whitespace[i][2] != "TB":
            continue
        if whitespace[i][0] == 0:
            whitespace[i] = (0, 1, "SP")
        else:
            whitespace[i] = (whitespace[i][0], whitespace[i][1] * 4, "SP")

    for i in range(whitespace_id, len(tokens)):
        if type(tokens[i]) == javalang.tokenizer.Comment and "\t" in tokens[i].value:
            new_comment = tokens[i].value.replace("\t", "    ")
            tokens[i].value = new_comment

    return whitespace
