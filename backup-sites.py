import os,shutil,datetime,json
from pprint import pprint
from pathlib import Path,PurePath

#CONSTANTS
script_path = os.path.dirname(os.path.realpath(__file__))
settings_path = os.path.join(script_path,"config")
settings_file = os.path.join(settings_path,"settings.json")
date = datetime.datetime.now().strftime('%Y-%m-%d_%H%M')

#Load the config files
with open(settings_file) as settings_file:
    config = json.load(settings_file)
    backup = config["directory"]["backup"]
    destination = config["directory"]["destination"]
    maxbackups = int(config["parameters"]["max-backups"])

#Create datestamped archive directory at destination
def create_archive_dir(dstPath,dateStamp):
    archive = os.path.join(dstPath,date)
    os.makedirs(archive)

#Prune old backup directories, as defined in the settings file
def prune_archives(dstPath,MaxDirs):
    CurDirs = len(os.listdir(dstPath))
    if CurDirs > MaxDirs:
        diff = CurDirs - MaxDirs
        print("{} {} {}".format("Too many dirs by",diff,"directories"))
   
   

prune_archives(destination,maxbackups)
#create_archive_dir(destination,date)
