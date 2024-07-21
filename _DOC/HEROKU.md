```shell
heroku login
heroku git:remote restbill-dev
heroku git:remote -a restbill-dev
git push heroku RBS-141-NOTIFICATION:master
heroku run bash
```