from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import jsonify, request, abort

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)


class Quote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quote = db.Column(db.String(255), unique=True, nullable=False)
    date = db.Column(db.String, nullable=True)
    annotation = db.Column(db.String(255), nullable=True)
    accepted = db.Column(db.Boolean, default=False)


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

    if Quote.query.filter_by(quote=request.form['Quote']):
        quote = Quote(quote=request.form['Quote'], date=request.form.get('Date', ''),
                      annotation=request.form.get('Annotation', ''))
        db.session.add(quote)
        db.session.commit()
        return quote.id

    else:
        abort(400)



