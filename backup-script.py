import wfbu

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

backup = wfbu.backup()



backup.archive_files()
