import os,shutil,datetime,json
from pprint import pprint

#CONSTANTS
script_path = os.path.dirname(os.path.realpath(__file__))
settings_path = os.path.join(script_path,"config")
settings_file = os.path.join(settings_path,"settings.json")

#Load the config files
with open(settings_file) as settings_file:
    config = json.load(settings_file)
    source = config["directory"]["source"]
    destination = config["directory"]["destination"]
    maxarchives = int(config["parameters"]["max-archives"])
    backup_wp_dbs = config["parameters"]["backup_wp_dbs"]
    compression = config["parameters"]["compression"]

#Create datestamped archive directory at destination
def create_archive_dir(dstPath):
    date = datetime.datetime.now().strftime('%Y-%m-%d_%H%M')
    archive = os.path.join(dstPath,date)
    try:
        os.makedirs(archive)
    except FileExistsError:
        archive = str(archive) + "." + str(datetime.datetime.now().strftime('%f')) 
        os.makedirs(archive)
    except:
        print("Failed to make destination directory")
    return(archive)

#Prune old backup directories, as defined in the settings file
def prune_archives(dstPath,MaxArchives):
    archives = []
    for dir in os.listdir(dstPath):
        archives.append(os.path.join(dstPath,dir))
    if len(archives) > MaxArchives:
        toPrune = int(len(archives)) - int(MaxArchives)
        print("{} = {}".format("Allowed Archives ",MaxArchives))
        print("{} = {}".format("Existing Archives",len(archives)))
        print("{} = {}".format("Archives to Prune",toPrune))
        archives = sorted(archives, key=os.path.getctime)
        i = 0
        while i < toPrune:
            print("{} : {}".format("Pruning",archives[i]))
            shutil.rmtree(archives[i])
            i += 1

#Backup content of source directories
def archive_files(srcPath):
    archives = []
    dstPath = create_archive_dir(destination)
    for dir in os.listdir(srcPath):
        if compression:
            zipdir = os.path.join(dstPath,dir)
            os.makedirs(zipdir)
            shutil.make_archive(os.path.join(zipdir,dir),'zip',zipdir,os.path.join(srcPath,dir))
        else:
            shutil.copytree(os.path.join(srcPath,dir),os.path.join(dstPath,dir))

        
#Search source directories for WordPress Config files
def identify_wp_installs(srcPath):
    print("{} {} {}".format("Scanning",srcPath,"for WordPress configs"))
    wpInstalls = []
    for dir in os.listdir(srcPath):
        for file in os.listdir(os.path.join(srcPath,dir)):
            if file == "wp-config.php":
                wpInstalls.append(dir)
    print(wpInstalls)
 

#archive_files(source)
#prune_archives(destination,maxarchives)
identify_wp_installs(source)
