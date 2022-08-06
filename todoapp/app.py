from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

load_dotenv()

dbUser = os.getenv("DB_USER")
dbPassword = os.getenv("DB_PASSWORD")
dbHost = os.getenv("DB_HOST")
dbPort = os.getenv("DB_PORT")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{dbUser}:{dbPassword}@{dbHost}:{dbPort}/todoapp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Todo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<Todo {self.id} {self.description}>'


db.create_all()
todos = Todo.query.all()


@app.route('/')
def index():
    return render_template('index.html', data=todos)
