import os

from flask import Flask, render_template, request, url_for
from flask.json import jsonify
from flask_cors import CORS
from pandas._libs import json

from pandastests import make_conversion
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'carol'
socketio = SocketIO(app)


# @app.route('/')
# def hello_world():
#    file = 'datatest1.xls'
#    print(make_conversion(file, 40).to_dict('dict'))
#    return render_template('index.html', alumnos=make_conversion(file, 40))
#    # print(make_conversion(file,40).iterrows()['MATRICULA'])
#    # return 'HOLA MUNDO'


# @app.route('/tests', methods=['POST'])
# def tests(*args):
#    print(request.form['format'])
#    return jsonify(request.form)


def make_note_uri(note):
    new_note = {}
    for field in note:
        if field == 'id':
            new_note['uri'] = 'url'
        else:
            new_note[field] = note[field]
    return new_note



def loads_bd():
    with open('notes.txt', 'tr') as bd:
        return eval(bd.read())


def write_db(notelist):
    with open('notes.txt', 'wt') as db:
        db.write(str(notelist))


@socketio.on('connect')
def handle_connect():
    print('Connected')
    send_notes()


@socketio.on('get notes')
def send_notes():
    notes = loads_bd()
    socketio.emit('notes', {'notes': list(map(make_note_uri, notes))})
    # socketio.send({'notes': list(map(make_note_uri, notes))}, json=True)


# @app.route('/notes', methods=['GET'])
# def get_notes():
#    return jsonify({'notes': list(map(make_note_uri, notes))})
#
#
# @app.route('/get_note', methods=['GET'])
# def get_note():
#    return jsonify({'notes': list(map(make_note_uri, notes))})


@socketio.on('message')
def handle_json(message):
    content = json.loads(str(message))
    print('Content ' + str(content))
    if not content:
        return
    notes = loads_bd()
    id = 0
    try:
        id = notes[-1]['id'] + 1
    except Exception:
        id = 0

    note = {
        'id': id,
        'title': content['title'],
        'body': content['body'],
        'color': content['color'],
        'fontColor': content['fontColor']
    }
    notes.append(note)
    write_db(notes)
    socketio.emit('add note', {'note': make_note_uri(note)})


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    socketio.run(app)
