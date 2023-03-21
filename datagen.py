import os
import json
import shutil

dataDir = "../data"
outputDir = "../data-by-rule"
if not os.path.exists(outputDir):
    os.mkdir(outputDir)

violationRules = ["CommentsIndentation", "EmptyForIteratorPad", "EmptyLineSeparator", "FileTabCharacter", "GenericWhitespace", "Indentation", 
            "LeftCurly", "LineLength", "MethodParamPad", "NoLineWrap", "NoWhitespaceAfter", "NoWhitespaceBefore", "OneStatementPerLine",
            "OperatorWrap", "ParenPad", "Regexp", "RegexpMultiline", "RegexpSingleline", "RegexpSinglelineJava", "RightCurly", "SeparatorWrap",
            "SingleSpaceSeparator", "TrailingComment", "WhitespaceAfter", "WhitespaceAround", "NewlineAtEndOfFile"]
violationCountDict = {}
for i in violationRules:
    violationCountDict[i] = 0
    violationDir = os.path.join(outputDir, i)
    os.mkdir(violationDir)



projs = os.listdir(dataDir)
for proj in projs:
    projDir = os.path.join(dataDir, proj)

    checkstyleFile = os.path.join(projDir, "checkstyle.xml")
    infoFile = os.path.join(projDir, "info.json")
    if not os.path.exists(checkstyleFile) or not os.path.exists(infoFile):
        continue

# from bs4 import BeautifulSoup
#     # with open(checkstyleFile, "r") as f:
#     #     checkstyleData = f.read()
#     # bs_data = BeautifulSoup(checkstyleData, "xml")
#     # # print(bs_data)
#     # for i in violations:
#     #     print(i, bs_data.find("module", {"name": i}))

    with open(infoFile, "r") as f:
        info = json.load(f)
    


    for commit in os.listdir(projDir):
        commitPath = os.path.join(projDir, commit)
        if not os.path.isdir(commitPath): continue
        violationList = os.listdir(commitPath)
        for _id in violationList:
            id = os.path.join(commitPath, _id)
            violationFile = os.path.join(id, "violations.json")
            javaFile = [i for i in os.listdir(id) if i.endswith("java")][0]
            javaFile = os.path.join(id, javaFile)
            violationSet = set()
            try:
                with open(violationFile, "r") as f:
                    violations = json.load(f)
            except Exception:
                pass

            for violation in violations:
                rule = violation["source"].split(".")[-1][:-5]
                if rule in violationCountDict and rule not in violationSet:
                    violationSet.add(rule)
                    violationID = violationCountDict[rule]
                    violationCountDict[rule] += 1
                    ruleDir = os.path.join(outputDir, rule, str(violationID))
                    os.mkdir(ruleDir)
                    shutil.copy(javaFile, os.path.join(ruleDir, "code.java"))
                    shutil.copy(violationFile, os.path.join(ruleDir, "violations.json"))
                    shutil.copy(checkstyleFile, os.path.join(ruleDir, "checkstyle.xml"))
                    info = {"checkstyle_jar": info["checkstyle_jar"], "repo": proj, "commit": commit, "fileID": _id}
                    with open(os.path.join(ruleDir, "info.json"), "w") as f:
                        json.dump(info, f)

