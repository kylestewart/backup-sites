import wfbu
import os
import json

_script_path = os.path.dirname(os.path.realpath(__file__))
_settings_path = os.path.join(_script_path,"config")
_settings_file = os.path.join(_settings_path,"settings.json")

#First we will load everything from our settings file
with open(_settings_file) as settings_file:
    config = json.load(settings_file)

#Load the config values
source        = config["backup"]["source"]
destination   = config["backup"]["destination"]
maxarchives   = config["backup"]["max_archives"]
autoprune     = config["backup"]["autoprune"]
backup_wp_dbs = config["backup"]["backup_wp_dbs"]
compression   = config["backup"]["compression"]
remote        = config["remote"]["enable_remote_upload"]
access_key    = config["remote"]["aws_access_key_id"]
secret_key    = config["remote"]["aws_secret_access_key"]
bucket_name   = config["remote"]["bucket_name"]
remote_folder = config["remote"]["folder"]


#Create a new backup object
backup = wfbu.backup()

#Create a new archive directory
archive_dir = backup.create_archive_dir(destination)

#Archive the source files into an archive directory
backup.archive_files(source, destination, compression, archive_dir)

#Backup Wordpress Databases, if desired
if backup_wp_dbs:
    backup.backup_wp_databases(source, destination, archive_dir)

#Prune the archives, if desired
if autoprune:
    backup.prune_archives(destination, maxarchives)

#If remote (currently only S3) is enabled, fire it up.
if remote:
    backup.remote_upload(destination, bucket_name, remote_folder)

