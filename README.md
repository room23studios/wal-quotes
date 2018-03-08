# zsa-quotes-api
Memorable quotes from ZSA teachers.

## Getting started
The first thing one needs to do after cloning the repository is initializing the database and creating the admin account.

```
$ python3
> from main import db, Admin
> db = create_all()
> admin = Admin(username=[username])
> admin.hash_password([password])
> db.session.add(admin)
> db.session.commit()
```

After executing the commands successfully, you're free to close the python shell and launch the webserver.

```
$ FLASK_APP=main.py flask run
```

Then you can use the API, e.g. via cURL:
```
$ curl -X POST -F "Quote=[quote]" -F "Date=[date] -F "Annotation=[annotation]" localhost:5000/api/submit
```

The list of endpoints is available on our [wiki](https://github.com/room23studios/wal-quotes/wiki)
