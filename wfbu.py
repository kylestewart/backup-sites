import os
import shutil
import datetime
import json
import re
import subprocess
import boto3 #AWS Remote, installed via pip

class backup:

#Create datestamped archive directory at destination
    def create_archive_dir(destination):
        date = datetime.datetime.now().strftime('%Y-%m-%d_%H%M')
        archive = os.path.join(self.destination,date)
        try:
            os.makedirs(archive)
        except:
            archive = str(archive) + "." + str(datetime.datetime.now().strftime('%f')) 
            os.makedirs(archive)
        return(archive)

#Get a list of archives and sort the list by creation time
    def list_archives(self):
        archives = []
        for dir in os.listdir(self.destination):
            archives.append(os.path.join(self.destination,dir))
        archives = sorted(archives, key=os.path.getctime)
        return(archives)

#Return the name of the newest archive directory
    def get_newest_archive(self):
        archives = self.list_archives()
        newest_index = len(archives) - 1
        newest_archive = archives[newest_index]
        return (newest_archive)

#Prune old backup directories, as defined in the settings file
    def prune_archives(self):
        archives = self.list_archives()
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
        dstPath = self.create_archive_dir()
        for object in os.listdir(self.source):
            if self.compression:
                if os.path.isfile(os.path.join(self.source,object)):
                    zipfile = os.path.join(dstPath,object)
                    shutil.make_archive(zipfile,'zip',dstPath,os.path.join(self.source,object))
                if os.path.isdir(os.path.join(self.source,object)):
                    zipdir = os.path.join(dstPath,object)
                    os.makedirs(zipdir)
                    shutil.make_archive(os.path.join(zipdir,object),'zip',zipdir,os.path.join(self.source,object))
            else:
                if os.path.isfile(os.path.join(self.source,object)):
                    shutil.copyfile(os.path.join(self.source,object),os.path.join(dstPath,object))
                if os.path.isdir(os.path.join(self.source,object)):
                    shutil.copytree(os.path.join(self.source,object),os.path.join(dstPath,object))
        
        if self.backup_wp_dbs:
            self.backup_wp_databases()
        
        if self.autoprune:
            self.prune_archives()
        
        if self.remote:
            self.remote_upload()
        return("Archiving Complete")


#Take a list of WP Installs, snag the DB credentials, and take the dumps.  The newest created archive dir will get the dump files.
    def backup_wp_databases(self):
        wpInstalls = self.identify_wp_installs()
        for install in wpInstalls:
            dbinfo  = {}
            srcdir  = os.path.join(self.source,install)
            dstPath = os.path.join(self.destination,self.get_newest_archive())
            dstdir  = os.path.join(dstPath,install)
            myconf  = os.path.join(dstdir,"mylogin.cnf")
            target  = os.path.join(dstdir,install) + ".sql"
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


#Use boto3 to create a session with S3
    def remote_connect(self):
        session = boto3.Session(
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
        )
        return(session)

    def remote_ls_buckets(self):
        buckets = []
        session = self.connect()
        s3 = session.resource('s3')
        for bucket in s3.buckets.all():
            buckets.append(bucket)
        return(buckets)

#Until boto3 supports directory syncing, we'll use this method to shell out and use the aws CLI.
    def remote_upload(self):
        src = self.get_newest_archive()
        dest = "s3://" + self.bucket_name + self.remote_folder
        cmd = "{} {} {} {} {} {} {}".format("aws","s3","sync",src,dest,"--size-only","--delete")
        subprocess.run(cmd,shell = True)
        return("Upload Complete")


