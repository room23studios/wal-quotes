from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import jsonify, request, abort, g
from passlib.apps import custom_app_context as pwd_context
from flask_httpauth import HTTPBasicAuth
from sqlalchemy.sql.expression import func, desc

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
auth = HTTPBasicAuth()


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


@app.route('/api/id/<int:quote_id>')
def get_quote(quote_id):
    quote_db = Quote.query.filter_by(id=quote_id).first()
    if quote_db is not None:
        if quote_db.accepted:
            quote = {'quote': quote_db.quote,
                     'date': quote_db.date,
                     'annotation': quote_db.annotation}
            return jsonify(quote)
        else:
            abort(403)
    else:
        abort(404)


@app.route('/api/submit', methods=['POST'])
def submit():
    if Quote.query.filter_by(quote=request.form['Quote']).scalar() is None:
        quote = Quote(quote=request.form['Quote'], date=request.form.get('Date', ''),
                      annotation=request.form.get('Annotation', ''))
        db.session.add(quote)
        db.session.commit()
        return str(quote.id)

    else:
        abort(400)


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
    return jsonify(output)


@app.route('/api/submissions/<int:quote_id>', methods=['POST'])
@auth.login_required
def set_submissions(quote_id):
    quote_db = Quote.query.filter_by(id=quote_id).first()
    if quote_db is not None:
        if request.form.get('action', 'accept') == 'accept':
            quote_db.accepted = True
            db.session.add(quote_db)
            db.session.commit()
            return '', 200
        else:
            Quote.query.filter_by(id=quote_id).delete()
            db.session.commit()
            return '', 200
    else:
        abort(404)


@app.route('/api/new_admin', methods=['POST'])
@auth.login_required
def add_admin():
    if Admin.query.filter_by(username=request.form['Username']).scalar() is None:
        admin = Admin(username=request.form['Username'])
        admin.hash_password(request.form['Username'])
        db.session.add(admin)
        db.session.commit()
        return '', 200
    else:
        abort(400)


@app.route('/api/change_password', methods=['POST'])
@auth.login_required
def change_password():
    g.user.hash_password(request.form['Password'])
    db.session.add(g.user)
    db.session.commit()
    return '', 200


@app.route('/api/random')
def get_random_quote():
    quote_db = Quote.query.filter_by(accepted=True).order_by(func.random()).first()
    quote = {'id': quote_db.id,
             'quote': quote_db.quote,
             'date': quote_db.date,
             'annotation': quote_db.annotation}
    return jsonify(quote)


@app.route('/api/daily')
def get_daily():
    quote_id = Daily.query.order_by(desc(Daily.id)).first().quote_id
    quote_db = Quote.query.filter_by(id=quote_id).first()
    quote = {'id': quote_db.id,
             'quote': quote_db.quote,
             'date': quote_db.date,
             'annotation': quote_db.annotation}
    return jsonify(quote)


@app.route('/api/new_daily')
@auth.login_required
def new_daily():
    daily_id = Quote.query.filter_by(accepted=True).order_by(func.random()).first().id
    while daily_id == Daily.query.order_by(desc(Daily.id)).first().quote_id:
        daily_id = Quote.query.filter_by(accepted=True).order_by(func.random()).first().id
    daily = Daily(quote_id=daily_id)
    db.session.add(daily)
    db.session.commit()
    return '', 200
