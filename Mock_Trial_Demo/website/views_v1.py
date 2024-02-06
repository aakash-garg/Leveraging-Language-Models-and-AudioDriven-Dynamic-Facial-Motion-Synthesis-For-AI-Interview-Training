from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from . import db
import json
from .model import *
from .models import *
from sqlalchemy import desc
import webbrowser
import keyboard
from time import sleep

views = Blueprint('views', __name__)


@views.route('/', methods=['GET'])
@login_required
def home():
    return render_template("home.html", user=current_user)

@views.route('/predict', methods=['POST'])
def predict():
    text = request.get_json().get("message")
    # response = get_response(text)
    response = run_ai(all_intents, queries, manual_responses, queries_encoded, embeddings, final_sentences, context_s, intents, responses, text)
    

    new_message = Chat(request_text = text, response_text = response, user_id=current_user.id) 
    
    try:
        db.session.add(new_message)
        db.session.commit()
        message = {"answer": response, "id": new_message.id}
        return jsonify(message)
    except:
        return jsonify(message), print("Error creating")

@views.route('/history', methods=['POST','GET'])
@login_required
def index_history():
    if request.method == 'POST':
        note = request.form.get('note')

        if len(note) < 1:
            flash('Note is too short!', category='error')
        else:
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Note added!', category='success')
            notes = Note.query.order_by(desc(Note.id)).all()
            messages = Chat.query.order_by(desc(Chat.user_id)).all()
            # return render_template("history.html", notes)
    else:
        messages = Chat.query.order_by(desc(Chat.user_id)).all()
        notes = Note.query.order_by(desc(Note.id)).all()

    return render_template("history.html", messages = messages, notes=notes, user=current_user)

@views.route('/edit_chat', methods=['GET'])
@login_required
def index_edit_history():
    messages = edit_Chat.query.order_by(desc(edit_Chat.date_created)).all()
    return render_template("edit_chat.html", messages = messages, user=current_user)

@views.route('/train/<int:id>', methods=["POST", "GET"])
def train(id):
    message_to_edit = edit_Chat.query.get_or_404(id)

    question = message_to_edit.request_text
    answer = message_to_edit.edit_response_text

    tune(all_intents, queries, manual_responses, queries_encoded, embeddings, final_sentences, context_s, intents, responses, question, answer)
    flash('AI-Model Update Complete', category='success')
    db.session.delete(message_to_edit)
    db.session.commit()
    return redirect('/edit_chat')        

@views.route('/delete/<int:id>')
def delete(id):
    message_to_delete = Chat.query.get_or_404(id)

    try: 
        db.session.delete(message_to_delete)
        db.session.commit()
        return redirect('/history')
    except:
        return 'There was a problem deleting that message'

@views.route('/edit_delete/<int:id>')
def edit_delete(id):
    message_to_delete = edit_Chat.query.get_or_404(id)

    try: 
        db.session.delete(message_to_delete)
        db.session.commit()
        return redirect('/edit_chat')
    except:
        return 'There was a problem deleting that message'        

@views.route('/delete-note', methods=['POST'])
def delete_note():
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        db.session.delete(note)
        db.session.commit()

    return jsonify({})

# @views.route('/edit-note/<int:id>', methods=['POST'])
# def editNote(id):
#     message_to_edit = Chat.query.get_or_404(id)
#     edited_answer = request.input.value
#     if message_to_edit:
#         editchat = edit_Chat(request_text = message_to_edit.request_text, response_text = message_to_edit.response_text, edit_response_text = edited_answer) 
#         db.session.add(editchat)
#         db.session.commit()

#     return jsonify({})

# @views.route('/edit-chat/', methods=['POST'])
# def editChat():
#     chat = json.loads(request.data)
#     chatId = chat['chatId']
#     message_to_edit = Chat.query.get(chatId)
#     edited_answer = request.form.input.InnerText
#     if message_to_edit:
#         editchat = edit_Chat(request_text = message_to_edit.request_text, response_text = message_to_edit.response_text, edit_response_text = edited_answer, user_id=current_user.id) 
#         db.session.add(editchat)
#         db.session.commit()

#     return jsonify({})

@views.route('/update/<int:id>', methods=['POST', 'GET'])
def update(id):
    message_to_update = Chat.query.get_or_404(id)
    if request.method == "POST":
        try:
            edited_answer = request.form['Sam']
            editchat = edit_Chat(request_text = message_to_update.request_text, response_text = message_to_update.response_text, edit_response_text = edited_answer, user_id=current_user.id)
            db.session.add(editchat)
            db.session.commit()
            flash('Thank you for your feedback!', category='success')
            flash('Close the tab', category='success')
            return redirect('/history')
        except:
            return 'There was a problem editing that message'
    else:
        return render_template('update.html', message_to_update=message_to_update, user=current_user)

@views.route('/edit_update/<int:id>', methods=['POST', 'GET'])
def edit_update(id):
    message_to_update = edit_Chat.query.get_or_404(id)
    if request.method == "POST":
        try:
            edited_answer = request.form['Sam']
            editchat = edit_Chat(request_text = message_to_update.request_text, response_text = message_to_update.response_text, edit_response_text = edited_answer, user_id=current_user.id)
            db.session.add(editchat)
            db.session.commit()
            return redirect('/edit_chat')
        except:
            return 'There was a problem editing that message'
    else:
        return render_template('edit_update.html', message_to_update=message_to_update, user=current_user)