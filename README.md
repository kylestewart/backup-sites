# WFBU - Webfaction Backup

I needed to automate the backups for the web apps on my hosting provider, Webfaction.  I also wanted an excuse to learn and practice Python.  When the opportunity presented myself, I got into it.  This is the work in progress that I've been using to accomplish these things.  

I am still learning, and this project has already evolved quite a bit in the short time I've been working on it.  I am maintaining a backlog of user stories to help manage what I add or fix next, so it is by no means "done".  That said, if you managed to find this somehow, I am open to feedback and would appreciate the opportunity to learn something new.

#Elevator Pitch

Backup a directory of files and subdirectories to another location.  Automatically identify WordPress installs, parse their configs, and get dumps of their databases.  Optionally compress or not compress, and also auto-upload the newest archive to S3.

# Quick Start

1. python3 -m pip install boto3
2. python3 -m pip install awscli
3. Rename settings-sample.json to settings.json and update it accordingly
4. python3 backup-script.py

 Note - If enabling the remote-upload you will still need to store your AWS credentials either as environment variables on in ~/.aws/credentials.  From my research the CLI is the best method for syncing entire directories, which was a requirement of that feature.  I've toyed with the idea of temporarily creating a credentials file or setting an environment variable, but I decided those were not ideal options.


