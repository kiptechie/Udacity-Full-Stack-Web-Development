from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html', data=[
        {'id': 1, 'title': 'Todo 1'},
        {'id': 2, 'title': 'Todo 2'},
        {'id': 3, 'title': 'Todo 3'},
        {'id': 4, 'title': 'Todo 4'},
    ])
