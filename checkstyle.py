import os 
import requests
import subprocess
from bs4 import BeautifulSoup

def check(codeFile: str, checkstyleConfigFile: str, checkstyleJar: str = None) -> list:
    if checkstyleJar == "" or checkstyleJar is None:
        checkstyleJar = "jars/checkstyle-8.0-all.jar"

    if not os.path.exists(checkstyleJar):    
        # auto download jar
        version = checkstyleJar.split("/")[-1][:-8]
        if not os.path.exists(checkstyleJar):
            url = f"https://github.com/checkstyle/checkstyle/releases/download/{version}/{version}-all.jar"
            binary = requests.get(url)
            with open(checkstyleJar, "wb") as f:
                f.write(binary.content)

    cmd = ["java", "-jar", checkstyleJar, "-f", "xml", "-c", checkstyleConfigFile, codeFile]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    output = process.communicate()[0]
    output = BeautifulSoup(output, "xml").find("file")
    ret = []
    if output is not None:
        for i in output.children:
            if i.name == None: continue
            ret.append(i.attrs)
    
    return ret
