from email.policy import default
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from flask_migrate import Migrate

load_dotenv()

dbUser = os.getenv("DB_USER")
dbPassword = os.getenv("DB_PASSWORD")
dbHost = os.getenv("DB_HOST")
dbPort = os.getenv("DB_PORT")
dbName = os.getenv("DB")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{dbUser}:{dbPassword}@{dbHost}:{dbPort}/{dbName}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Person(db.Model):
    __tablename__ = 'people'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f'<Person id: {self.id}, name: {self.name}>'


# db.create_all()


def addMulamwa():
    mulamwa = Person(name='Mulamwa')
    db.session.add(mulamwa)
    db.session.commit()


@app.route('/')
def index():
    addMulamwa()
    person = Person.query.first()
    return f'Good Evening {person.name}!'
