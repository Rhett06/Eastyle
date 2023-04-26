
from typing import Tuple
from javalang import tokenizer as javalang_tokenizer

if __name__ == "__main__":
    from token_utils import get_line_indent,get_token_value,get_space_value, whitespace_token_to_tuple
else:
    from .token_utils import get_line_indent,get_token_value,get_space_value, whitespace_token_to_tuple

def getViolationType(violation: dict) -> str:
    return violation["source"].split(".")[-1][:-5]


def tokenize_with_white_space(code: str) -> Tuple[list, list, list]:
    """
    Tokenize the java source code
    :param file_content: the java source code
    :return: (whitespace, tokens)
    """
    indentation_last_line = 1
    file_content_lines = code.split('\n')
    javalang_tokens = javalang_tokenizer.tokenize(code, parse_comments=True)
    tokens = []
    count = 0
    try:
        for t in javalang_tokens:
            count += 1
            if count > 1000000:
                break
            tokens.append(t)
            pass
    except Exception as err:
        print('Something wrong happened while tokenizing the following content: ' + code)
        return None, None
    whitespace = list()
    whitespaceStr = []

    for index in range(0, len(tokens)-1):
        tokens_position = tokens[index].position
        next_token_position = tokens[index+1].position
        if tokens_position[0] == 1:
            tokens_position = (1, tokens_position[1]+1)
        if next_token_position[0] == 1:
            next_token_position = (1, next_token_position[1]+1)

        token_lines = tokens[index].value.split("\n")
        end_of_token_line = tokens_position[0] + len(token_lines) - 1
        end_of_token_col = (tokens_position[1] + len(token_lines[0]))  if (len(token_lines)==1) else (len(token_lines[-1]) + 1)
        end_of_token = (end_of_token_line, end_of_token_col)


        if end_of_token == next_token_position:
            whitespace.append((0,0,'None'))
            whitespaceStr.append('')
            # whitespaceStr.append((tokens_position, end_of_token))
        else:
            if end_of_token[0] == next_token_position[0]:
                # same line
                if file_content_lines[tokens_position[0]-1] != '':
                    if len(file_content_lines[tokens_position[0]-1]) > end_of_token[1] and file_content_lines[tokens_position[0]-1][end_of_token[1]] == '\t':
                        space_type = 'TB'
                    else:
                        space_type = 'SP'
                else:
                    space_type = 'None'
                whitespace.append(( 0, next_token_position[1] - end_of_token[1], space_type))
                whitespaceStr.append(file_content_lines[tokens_position[0]-1][end_of_token[1]-1:next_token_position[1]-1])

            else:
                # new line
                new_line = file_content_lines[next_token_position[0]-1]
                if new_line != '':
                    if new_line[get_line_indent(new_line) - 1] == '\t':
                        space_type = 'TB'
                    else:
                        space_type = 'SP'
                else:
                    space_type = 'None'
                if True: # relative
                    spaces = next_token_position[1] - indentation_last_line
                    whitespace.append((next_token_position[0] - end_of_token[0], spaces, space_type))
                    temp = file_content_lines[end_of_token[0]-1][end_of_token[1]-1:] + "\n"
                    for i in range(end_of_token[0], next_token_position[0]-1):
                        temp += file_content_lines[i] + "\n"
                    temp += file_content_lines[next_token_position[0]-1][:next_token_position[1]-1]
                    whitespaceStr.append(temp)
                    indentation_last_line = next_token_position[1]
                # else:
                #     whitespace.append((next_token_position[0] - end_of_token[0] - tokens[index].value.count('\n'), next_token_position[1] - 1, space_type))
    
    count_line_break = 0
    temp = ""
    for index in range(len(code)-1, 0, -1):
        if code[index] == '\n':
            count_line_break += 1
        elif code[index] != ' ' and code[index] != '\t':
            break
        temp += code[index]

    whitespace.append((count_line_break, 0, 'None'))
    whitespaceStr.append(''.join(temp[::-1]))

    return whitespace, tokens, whitespaceStr




def tokenize_violation(code: str, violation: dict) -> Tuple[list, dict]:
    spaces, tokens, _ = tokenize_with_white_space(code)
    violation["type"] = getViolationType(violation)

    info = {}

    n_lines = 6

    token_started = False
    token_line_start = -1
    token_line_end = -1
    count = 0

    tokens_violating = []

    context_beginning_token = len(tokens)
    context_end_token = 0

    violation_beginning_token = 0
    violation_end_token = 0

    for token, space in zip(tokens, spaces):
        if token.position[0] >= int(violation['line']) - n_lines and token.position[0] <= int(violation['line']) + n_lines:
            context_beginning_token = min(count, context_beginning_token)
            context_end_token = max(count, context_end_token)
        if not token_started and int(violation['line']) == token.position[0]:
            token_started = True
            token_line_start = count
        if token_started and int(violation['line']) < token.position[0]:
            token_started = False
            token_line_end = count
        count += 1
    context_beginning_token = max(0, context_beginning_token - 1)
    context_end_token = min(len(tokens), context_end_token + 1)
    if token_line_end == -1:
        token_line_end = token_line_start

    # print(violation)

    violating_token_index = -1
    if 'column' in violation:
        around = 1
        column = int(violation['column'])

        if column <= tokens[token_line_start].position[1]:
            violating_token_index = token_line_start
        elif column >= tokens[token_line_end - 1].position[1]:
            violating_token_index = token_line_end - 1
        else:
            index = token_line_start
            for token in tokens[token_line_start:token_line_end]:
                if token.position[1] <= column:
                    violating_token_index = index
                index += 1

        violation_beginning_token = max(0, violating_token_index - around)
        violation_end_token = min(len(tokens), violating_token_index + around)
    else:
        around = 1
        around_after = 1
        if token_line_start != -1:
            violation_beginning_token = max(context_beginning_token, token_line_start - around)
            violation_end_token = min(context_end_token, token_line_end + around_after)
        else:
            for token, index in zip(tokens,range(len(tokens))):
                if token.position[0] < int(violation['line']):
                    violating_token_index = index
            violation_beginning_token = max(0, violating_token_index - around)
            violation_end_token = min(len(tokens), violating_token_index + around_after)
    

    tokens_violating_in_tag = []
    for token, space in zip(tokens[violation_beginning_token:violation_end_token], spaces[violation_beginning_token:violation_end_token]):
        tokens_violating_in_tag.append(get_token_value(token))
        tokens_violating_in_tag.append(get_space_value(space))


    for token, space in zip(tokens[context_beginning_token:violation_beginning_token], spaces[context_beginning_token:violation_beginning_token]):
        tokens_violating.append(get_token_value(token))
        tokens_violating.append(get_space_value(space))
    tokens_violating.append(f'<{violation["type"]}>')
    for token, space in zip(tokens[violation_beginning_token:violation_end_token], spaces[violation_beginning_token:violation_end_token]):
        tokens_violating.append(get_token_value(token))
        tokens_violating.append(get_space_value(space))
    tokens_violating.append(f'</{violation["type"]}>')
    for token, space in zip(tokens[violation_end_token:context_end_token], spaces[violation_end_token:context_end_token]):
        tokens_violating.append(get_token_value(token))
        tokens_violating.append(get_space_value(space))


    info['violation_beginning_token'] = violation_beginning_token
    info['violation_end_token'] = violation_end_token
    info['context_beginning_token'] = context_beginning_token
    info['context_end_token'] = context_end_token
    info['violation'] = violation
    info['tokens_violating_in_tag'] = tokens_violating_in_tag

    return tokens_violating, info




# TODO: tokenize
def tokenize_file(code: str) -> list:
    spaces, tokens, _ = tokenize_with_white_space(code)

    tokens_violating = []


    for token, space in zip(tokens, spaces):
        tokens_violating.append(get_token_value(token))
        tokens_violating.append(get_space_value(space))


    return tokens_violating


def reformat(whitespace: list, violating_whitespace: list, tokens: list, whitespaceStr: list, relative=True):
    """
    Given the sequence of whitespaces and javat token reformat the java source code
    :return: the java source code
    """
    result = ''
    indent = 0
    for ws, ews, t, wss in zip(whitespace, violating_whitespace, tokens, whitespaceStr):
        if ws[0] > 0:
            indent += ws[1]
        # print(ws, ews, indent)
        if ws == ews:
            result += str(t.value) + wss
        else: 
            if ws[2] == 'TB':
                space = "\t"
            else:
                space = " "
            if ws[0] > 0:
                result += str(t.value) + "\n" * ws[0] + space * indent 
            else:
                result += str(t.value) + space * ws[1]
    return result

def de_tokenize(code: str, fixedWihtespaces: list) -> str:
    violatingWihtespaces, tokens, wihtespaceStr = tokenize_with_white_space(code)
    # for a,b,c in zip(violatingWihtespaces,tokens, wihtespaceStr):
    #     print(a, b, "*"+c+"*")
    fixedSourceCode = reformat(fixedWihtespaces, violatingWihtespaces, tokens, wihtespaceStr)
    # print(fixedTokens)
    return fixedSourceCode


if __name__ == "__main__":
    import os
    import json
    with open(os.path.join(os.path.dirname(__file__), "./test.json")) as f:
        testDataset = json.load(f)
    data = testDataset[0]
    code = data["code"]
    violation = data["violation"]
    tokens = data["tokens"]
    tokens[-1] = "2_NL"
    info = data["info"]
    fixedWihtespaces = tokens[1::2]
    fixedWihtespaces = [ whitespace_token_to_tuple(token) for token in fixedWihtespaces ]
    newCode = de_tokenize(code, fixedWihtespaces)
    # print(newCode)
    with open("new.java","w") as f:
        f.write(newCode)
    with open("old.java","w") as f:
        f.write(code)
