import subprocess
import os
import os.path
from os import path

HOME = "/home/autofz"
OUT = "output"
PATH = os.getcwd()
MAB = "mab" # if directory name is not mab, it must change.
TARGET = [
    'exiv2',
    'ffmpeg',
    'imginfo',
    'infotocap',
    'lame',
    'mp42aac',
    'mujs',
    'nm',
    'objdump',
    'pdftotext',
    'tcpdump',
    'tiffsplit',
    'freetype2',
    'harfbuzz',
    'libarchive',
    'libjpeg',
    'boringssl',
    # 'openthread-2018-02-27-radio',
    'woff2',
    'wpantund',
    # 'boringssl-2016-02-12',
    'c-ares',
    'guetzli',
    # 'json-2017-02-12',
    'lcms',
    'libpng',
    're2',
    'sqlite',
    # 'vorbis-2017-12-11'
]

# Get docker container name in command "docker ps"
def getContainerName():
    nlist = [] # Name List

    psString = subprocess.check_output("docker ps --format \"{{.Names}}\"", shell=True).decode("utf-8")
    for name in psString.splitlines():
        nlist.append(name)
    return nlist

# Get output directory name in docker container with name entered as a parameter
def getLogPath(containerName):

    """ Get home directory's files """
    """ return string list """
    def getHomeFiles(container):
        # Get home directory's files
        homeDirectoryFiles = [] # Home directory List
        lsString = subprocess.check_output("docker exec -ti " 
                                            + container 
                                            + " sh -c \"ls ~\"", shell=True).decode("utf-8")
        for files in lsString.split():
            homeDirectoryFiles.append(files)

        return homeDirectoryFiles

    """ Get output directory's name """
    """ return string list """
    def getOutputDirectoryNames(homeDirectory):
        outputDirectoryNames = []
        for files in homeDirectory:
            if files.find(OUT) != -1:
                outputDirectoryNames.append(files)
            else:
                print("A file \'" + files + "\' is not output directory.")
                continue

        return outputDirectoryNames


    """ Get output directory's log file """
    """ return string """
    def getLogFile(container, outputDirectoryName):
        outputDirectoryFiles = [] # output directory List
        lsString = subprocess.check_output("docker exec -ti " 
                                            + container
                                            + " sh -c \"ls ~/" 
                                            + outputDirectoryName
                                            + "\"", shell=True).decode("utf-8")
        for files in lsString.split():
            outputDirectoryFiles.append(files)

        # Get log file's name
        logFileName = '' # default log file name
        for files in outputDirectoryFiles:
            if files.find('.json') != -1:
                logFileName = files
            else:
                continue
        if logFileName == '':
            print("There is no log file in " + outputDirectoryName + "!")

        return logFileName

    outputDirectories = getOutputDirectoryNames(getHomeFiles(containerName))
    
    logPaths = []
    for directory in outputDirectories:
        logPath = HOME + "/" + directory + "/" + getLogFile(containerName, directory)
        logPaths.append(logPath)

    return logPaths

# It modify a log for making focus_one to autofz_mab
def modifyFocusOneMAB(file):
    temp_line = []
    
    # Modify the line 1
    with open(file) as f:
        lines = f.readlines()
        for line in lines:
            line = line.replace('\"focus_one\": \"null\"', '\"focus_one\": \"autofz_mab\"')
            line = line.replace('\"focus_one\": \"afl\"', '\"focus_one\": \"autofz_mab\"')
            line = line.replace('\"focus_one\": \"aflfast\"', '\"focus_one\": \"autofz_mab\"')
            line = line.replace('\"focus_one\": \"mopt\"', '\"focus_one\": \"autofz_mab\"')
            line = line.replace('\"focus_one\": \"angora\"', '\"focus_one\": \"autofz_mab\"')
            line = line.replace('\"focus_one\": \"qsym\"', '\"focus_one\": \"autofz_mab\"')
            line = line.replace('\"focus_one\": \"fairfuzz\"', '\"focus_one\": \"autofz_mab\"')
            line = line.replace('\"focus_one\": \"lafintel\"', '\"focus_one\": \"autofz_mab\"')
            line = line.replace('\"focus_one\": \"learnafl\"', '\"focus_one\": \"autofz_mab\"')
            line = line.replace('\"focus_one\": \"libfuzzer\"', '\"focus_one\": \"autofz_mab\"')
            line = line.replace('\"focus_one\": \"radamsa\"', '\"focus_one\": \"autofz_mab\"')
            line = line.replace('\"focus_one\": \"redqueen\"', '\"focus_one\": \"autofz_mab\"')
            temp_line.append(line)
    # Rewrite
    with open(file, 'w') as f:
        f.writelines(temp_line)



def main():
    # Get container name
    containerList = getContainerName()

    for containerName in containerList:
        print()
        print("In" + containerName)
        logPaths = getLogPath(containerName)
        for logPath in logPaths:
            # If there is no log file -> continue
            if logPath.find(".json") == -1:
                continue
            
            # Set a target directory as a target program
            targetDirectory = PATH
            for target in TARGET:
                if logPath.find(target) != -1:
                    if not path.exists(target):
                        os.system("mkdir " + target)
                    targetDirectory = path.join(PATH, target)
            
            if logPath.find(MAB) != -1:
                if not path.exists(MAB):
                    os.system("mkdir mab")
                    targetDirectory = path.join(PATH, MAB)
            subprocess.call("docker cp " + containerName + ":" + logPath + " " + targetDirectory, shell=True)
    
    # If there are autofz_mab logs, it change focus_one for autofz-draw
    if path.exists(MAB):
        for (root, directories, files) in os.walk(MAB):
            for file in files:
                modifyFocusOneMAB(path.join(root, file))

if __name__ == "__main__":
    main()
