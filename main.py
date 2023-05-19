import argparse
import os
from bs4 import BeautifulSoup  # parse xml
import json
import javalang
import checkstyle
import tqdm

from tokenizer.tokenizer import tokenize_file, tokenize_violation, tokenize_with_white_space, de_tokenize
from utils import get_violation_type

from violationFixes import (
    fixNewlineAtEndOfFile, fixNoLineWrap, fixEmptyForIteratorPad, fixLeftCurly,
    fixOneStatementPerLine, fixCommentsIndentation, fixNoWhitespaceAfter,
    fixNoWhitespaceBefore,fixWhitespaceAfter, fixFileTabCharacter, fixGenericWhitespace,
    fixEmptyLineSeparator, fixIndentation, fixLineLength, fixMethodParamPad,
    fixOperatorWrap, fixParenPad, fixRightCurly, fixSeparatorWrap, 
    fixSingleSpaceSeparator, fixTrailingComment, fixWhitespaceAround,
    fixAnnotationLocation, fixTypecastParenPad
)

violationRules = {"TypecastParenPad"}

tempDir = "temp"


# return a list of fixes
def fix_violations(code: str, violations: list, checkstyleData: BeautifulSoup) -> str:
    codeLines = code.split("\n")
    whitespace, tokens, whitespace_str = tokenize_with_white_space(code)

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

    code = de_tokenize(code, whitespace)
    # print(whitespace)
    # print(code)
    return code


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
    for rule in violationRules:
        result[rule] = {"success": 0, "fail": 0}
        rulePath = os.path.join(dataPath, rule)
        dataset = os.listdir(rulePath)
        dataset = [os.path.join(rulePath, i) for i in dataset]
        import random

        random.shuffle(dataset)
        dataset = dataset[:100]
        # dataset = ["../data-by-rule/TypecastParenPad/1354"] #  27098 73797

        #dataset = ["../data-by-rule/EmptyForIteratorPad/2073"]
        #dataset = ["../data-by-rule/OneStatementPerLine/25"]  # 33 184 63
        for data in tqdm.tqdm(dataset):
            # print(data)
            checkstyleConfigFile = os.path.join(data, "checkstyle.xml")
            codeFile = os.path.join(data, "code.java")
            infoFile = os.path.join(data, "info.json")
            violationFile = os.path.join(data, "violations.json")

            with open(codeFile, "r") as f:
                code = f.read()
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

            checkstyleJar = info["checkstyle_jar"]
            # print(checkstyleJar)
            checkstyleJar = os.path.join("jars", checkstyleJar)
            init_code = code
            init_violations = violations
            for _ in range(3):
                fixed = fix_violations(code, violations, checkstyleData)
                tempCodeFile = os.path.join(tempDir, "output.java")
                with open(tempCodeFile, "w") as f:
                    f.write(fixed)
                newViolations = checkstyle.check(tempCodeFile, checkstyleConfigFile, checkstyleJar)
                # print(newViolations)
                remaining = [i for i in newViolations if get_violation_type(i) == rule]
                
                if len(remaining) == 0 or violations == remaining:
                    break
                code = fixed
                violations = remaining
            # print(remaining)

            if len(remaining) == 0:
                result[rule]["success"] += 1
            else:
                result[rule]["fail"] += 1
                print(data)
                # exit()
    print(result)
