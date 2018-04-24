# zsa-quotes-api
Great quotes by various ZSA teachers.

## Getting started
The first thing one needs to do after cloning the repository is initializing the python virtual environment and installing dependencies.

```
$ virtualenv env
$ source env/bin/activate
$ pip3 install -r requirements.txt
```

After executing the commands successfully, need to do the migration, create admin account and after that you're free to run the webserver.

```
$ python3 manage.py migrate
$ python3 manage.py createsuperuser
$ python3 manage.py runserver
```

Then you can use the API, e.g. via cURL:
```
$ curl -X POST -F "Quote=[quote]" -F "Date=[date] -F "Annotation=[annotation]" localhost:5000/api/submit
```

The list of endpoints is available on our [wiki](https://github.com/room23studios/wal-quotes/wiki)

