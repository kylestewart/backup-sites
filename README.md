# WFBU - Webfaction Backup

I wanted to both automate the backups for all of my webapps on the Webfaction platform and to teach myself python.  This is the work in progress to accomplish those things.  I am still learning Python so there are sure to be some horrifying things in here, but that said, feedback is always appreciated as I aim to improve.

# Quick Start

1. Clone this repo
2. python3 -m pip install boto3
3. python3 -m pip install awscli
2. Rename settings-sample.json to settings.json and update it accordingly
3. python3 backup-script.py

 Note - If enabling the remote-upload you will still need to store your AWS credentials either as environment variables on in ~/.aws/credentials.  Although the boto connection works with the config file, I am having to shell out to use the aws cli for the actual upload.  It's a drag, but if you're using S3 you probably already have a credentials file anyway.


