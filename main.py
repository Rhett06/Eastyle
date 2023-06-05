import argparse
import os
import sys
from bs4 import BeautifulSoup  # parse xml
import json
import javalang
import checkstyle
import tqdm
from typing import Tuple, Union
import copy

from tokenizer.tokenizer import tokenize_file, tokenize_violation, tokenize_with_white_space, de_tokenize, reformat
from utils import get_violation_type, load_file, save_file

from violationFixes import (
    fixNewlineAtEndOfFile, fixNoLineWrap, fixEmptyForIteratorPad, fixLeftCurly,
    fixOneStatementPerLine, fixCommentsIndentation, fixNoWhitespaceAfter,
    fixNoWhitespaceBefore,fixWhitespaceAfter, fixFileTabCharacter, fixGenericWhitespace,
    fixEmptyLineSeparator, fixIndentation, fixLineLength, fixMethodParamPad,
    fixOperatorWrap, fixParenPad, fixRightCurly, fixSeparatorWrap, 
    fixSingleSpaceSeparator, fixTrailingComment, fixWhitespaceAround,
    fixAnnotationLocation, fixTypecastParenPad
)

violationRules = {"CommentsIndentation", "EmptyForIteratorPad", "EmptyLineSeparator", "FileTabCharacter", "GenericWhitespace", "Indentation", 
            "LeftCurly", "LineLength", "MethodParamPad", "NoLineWrap", "NoWhitespaceAfter", "NoWhitespaceBefore", "OneStatementPerLine",
            "OperatorWrap", "ParenPad", "Regexp", "RegexpMultiline", "RegexpSingleline", "RegexpSinglelineJava", "RightCurly", "SeparatorWrap",
            "SingleSpaceSeparator", "TrailingComment", "WhitespaceAfter", "WhitespaceAround", "NewlineAtEndOfFile", "AnnotationLocation", 
            "AnnotationOnSameLine", "EmptyForInitializerPad", "TypecastParenPad"}
tempDir = "temp"


# return a list of fixes
def fix_violations_step(code: str, violations: list, checkstyleData: BeautifulSoup) -> str:
    codeLines = code.split("\n")
    whitespace, tokens, whitespace_str = tokenize_with_white_space(code)
    violating_whitespace = copy.deepcopy(whitespace)
    # for i in range(30):
    #    print(tokens[i].value, len(tokens[i].value), whitespace[i], f"*{whitespace_str[i]}*")
    for violation in violations:
        # print(violation)
        # print(type(tokens[0]))
        violation_type = get_violation_type(violation)
        args = {"violation": violation, "tokens": tokens, "whitespace": whitespace, "checkstyleData":checkstyleData}
        if violation_type not in violationRules:
            continue
        whitespace = globals()["fix"+violation_type](**args)
    # print(type(violation))
    # print(whitespace)

    # code = de_tokenize(code, whitespace)
    code = reformat(whitespace, violating_whitespace, tokens, whitespace_str)
    # print(whitespace)
    # print(code)
    return code

def fix_violations(code: str, violations: list, checkstyleData: BeautifulSoup, steps: int = 3) -> Tuple[Union[str, None], list]:
    # TODO: expose an interface to users
    try:
        for _ in range(steps):
            fixed = fix_violations_step(code, violations, checkstyleData)
            
            tempCodeFile = os.path.join(tempDir, info["filename"]) # TODO: generate an output path
            with open(tempCodeFile, "w") as f:
                f.write(fixed)
            save_file(fixed, tempCodeFile)
            remaining = checkstyle.check(tempCodeFile, checkstyleConfigFile, checkstyleJar)
            # print(newViolations)
            # remaining = [i for i in newViolations if get_violation_type(i) == rule]
            if len(remaining) == 0 or violations == remaining:
                break
            
            code = fixed
            violations = remaining
        
        return code, remaining
    except Exception:
        return None, []

# def fix_violations2(code: str, violations: list, checkstyleData: BeautifulSoup, steps: int = 3) -> Tuple[Union[str, None], list]:
#     tempCodeFile = os.path.join(tempDir, info["filename"]) # TODO: generate an output path
#     with open(tempCodeFile, "w") as f:
#         f.write(code)
#     remaining = checkstyle.check(tempCodeFile, checkstyleConfigFile, checkstyleJar)
#     return code, remaining

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', help='the dataset directory')
    parser.add_argument('--rule', help='the tested rule')
    args = parser.parse_args()
    dataPath = args.data
    if args.rule is not None:
        violationRules = {args.rule}
    os.makedirs(tempDir, exist_ok=True)

    result = {}
    checkpoint_file = open("./checkpoint.txt", "w")
    for rule in violationRules:
        print(f"running with rule {rule}...")
        result[rule] = {"success": 0, "same": 0, "new": 0, "same+new": 0, "error": 0}
        rulePath = os.path.join(dataPath, rule)
        dataset = os.listdir(rulePath)
        dataset = [os.path.join(rulePath, i) for i in dataset]
        
        # import random
        # random.shuffle(dataset)
        # dataset = dataset[:1]
        # print(dataset)
        # dataset = ["../data-by-rule/FileTabCharacter/1330"] # 201 860 1675 977
        for data in tqdm.tqdm(dataset):
            # print(data)
            checkstyleConfigFile = os.path.join(data, "checkstyle.xml")
            infoFile = os.path.join(data, "info.json")
            violationFile = os.path.join(data, "violations.json")
            
            with open(checkstyleConfigFile, "r") as f:
                checkstyleData = f.read()
                checkstyleData = BeautifulSoup(checkstyleData, "xml")  # xml -> java
            try:
                with open(violationFile, "r") as f:
                    violations = json.load(f)
            except Exception:
                continue
            with open(infoFile, "r") as f:
                info = json.load(f)

            codeFile = os.path.join(data, info["filename"])

            code = load_file(codeFile)
            if code is None:
                print("error on input file: ", data, file=sys.stderr)
                result[rule]["error"] += 1
                continue

            checkstyleJar = info["checkstyle_jar"]
            # print(checkstyleJar)
            checkstyleJar = os.path.join("jars", checkstyleJar)
            init_code = code
            init_violations = violations

            new_code, remaining = fix_violations(code, violations, checkstyleData, 10)

            
            exclude_set = {"JavadocPackage", "PackageDeclaration"}
            remaining = [i for i in remaining if get_violation_type(i) not in exclude_set]
            # print(remaining)
            
            remaining_same = len([i for i in remaining if get_violation_type(i) == rule])
            remaining_new = len([i for i in remaining if get_violation_type(i) != rule])
            if new_code is None or remaining is None:
                print("error on data point: ", data, file=sys.stderr)
                result[rule]["error"] += 1
            elif len(remaining) == 0:
                result[rule]["success"] += 1
            else:
                print(data, [get_violation_type(i) for i in remaining], file=sys.stderr)
                # print(remaining)
                if remaining_same > 0 and remaining_new > 0:
                    result[rule]["same+new"] += 1
                elif remaining_same > 0:
                    result[rule]["same"] += 1
                elif remaining_new > 0:
                    result[rule]["new"] += 1
        
        print(rule, result[rule], file=checkpoint_file)
    print(result)
