# cat-feeder
Python code to control to Raspberry Pi automated cat feeder

Git commands to refresh files on raspberry pi...

"git pull" to refresh files from GitHub

"git commit" to commit new changes to local repo

"git push" to push committed changes to GitHub 

# crontab on raspberry pi to run every minute
m h  dom mon dow   command
* * * * * python /home/david/dev/cat-feeder/CatFeeder.py
