from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from .models import UserForm
import os
from .pdf_extractor import *
from werkzeug.utils import secure_filename
import os
from .models import UserCV
from flask_jwt_extended import create_access_token
from flask_login import current_user, login_required
from flask import jsonify
from datetime import timedelta
from flask_jwt_extended import jwt_required, get_jwt_identity

auth = Blueprint('auth', __name__)

import os




@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.survey'))


@auth.route('/survey', methods=['GET', 'POST'])
def survey():
    if request.method == 'POST':
        name = request.form.get('name')
        age = request.form.get('Age')
        gender = request.form.get('gender') #try Gender for label, gender for input
        profession = request.form.get('profession')
        email = request.form.get('email')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 5:
            flash('Password must be at least 5 characters.', category='error')
        else:
            new_user = User(email=email, name=name, age=age, gender=gender, profession=profession, password=generate_password_hash(
                password1, method='sha256'))
            
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash(f'Hello {name}, welcome!', category='success')
            return redirect(url_for('auth.cv_choice'))

    return render_template("survey.html", user=current_user)


@auth.route('/user-form', methods=['GET', 'POST'])
@login_required
def user_form():
    if request.method == 'POST':
        education = request.form.get('education')
        skills = request.form.get('skills')
        experiences = request.form.get('experiences')

        # Delete the older entries for this user if they exist
        old_data = UserForm.query.filter_by(user_id=current_user.id).all()
        if old_data:
            for entry in old_data:
                db.session.delete(entry)
            db.session.commit()


        # Add the new form data
        form_data = UserForm(education=education, skills=skills, experiences=experiences, user_id=current_user.id)

        db.session.add(form_data)
        db.session.commit()

        flash(f'Thank you for updating the form {current_user.name}!', category='success')
        return redirect(url_for('views.home'))

    return render_template("user_form.html", user=current_user)




@auth.route('/cv-choice', methods=['GET', 'POST'])
@login_required
def cv_choice():
    if request.method == 'POST':
        cv_input_type = request.form.get('cv_input_type')
        if cv_input_type == 'manual':
            return redirect(url_for('auth.user_form'))
        elif cv_input_type == 'upload':
            return redirect(url_for('auth.upload_cv'))
        else:
            flash('Invalid choice. Please try again.', category='error')
    return render_template("cv_choice.html", user=current_user)

# @auth.route('/upload-cv', methods=['GET', 'POST'])
# @jwt_required(optional=True)
# def upload_cv():
#     upload_folder = 'uploads/'
#     if not os.path.exists(upload_folder):
#         os.makedirs(upload_folder)
#     if request.method == 'POST':
#         if request.content_type == 'application/json':
#             cv_file_path = request.get_json().get('cv_pdf')
#             if cv_file_path and os.path.exists(cv_file_path):
#                 cv_file = open(cv_file_path, 'rb')
#             current_user_id = get_jwt_identity()
#             filename = request.get_json().get('filename')
#         else:
#             cv_file = request.files.get('cv_pdf')
#             current_user_id = current_user.id
#         if cv_file:
#             if filename is None:
#                 filename = secure_filename(cv_file.filename)
#             else:
#                 filename = secure_filename(filename)
#             print(filename)
#             cv_file.save(os.path.join('uploads/', filename))
#             success = extract_cv_details_and_store("uploads/"+filename, current_user_id)  
#             os.remove(os.path.join('uploads/', filename))  # Delete the file after extraction
#             if not request.content_type == 'application/json':
#                 if not success:
#                     flash('An error occurred during CV extraction. Please try to enter manually', category='error')
#                     return redirect(url_for('auth.user_form'))
#                 else:
#                     flash('CV details successfully stored!', category='success')
#                     return redirect(url_for('views.home'))
#     return render_template("upload_cv.html", user=current_user)

@auth.route('/upload-cv', methods=['GET', 'POST'])
@jwt_required(optional=True)
def upload_cv():
    upload_folder = 'uploads/'
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    
    if request.method == 'POST':
        current_user_id = None
        file_path = None
        success = False

        if request.content_type == 'application/json':
            json_data = request.get_json()
            file_path = json_data.get('cv_pdf')
            filename = json_data.get('filename')
            
            if file_path and os.path.exists(file_path):
                # Validate and sanitize the file_path here
                current_user_id = get_jwt_identity()
                if filename is None:
                    filename = os.path.basename(file_path)
                filename = secure_filename(filename)
                # Process the file at file_path
                success = extract_cv_details_and_store(file_path, current_user_id)
            else:
                return jsonify({'error': 'Invalid file path'}), 400

        else:  # Handling form-data file upload
            cv_file = request.files.get('cv_pdf')
            if cv_file:
                current_user_id = current_user.id
                filename = secure_filename(cv_file.filename)
                file_path = os.path.join(upload_folder, filename)
                cv_file.save(file_path)
                success = extract_cv_details_and_store(file_path, current_user_id)
                os.remove(file_path)  # Delete the file after extraction

        if not request.content_type == 'application/json':
            if not success:
                flash('An error occurred during CV extraction. Please try to enter manually', category='error')
                return redirect(url_for('auth.user_form'))
            else:
                flash('CV details successfully stored!', category='success')
                return redirect(url_for('views.home'))

    return render_template("upload_cv.html", user=current_user)



# @auth.route('/home-new', methods=['GET', 'POST'])
# def home_new():
#     return render_template('home.html')

@auth.route('/delete-cv-manual', methods=['GET', 'POST'])
@login_required
def delete_cv_manual():
    # Delete the older entries for UserForm
    old_data = UserForm.query.filter_by(user_id=current_user.id).all()
    if old_data:
        for entry in old_data:
            db.session.delete(entry)
        db.session.commit()


    flash('Manual CV details deleted successfully!', category='success')
    return redirect(url_for('views.home'))



@auth.route('/delete-cv-pdf', methods=['GET', 'POST'])
@login_required
def delete_cv_pdf():

    # Delete older entries for UserCV
    old_cvs = UserCV.query.filter_by(user_id=current_user.id).all()
    if old_cvs:
        for cv in old_cvs:
            db.session.delete(cv)
        db.session.commit()


    flash('CV Pdf details deleted successfully!', category='success')
    return redirect(url_for('views.home'))

@auth.route('/generate_token')
@login_required
def generate_token():
    # Set the expiration time to 1 year (365 days)
    expires = timedelta(days=365)
    access_token = create_access_token(identity=current_user.id, expires_delta=expires)
    return jsonify(access_token=access_token)