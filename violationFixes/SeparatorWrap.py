from bs4 import BeautifulSoup
from .utils import locate_token, next_nl


def fixSeparatorWrap(violation: dict, tokens: list, whitespace: list, checkstyleData: BeautifulSoup, **kwargs) -> list:
    # print(violation)
    line = int(violation["line"])
    col = int(violation["column"])

    token_id = locate_token(tokens, line, col)
    token_name = violation["message"].split("'")
    if not token_id or len(token_name) < 2: # TODO: handle error
        return whitespace
    token_name = token_name[1]

    if not token_id:
        return whitespace
    if tokens[token_id].value != token_name:
        if token_id > 0 and tokens[token_id-1].value == token_name:
            token_id -= 1
        elif token_id < len(tokens)-1 and tokens[token_id+1].value == token_name:
            token_id += 1
        else:
            for i in range(locate_token(tokens, line, 0), len(tokens)):
                if tokens[i].value == token_name:
                    token_id = i
                    break
                if tokens[i].position[0] > line:
                    break

    if tokens[token_id].value != token_name:        
        return whitespace
    

    separatorConfig = checkstyleData.findAll(name="module", attrs={"name": "SeparatorWrap"})
    checkstyleNameMap = {".":"DOT",",":"COMMA",";":"SEMI", "...":"ELLIPSIS", "@":"AT", "(":"LPAREN",
                        ")":"RPAREN", "[":"ARRAY_DECLARATOR", "]":"RBRACK", "::":"METHOD_REF"}
    xml_token_name = checkstyleNameMap[token_name]
    default_names = "DOT, COMMA"
    option = None
    

    for i in separatorConfig:
        rule_tokens = i.find(name="property", attrs={"name": "tokens"})
        if ((rule_tokens is None) and (xml_token_name in default_names)) or xml_token_name in rule_tokens.attrs["value"]:
            option = i.find(name="property", attrs={"name": "option"})
            option = ("EOL" if not option else option.attrs["value"]).upper()
            # break
            # TODO: contradictory config files

    # print(token_name, option, tokens[token_id])

    if option == "EOL":
        if whitespace[token_id][0] > 0:
            whitespace[token_id] = (whitespace[token_id-1][0] + whitespace[token_id][0], 
                                    whitespace[token_id-1][1] + whitespace[token_id][1], 
                                    whitespace[token_id-1][2])
        elif whitespace[token_id-1][0] > 0:
            whitespace[token_id] = whitespace[token_id - 1]
        else:
            whitespace[token_id] = (1, 0, "SP")

        whitespace[token_id - 1] = (0, 0, "None")


    elif option == "NL":
        if whitespace[token_id - 1][0] > 0:
            whitespace[token_id - 1] = (whitespace[token_id-1][0] + whitespace[token_id][0], 
                                    whitespace[token_id-1][1] + whitespace[token_id][1], 
                                    whitespace[token_id-1][2])
        elif whitespace[token_id][0] > 0:
            whitespace[token_id - 1] = whitespace[token_id]
        else:
            whitespace[token_id - 1] = (1, 0, "SP")
        
        whitespace[token_id] = (0, 1, "SP")
        

    return whitespace
