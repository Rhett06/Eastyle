

def fixNoLineWrap(violation: dict,tokens: list, whitespace: list, **kwargs) -> list:
    line = int(violation["line"])+1
    #line_str= "line "+ str(line)
    #print(line_str)

    for i in range(len(tokens)):
        if tokens[i].position[0] >= line:
            token_id = i
            break
    indent = whitespace[token_id-1][1]
    whitespace[token_id-1] = (0,0,"None")
    for i in range(token_id, len(tokens)):
        if whitespace[i][0] > 0:
            whitespace[i] = (whitespace[i][0], whitespace[i][1]+indent, whitespace[i][2])
            break


    # for token in tokens:
    #     if token.find(line_str)!= -1
    #         id=tokens.index(token)
    #         break
    #print(token_id)

    return whitespace