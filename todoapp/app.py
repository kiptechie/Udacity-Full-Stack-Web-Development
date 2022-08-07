import sys
from flask import Flask, render_template, request, jsonify, redirect, url_for, abort
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from flask_migrate import Migrate

load_dotenv()

dbUser = os.getenv("DB_USER")
dbPassword = os.getenv("DB_PASSWORD")
dbHost = os.getenv("DB_HOST")
dbPort = os.getenv("DB_PORT")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{dbUser}:{dbPassword}@{dbHost}:{dbPort}/todoapp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Todo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    list_id = db.Column(db.Integer, db.ForeignKey(
        'todo_lists.id'), nullable=False)

    def __repr__(self):
        return f'<Todo {self.id} {self.description}>'


class TodoList(db.Model):
    __tablename__ = 'todo_lists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    all_completed = db.Column(db.Boolean, nullable=False, default=False)
    todos = db.relationship('Todo', backref='list', lazy=True)

    def __repr__(self):
        return f'<TodoList {self.id} {self.name}>'


# db.create_all()


@app.route('/todos/create', methods=['POST'])
def create_todo():
    error = False
    body = {}
    try:
        description = request.get_json()['description']
        list_id = request.get_json()['list_id']
        todo = Todo(description=description, completed=False, list_id=list_id)
        db.session.add(todo)
        db.session.commit()
        body['id'] = todo.id
        body['complete'] = todo.completed
        body['description'] = todo.description
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        return jsonify(body)


@app.route('/lists/create', methods=['POST'])
def create_todo_list():
    error = False
    body = {}
    try:
        name = request.get_json()['name']
        todolist = TodoList(name=name)
        db.session.add(todolist)
        db.session.commit()
        body['id'] = todolist.id
        body['name'] = todolist.name
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info)
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        return jsonify(body)


@app.route('/todos/<todo_id>/set-completed', methods=['POST'])
def set_completed_todo(todo_id):
    try:
        completed = request.get_json()['completed']
        todo = Todo.query.get(todo_id)
        todo.completed = completed
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('index'))


@app.route('/todos/<todo_id>/delete', methods=['POST'])
def delete_todo(todo_id):
    try:
        todo = Todo.query.filter_by(id=todo_id)
        todo.delete()
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return jsonify({'delete success': True})


@app.route('/lists/<list_id>/delete', methods=['DELETE'])
def delete_list(list_id):
    error = False
    try:
        list = TodoList.query.get(list_id)
        for todo in list.todos:
            db.session.delete(todo)

        db.session.delete(list)
        db.session.commit()
    except:
        db.session.rollback()
        error = True
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        return jsonify({'success': True})


@app.route('/lists/<list_id>/set-completed', methods=['POST'])
def set_completed_list(list_id):
    error = False

    try:
        list = TodoList.query.get(list_id)

        for todo in list.todos:
            todo.completed = True

        list.all_completed = True
        db.session.commit()
    except:
        db.session.rollback()

        error = True
    finally:
        db.session.close()

    if error:
        abort(500)
    else:
        return '', 200


@app.route('/lists/<list_id>')
def get_list_todos(list_id):
    return render_template(
        'index.html',
        lists=TodoList.query.order_by('id').all(),
        active_list=TodoList.query.get(list_id),
        todos=Todo.query
        .filter_by(list_id=list_id)
        .order_by('id')
        .all()
    )


@app.route('/')
def index():
    return redirect(url_for('get_list_todos', list_id=1))
