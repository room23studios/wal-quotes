from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import request, abort, g, Response
from passlib.apps import custom_app_context as pwd_context
from flask_httpauth import HTTPBasicAuth
from sqlalchemy.sql.expression import func, desc
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import json
from flask_cors import CORS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
CORS(app)
db = SQLAlchemy(app)
auth = HTTPBasicAuth()
limiter = Limiter(app, key_func=get_remote_address)


class Quote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quote = db.Column(db.String(255), unique=True, nullable=False)
    date = db.Column(db.String, nullable=True)
    annotation = db.Column(db.String(255), nullable=True)
    accepted = db.Column(db.Boolean, default=False)


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    password_hash = db.Column(db.String(128))

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)


class Daily(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quote_id = db.Column(db.Integer)


@app.route('/api/quote/<int:quote_id>')
def get_quote(quote_id):
    quote_db = Quote.query.filter_by(id=quote_id).filter_by(accepted=True).first()
    if quote_db is not None:
        quote = {'quote': quote_db.quote,
                 'date': quote_db.date,
                 'annotation': quote_db.annotation,
                 'id': quote_db.id}
        return make__json_response({'status': 'success',
                                    'quote': quote})
    else:
        return make__json_response({'status': 'error',
                                    'description': 'Quote does not exist'})


@app.route('/api/quote/<int:quote_id>/next')
def get_next_quote(quote_id):
    quote_db = Quote.query.order_by(Quote.id).filter(Quote.id > quote_id).filter_by(accepted=True).first()
    if quote_db is not None:
            quote = {'quote': quote_db.quote,
                     'date': quote_db.date,
                     'annotation': quote_db.annotation,
                     'id': quote_db.id}
            return make__json_response({'status': 'success',
                                        'quote': quote})
    else:
        return make__json_response({'status': 'error',
                                    'description': 'Quote does not exist'})


@app.route('/api/quote/<int:quote_id>/prev')
def get_prev_quote(quote_id):
    quote_db = Quote.query.order_by(desc(Quote.id)).filter(Quote.id < quote_id).filter_by(accepted=True).first()
    if quote_db is not None:
        quote = {'quote': quote_db.quote,
                 'date': quote_db.date,
                 'annotation': quote_db.annotation,
                 'id': quote_db.id}
        return make__json_response({'status': 'success',
                                    'quote': quote})
    else:
        return make__json_response({'status': 'error',
                                    'description': 'Quote does not exist'})



@app.route('/api/quotes')
def get_quotes():
    quotes = Quote.query.filter_by(accepted=True)
    output = []
    for quote in quotes:
        output.append({'quote': quote.quote,
                       'date': quote.date,
                       'annotation': quote.annotation})
    return make__json_response({'status': 'success', 'quotes': output})


@app.route('/api/submit', methods=['POST'])
@limiter.limit("20 per hour")
def submit():
    if Quote.query.filter_by(quote=request.form['Quote']).first() is None:
        quote = Quote(quote=request.form['Quote'], date=request.form.get('Date', ''),
                      annotation=request.form.get('Annotation', ''))
        db.session.add(quote)
        db.session.commit()
        return make__json_response({'status': 'success',
                                    'id': quote.id})

    else:
        return make__json_response({'status': 'error',
                                    'description': 'Quote is not unique'})


@auth.verify_password
def verify_password(username, password):
    admin = Admin.query.filter_by(username=username).first()
    if not admin or not admin.verify_password(password):
        return False
    g.user = admin
    return True


@app.route('/api/submissions')
@auth.login_required
def get_submissions():
    output = []
    quotes = Quote.query.filter_by(accepted=False)
    for quote in quotes:
        output.append({'id': quote.id,
                       'quote': quote.quote,
                       'date': quote.date,
                       'annotation': quote.annotation})
    return make__json_response({'status': 'success',
                                'submissions': output})


@app.route('/api/delete/<int:quote_id>', methods=['POST'])
@auth.login_required
def remove_quote(quote_id):
    quote_db = Quote.query.filter_by(id=quote_id).first()
    if quote_db is not None:
        Quote.query.filter_by(id=quote_id).delete()
        db.session.commit()
        return make__json_response({'status': 'success'})
    else:
        return make__json_response({'status': 'error',
                                    'description': 'Quote does not exist'})


@app.route('/api/submissions/<int:quote_id>', methods=['POST'])
@auth.login_required
def set_submissions(quote_id):
    quote_db = Quote.query.filter_by(id=quote_id).first()
    if quote_db is not None:
        quote_db.accepted = True
        db.session.add(quote_db)
        db.session.commit()
        return make__json_response({'status': 'success'})
    else:
        return make__json_response({'status': 'error',
                                    'description': 'Quote does not exist'})


@app.route('/api/new_admin', methods=['POST'])
@auth.login_required
def add_admin():
    if Admin.query.filter_by(username=request.form['Username']).first() is None:
        admin = Admin(username=request.form['Username'])
        admin.hash_password(request.form['Username'])
        db.session.add(admin)
        db.session.commit()
        return make__json_response({'status': 'success'})
    else:
        return make__json_response({'status': 'error',
                                    'description': 'Username is not unique'})


@app.route('/api/change_password', methods=['POST'])
@auth.login_required
def change_password():
    g.user.hash_password(request.form['Password'])
    db.session.add(g.user)
    db.session.commit()
    return make__json_response({'status': 'success'})


@app.route('/api/random')
def get_random_quote():
    if Quote.query.first() is not None:
        quote_db = Quote.query.filter_by(accepted=True).order_by(func.random()).first()
        quote = {'id': quote_db.id,
                 'quote': quote_db.quote,
                 'date': quote_db.date,
                 'annotation': quote_db.annotation}
        return make__json_response({'status': 'success',
                                    'quote': quote})
    else:
        return make__json_response({'status': 'error',
                                    'description': 'No accepted quotes in database'})


@app.route('/api/daily')
def get_daily():
    if Daily.query.first() is not None:
        quote_id = Daily.query.order_by(desc(Daily.id)).first().quote_id
        quote_db = Quote.query.filter_by(id=quote_id).first()
        quote = {'id': quote_db.id,
                 'quote': quote_db.quote,
                 'date': quote_db.date,
                 'annotation': quote_db.annotation}
        return make__json_response({'status': 'success',
                                    'quote': quote})
    else:
        return make__json_response({'status': 'error',
                                    'description': 'No daily quote'})


@app.route('/api/new_daily', methods=['POST'])
@auth.login_required
def new_daily():
    if not change_daily():
        return make__json_response({'status': 'error',
                                    'description': 'No accepted quotes in database'})
    else:
        return make__json_response({'status': 'success',
                                    'id': Daily.query.order_by(desc(Daily.id)).first().quote_id})


def change_daily():
    if Quote.query.filter_by(accepted=True).first is not None:
        daily_id = Quote.query.filter_by(accepted=True).order_by(func.random()).first().id
        if Daily.query.order_by(desc(Daily.id)).first() is not None:
            while daily_id == Daily.query.order_by(desc(Daily.id)).first().quote_id:
                daily_id = Quote.query.filter_by(accepted=True).order_by(func.random()).first().id
        daily = Daily(quote_id=daily_id)
        db.session.add(daily)
        db.session.commit()
        return True
    else:
        return False


def make__json_response(json_object):
    resp = Response(json.dumps(json_object, ensure_ascii=False).encode('utf8'))
    resp.headers['Content-Type'] = 'application/json'
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp
