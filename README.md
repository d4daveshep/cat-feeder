# cat-feeder
Python code to control to Raspberry Pi automated cat feeder

## git commands to refresh files on raspberry pi...
```
"git pull" to refresh files from GitHub

"git commit" to commit new changes to local repo

"git push" to push committed changes to GitHub

"git checkout -f" to ignore any local non-committed changes
```
## crontab on raspberry pi to run every minute
```
m h  dom mon dow   command
* * * * * python3 /home/pi/dev/cat-feeder/CatFeeder.py
```
