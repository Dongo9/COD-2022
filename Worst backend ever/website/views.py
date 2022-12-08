from flask import Blueprint, render_template, render_template_string, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Note, User
from . import db
from datetime import datetime
views = Blueprint('views', __name__)
import json

@views.route('/', methods=['POST','GET'])
@login_required
def home():
    if request.method == 'POST':
        note = request.form.get('note')

        if len(note) < 1:
            flash('Note is too short!', category='error')
        else:
            now = datetime.now()
            new_note = Note(data=note, date=now, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Note added!', category='success')

    return render_template('home.html', user=current_user)

@views.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if request.method == 'GET':
        users = User.query.all()
        notes = Note.query.all()

        return render_template('admin.html', user=current_user, users=users, notes=notes)

@views.route('/delete-note', methods=['POST'])
def delete_note():
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id: #POSSIAMO CANCELLARE LE NOTE DA QUEST'IF
            db.session.delete(note)
            db.session.commit()
            
    return jsonify({}) 

@views.route('/delete-user', methods=['POST'])
def delete_user():
    user = json.loads(request.data)
    userId = user['userId']
    user = User.query.get(userId)
    if user:
        db.session.delete(user)
        db.session.commit()
    return jsonify({})

@views.route('/delete-note-admin', methods=['POST'])
def delete_note_admin():
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note: 
        db.session.delete(note)
        db.session.commit()
            
    return jsonify({}) 

@views.route('/user', methods=['GET'])
def user():
    username = request.args.get('username', default = current_user.first_name)

    template = ''' 
   {% extends "base.html" %} {% block title %}User panel{% endblock %}
   
    {%block content%}
        <br/>
            <h1 align="center">User panel</h1>
            <div>My name is: ''' +  username + '''</div>
            <div>My email address is: {{user.email}}</div>
        </body>
        </html>
    {%endblock%}
    '''

    return render_template_string(template, user = current_user)