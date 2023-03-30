import argparse
import os
from bs4 import BeautifulSoup #parse xml
import json
import javalang
import checkstyle

from tokenizer.tokenizer import tokenize_file, tokenize_violation
from utils import getViolationType

violationRules = {"NewlineAtEndOfFile"}

tempDir = "temp"

# return a list of fixes
def fixViolations(code: str, violations: list, checkstyleData: BeautifulSoup) -> str:
    fixList = [] 
    codeLines = code.split("\n")
    tokens = None # TODO: tokenize & fix
    
    for violation in violations:
        violationType = getViolationType(violation)
        if violationType not in violationRules:
            continue
        if violationType == "NewlineAtEndOfFile":
            fixList.append({"violation": violationType}) # TODO: modify the last token
    
    # TODO: de-tokenize
    for i in fixList:
        if i["violation"] == "NewlineAtEndOfFile":
            code = code + "\n"

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
        # import random
        # random.shuffle(dataset)
        # dataset =  dataset[:100]
        for data in dataset:
            checkstyleConfigFile = os.path.join(data, "checkstyle.xml")
            codeFile = os.path.join(data, "code.java")
            infoFile = os.path.join(data, "info.json")
            violationFile = os.path.join(data, "violations.json")

            with open(codeFile, "r") as f:
                code = f.read()
            with open(checkstyleConfigFile, "r") as f:
                checkstyleData = f.read()
                checkstyleData = BeautifulSoup(checkstyleData, "xml") # xml -> java
            try:
                with open(violationFile, "r") as f:
                    violations = json.load(f)
            except Exception:
                continue
            with open(infoFile, "r") as f:
                info = json.load(f)
            
            checkstyleJar = info["checkstyle_jar"]
            checkstyleJar = os.path.join("jars", checkstyleJar)
            fixed = fixViolations(code, violations, checkstyleData)
            tempCodeFile = os.path.join(tempDir, "output.java")
            with open(tempCodeFile, "w") as f:
                f.write(fixed)
            newViolations = checkstyle.check(tempCodeFile, checkstyleConfigFile, checkstyleJar)
            remaining = [i for i in newViolations if getViolationType(i) == rule]
            if len(remaining) == 0:
                result[rule]["success"] += 1
            else:
                result[rule]["fail"] += 1
    print(result)

            

