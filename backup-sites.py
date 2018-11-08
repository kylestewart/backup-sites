import os
import shutil
import datetime
import json
import re
import subprocess

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
    except:
        archive = str(archive) + "." + str(datetime.datetime.now().strftime('%f')) 
        os.makedirs(archive)
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

#Search source directories for WordPress Config files
def identify_wp_installs(srcPath):
    print("{} {} {}".format("Scanning",srcPath,"for WordPress configs"))
    wpInstalls = []
    for dir in os.listdir(srcPath):
        for file in os.listdir(os.path.join(srcPath,dir)):
            if file == "wp-config.php":
                wpInstalls.append(dir)
    return(wpInstalls)

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
    if backup_wp_dbs:
        wp_installs = identify_wp_installs(srcPath)
        if len(wp_installs) > 0:
            backup_wp_databases(srcPath,dstPath,wp_installs)
        else:
            print("No WP Installs were found")

#Take a list of WP Installs, snag the DB credentials, and take the dumps
#TODO decide what happens when any of these ifs are false
def backup_wp_databases(srcPath,dstPath,wpInstalls):
    for install in wpInstalls:
        dbinfo = {}
        srcdir = os.path.join(srcPath,install)
        dstdir = os.path.join(dstPath,install)
        myconf = os.path.join(dstdir,"mylogin.cnf")
        target = os.path.join(dstdir,install) + ".sql"
        with open(os.path.join(srcdir,'wp-config.php')) as config_file:
            for line in config_file:
                name = re.search('define\(\'DB_NAME\'\,\ ?\'(?P<dbname>.*)\'\);',line)
                if name:
                    dbinfo['dbname'] = name.group('dbname')
                    #print(dbinfo['dbname'])
                user = re.search('define\(\'DB_USER\'\,\ ?\'(?P<dbuser>.*)\'\);',line)
                if user:
                    dbinfo['dbuser'] = user.group('dbuser')
                    #print(dbinfo['dbuser'])
                password = re.search('define\(\'DB_PASSWORD\'\,\ ?\'(?P<dbpass>.*)\'\);',line)
                if password:
                    dbinfo['dbpass'] = password.group('dbpass')
                    #print (dbinfo['dbpass'])
                host = re.search('define\(\'DB_HOST\'\,\ ?\'(?P<dbhost>.*)\'\);',line)
                if host:
                    dbinfo['dbhost'] = host.group('dbhost')
                    #print(dbinfo['dbhost'])
        with open(myconf, 'w')as conf:
                print("[client]",file=conf)
                print("{}{}".format("host=",dbinfo['dbhost']),file=conf)
                print("{}{}".format("user=",dbinfo['dbuser']),file=conf)
                print("{}{}".format("password=",dbinfo['dbpass']),file=conf)
        args = "mysqldump --defaults-extra-file=" + myconf + " " + dbinfo['dbname'] + " > " + target
        subprocess.run(args, shell=True)
        os.remove(myconf)

archive_files(source)
prune_archives(destination,maxarchives)
