import os
import shutil
import datetime
import re
import subprocess
import boto3 #AWS Remote, installed via pip

class backup:
    #def __init__():

#Create datestamped archive directory at destination
    def create_archive_dir(self,destination):
        date = datetime.datetime.now().strftime('%Y-%m-%d_%H%M')
        archive = os.path.join(destination,date)
        try:
            os.makedirs(archive)
        except:
            archive = str(archive) + "." + str(datetime.datetime.now().strftime('%f'))
            os.makedirs(archive)
        return(archive)

#Get a list of archives and sort the list by creation time
    def list_archives(self,destination):
        archives = []
        for dir in os.listdir(destination):
            archives.append(os.path.join(destination,dir))
        archives = sorted(archives, key=os.path.getctime)
        return(archives)

#Return the name of the newest archive directory
    def get_newest_archive(self,destination):
        archives = self.list_archives(destination)
        newest_index = len(archives) - 1
        newest_archive = archives[newest_index]
        return (newest_archive)

#Prune old backup directories, as defined in the settings file
    def prune_archives(self,destination,maxarchives):
        archives = self.list_archives(destination)

        if len(archives) > maxarchives:
            toPrune = int(len(archives)) - maxarchives
            archives = sorted(archives, key=os.path.getctime)

            i = 0
            while i < toPrune:

                #Check if the object is a file.  If it is, leave it alone.
                if os.path.isfile(os.path.join(destination,archives[i])):
                    pass
                else:
                    shutil.rmtree(archives[i])
                i += 1

        else:
            toPrune = 0

        return("{} {} {}".format("Pruned",toPrune,"Archives"))

#Search source directories for WordPress Config files
    def identify_wp_installs(self,source):
        wpInstalls = []
        for dir in os.listdir(source):
            for file in os.listdir(os.path.join(source,dir)):
                if file == "wp-config.php":
                    wpInstalls.append(dir)
        return(wpInstalls)

#Backup content of source directories
    def archive_files(self,source,destination,compression,archive_dir=None):

        #Use the provided Archive Directory, or make one if it isn't provided
        if archive_dir == None:
            dstPath = self.create_archive_dir(destination)
        else:
            dstPath = archive_dir

        for object in os.listdir(source):
            if compression:
                if os.path.isfile(os.path.join(source,object)):
                    zipfile = os.path.join(dstPath,object)
                    shutil.make_archive(zipfile,'zip',dstPath,os.path.join(source,object))
                if os.path.isdir(os.path.join(source,object)):
                    zipdir = os.path.join(dstPath,object)
                    os.makedirs(zipdir)
                    shutil.make_archive(os.path.join(zipdir,object),'zip',zipdir,os.path.join(source,object))
            else:
                if os.path.isfile(os.path.join(source,object)):
                    shutil.copyfile(os.path.join(source,object),os.path.join(dstPath,object))
                if os.path.isdir(os.path.join(source,object)):
                    shutil.copytree(os.path.join(source,object),os.path.join(dstPath,object))

        return("Archiving Complete")


#Take a list of WP Installs, snag the DB credentials, and take the dumps.  The newest created archive dir will get the dump files.
    def backup_wp_databases(self,source,destination,archive_dir=None):
        wpInstalls = self.identify_wp_installs(source)
        for install in wpInstalls:
            dbinfo  = {}
            srcdir  = os.path.join(source,install)

            #Use the provided Archive Directory, or use the newest one if it isn't provided
            if archive_dir == None:
                dstPath = os.path.join(destination,self.get_newest_archive(destination))
            else:
                dstPath = archive_dir

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
    def remote_connect(self,access_key,secret_key):
        session = boto3.Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
        )
        return(session)

#This works but not useful at the moment.  After connecting, list the buckets.
    def remote_ls_buckets(self):
        buckets = []
        session = self.connect()
        s3 = session.resource('s3')
        for bucket in s3.buckets.all():
            buckets.append(bucket)
        return(buckets)

#Until boto3 supports directory syncing, we'll use this method to shell out and use the aws CLI.
    def remote_upload(self,destination,bucket_name,remote_folder):
        src = self.get_newest_archive(destination)
        dest = "s3://" + bucket_name + remote_folder
        cmd = "{} {} {} {} {} {} {}".format("aws","s3","sync",src,dest,"--size-only","--delete")
        subprocess.run(cmd,shell = True)
        return("Upload Complete")


