import os
import shutil
import datetime
import json
import re
import subprocess

_script_path = os.path.dirname(os.path.realpath(__file__))
_settings_path = os.path.join(_script_path,"config")
_settings_file = os.path.join(_settings_path,"settings.json")

class backup:
    def __init__(self):
#First we will load everything from our settings file        
        with open(_settings_file) as settings_file:
            config = json.load(settings_file)

#Load the config values        
        self.source = config["backup"]["source"]
        self.destination = config["backup"]["destination"]
        self.maxarchives = int(config["backup"]["max-archives"])
        self.autoprune = config["backup"]["autoprune"]
        self.backup_wp_dbs = config["backup"]["backup_wp_dbs"]
        self.compression = config["backup"]["compression"]

#Create datestamped archive directory at destination
    def create_archive_dir(self):
        date = datetime.datetime.now().strftime('%Y-%m-%d_%H%M')
        archive = os.path.join(self.destination,date)
        try:
            os.makedirs(archive)
        except:
            archive = str(archive) + "." + str(datetime.datetime.now().strftime('%f')) 
            os.makedirs(archive)
        return(archive)

#Prune old backup directories, as defined in the settings file
    def prune_archives(self):
        archives = []
        for dir in os.listdir(self.destination):
             archives.append(os.path.join(self.destination,dir))
        if len(archives) > self.maxarchives:
            toPrune = int(len(archives)) - int(self.maxarchives)
            archives = sorted(archives, key=os.path.getctime)
            i = 0
            while i < toPrune:
                shutil.rmtree(archives[i])
                i += 1
        else:
            toPrune = 0
        return("{} {} {}".format("Pruned",toPrune,"Archives"))

#Search source directories for WordPress Config files
    def identify_wp_installs(self):
        wpInstalls = []
        for dir in os.listdir(self.source):
            for file in os.listdir(os.path.join(self.source,dir)):
                if file == "wp-config.php":
                    wpInstalls.append(dir)
        return(wpInstalls)

#Backup content of source directories
    def archive_files(self):
        archives = []
        dstPath = self.create_archive_dir()
        for dir in os.listdir(self.source):
            if self.compression:
                zipdir = os.path.join(dstPath,dir)
                os.makedirs(zipdir)
                shutil.make_archive(os.path.join(zipdir,dir),'zip',zipdir,os.path.join(self.source,dir))
            else:
                shutil.copytree(os.path.join(self.source,dir),os.path.join(dstPath,dir))
        if self.backup_wp_dbs:
            wp_installs = self.identify_wp_installs()
            if len(wp_installs) > 0:
                self._backup_wp_databases(dstPath,wp_installs)
            else:
                print("No WP Installs were found")
        if self.autoprune:
            self.prune_archives()
        return("{} : {}".format("File archiving complete in directory",dstPath))

#Take a list of WP Installs, snag the DB credentials, and take the dumps.  At the moment this is not intended to be called directly outside of the archive_files method.
    def _backup_wp_databases(self,dstPath,wpInstalls):
        for install in wpInstalls:
            dbinfo = {}
            srcdir = os.path.join(self.source,install)
            dstdir = os.path.join(dstPath,install)
            myconf = os.path.join(dstdir,"mylogin.cnf")
            target = os.path.join(dstdir,install) + ".sql"
            with open(os.path.join(srcdir,'wp-config.php')) as config_file:
                for line in config_file:
                    name = re.search('define\(\'DB_NAME\'\,\ ?\'(?P<dbname>.*)\'\);',line)
                    if name:
                        dbinfo['dbname'] = name.group('dbname')
                    user = re.search('define\(\'DB_USER\'\,\ ?\'(?P<dbuser>.*)\'\);',line)
                    if user:
                        dbinfo['dbuser'] = user.group('dbuser')
                    password = re.search('define\(\'DB_PASSWORD\'\,\ ?\'(?P<dbpass>.*)\'\);',line)
                    if password:
                        dbinfo['dbpass'] = password.group('dbpass')
                    host = re.search('define\(\'DB_HOST\'\,\ ?\'(?P<dbhost>.*)\'\);',line)
                    if host:
                        dbinfo['dbhost'] = host.group('dbhost')
            with open(myconf, 'w')as conf:
                print("[client]",file=conf)
                print("{}{}".format("host=",dbinfo['dbhost']),file=conf)
                print("{}{}".format("user=",dbinfo['dbuser']),file=conf)
                print("{}{}".format("password=",dbinfo['dbpass']),file=conf)
            args = "mysqldump --defaults-extra-file=" + myconf + " " + dbinfo['dbname'] + " > " + target
            subprocess.run(args, shell=True)
            os.remove(myconf)
        return("Database backup complete")
