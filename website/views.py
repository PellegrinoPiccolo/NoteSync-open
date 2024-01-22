from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, render_template_string
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import Note
from .models import User
from .models import Group
from .models import Folder
from . import db
import json
from sqlalchemy import delete
from .validate import *

views = Blueprint('views', __name__)

@views.route('/')
def home():
    return render_template("home.html")

@views.route('/my-notes')
@login_required
def notes():
    return render_template("notes.html")

@views.route('/new-note', methods=['GET','POST'])
@login_required
def new_note():
    if request.method == 'GET':
        groupId = request.args.get('groupId')
        folderId = request.args.get('folderId')
        return render_template("new_note.html", groupId = groupId, folderId = folderId)
    if request.method == 'POST':
        title = request.form.get('title')
        data = request.form.get('data')
        group = request.form.get('group')
        folderId = request.form.get('folderId')
        groupId = request.form.get('groupId')
        if len(title) < 1 or len(data) < 1:
            flash("Title or text of note must be greater 1 character", category='error')
            flash(data, 'text')
            return redirect(url_for('views.new_note'))
        else:
            format_data = render_template_string(data)
            new_note = Note(title=title, data=format_data, user_id=current_user.id, group_id=groupId if groupId != "None" else None, folder_id=folderId if folderId != "None" else None)
            db.session.add(new_note)
            db.session.commit()
            if new_note and folderId != "None":
                flash("Note created!", category='success')
                return redirect(f'/folder/{folderId}')
            elif new_note and groupId == "None":
                flash("Note created!", category='success')
                return redirect(url_for('views.notes'))
            elif new_note and groupId:
                flash("Note created!", category='success')
                return redirect(f'/group/{groupId}')
            else:
                flash("Note not created", category='error')
                return redirect(url_for('views.notes'))
    return render_template("new_note.html")

@views.route('/delete-note', methods=['POST'])
@login_required
def delete_note():
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()
            flash("Note eliminated!",category='success')
        else:
            flash("Error on remove note", category='error')
    else:
        flash("Note doesn't exists", category='error')
    return jsonify({})

@views.route('/code-github')
def code_github():
    return render_template("code_github.html")

@views.route('/account-setting', methods=['GET','POST'])
@login_required
def account_setting():
    if request.method == 'POST':
        if request.form.get('firstName'):
            firstName = request.form.get('firstName')
            if len(firstName) < 1:
                flash('The first name must be greate than 1 character', category='error')
                return redirect(url_for('views.account_setting'))
            else:
                user = User.query.get(current_user.id)
                user.first_name = firstName
                db.session.commit()
                flash('Fist name changed!', category='success')
                return redirect(url_for('views.account_setting'))
        elif request.form.get('email'):
            email = request.form.get('email')
            user = User.query.filter_by(email = email).first()
            if user:
                flash('Email already exists', category='error')
                return redirect(url_for('views.account_setting'))
            else:
                new_email_user = User.query.get(current_user.id)
                new_email_user.email = email
                db.session.commit()
                flash('Email changed!', category='success')
                return redirect(url_for('views.account_setting'))
        elif request.form.get('password'):
            current_password = request.form.get('current_password')
            password = request.form.get('password')
            password2 = request.form.get('password2')
            if password != password2:
                flash('Passwords don\'t match', category='error')
                return redirect(url_for('views.account_setting'))
            elif len(password) < 7:
                flash('Password must be greater than 7 characters', category='error')
                return redirect(url_for('views.account_setting'))
            else:
                user = User.query.get(current_user.id)
                if check_password_hash(user.password, current_password):
                    user.password = generate_password_hash(password, method="pbkdf2:sha256")
                    db.session.commit()
                    flash('Password changed', category='success')
                    return redirect(url_for('views.account_setting'))
                else:
                    flash('The current password isn\'t correct', category='error')
                    return redirect(url_for('views.account_setting'))
        elif request.form.get('password_for_delete'):
            password = request.form.get('password_for_delete')
            password2 = request.form.get('confirm_password_for_delete_account')
            if password == password2:
                if check_password_hash(current_user.password, password):
                    user = User.query.get(current_user.id)
                    group_to_delete = list(user.groups)
                    for group in user.groups:
                        if group.creator.id == user.id:
                            for users in group.users:
                                users.groups.remove(group)
                            db.session.commit()
                            db.session.execute(delete(Group).where(Group.id == group.id))
                            db.session.commit()
                        else:
                            user.groups.remove(group)
                        db.session.commit()
                    db.session.delete(user)
                    db.session.commit()
                    flash('Account deleted', category='success')
                    return redirect(url_for('auth.sign_up'))
                else:
                    flash('Password not correct', category='error')
            else:
                flash('Password doesn\'t match', category='error')
                
    return render_template("account_setting.html")

@views.route('/mod-note/<int:noteId>', methods=['GET','POST'])
@login_required
def mod_note(noteId):
    if request.method != "POST":
        note = Note.query.get(noteId)
        if note and note.user_id == current_user.id:
            return render_template("mod_note.html", note=note)
        else:
            flash("Error with selected note", category='error')
    elif request.method == 'POST':
        noteId = request.form.get('noteId')
        title = request.form.get('title')
        text = request.form.get('data')
        if len(title) < 1:
            flash('Title must be greate than 1 character', category='error')
            flash(text, category='text')
            return redirect(f'/mod-note/{noteId}')
        else:
            note = Note.query.get(noteId)
            if note:
                note.title = title
                note.data = render_template_string(text)
                db.session.commit()
                flash('Note modificated', category='success')
                return redirect(f'/read-note/{noteId}')
            else:
                flash('Errore to search note', category='error')
    return redirect(url_for('views.notes'))

@views.route('/read-note/<int:noteId>', methods=['GET'])
@login_required
def read_note(noteId):
    note = Note.query.get(noteId)
    if note and note.user_id == current_user.id:
        return render_template("read_note.html", note=note)
    else:
        flash('Error with selected note', category='error')
    return redirect(url_for('views.notes'))

@views.route('/my-groups')
@login_required
def my_groups():
    return render_template('my_groups.html')

@views.route('/new-group', methods=['GET','POST'])
@login_required
def new_group():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        password = request.form.get('password')
        password2 = request.form.get('password2')
        if len(name) < 1:
            flash('The name of group are must be greater than 1 character', category='error')
            flash(description, category='text')
            return redirect(url_for('views.new_group'))
        elif len(description) > 400:
            flash('The descript don\'t must be greater than 400 characters', category='error')
            flash(description, category='text')
            return redirect(url_for('views.new_group'))
        elif not is_valid_password(password):
            flash('Password must be at least 8 characters long and meet the following criteria:\n \
                       Contain at least one lowercase letter,\n \
                       Contain at least one uppercase letter,\n \
                       Contain at least one digit,\n \
                       Contain at least one special character.',category='error')
            flash(description, category='text')
            return redirect(url_for('views.new_group'))
        elif password != password2:
            flash('Passwords don\'t match', category='error')
            flash(description, category='error')
            return redirect(url_for('views.new_group'))
        else:
            new_group = Group(name=name, description=description, password=generate_password_hash(password, method="pbkdf2:sha256"), creator_id=current_user.id)
            db.session.add(new_group)
            new_group.users.append(current_user)
            db.session.commit()
            if new_group:
                flash('Group created!', category='success')
                return redirect(url_for('views.my_groups'))
            else:
                flash('Error with creation of group', category='error')
    return render_template('new_group.html')

@views.route('/delete-group', methods=['POST'])
@login_required
def delete_group():
    if request.method == 'POST':
        group = json.loads(request.data)
        groupId = group['groupId']
        group = Group.query.get(groupId)
        if group:
            if group.creator.id == current_user.id:
                notes = Note.query.filter_by(group_id=group.id).all()
                if notes:
                    for note in notes:
                        db.session.delete(note)
                    db.session.commit()
                for user in group.users:
                    user.groups.remove(group)
                db.session.commit()
                db.session.delete(group)
                db.session.commit()
                flash('Group eliminated', category='success')
            else:
                flash('Error with permission', category='error')
        else:
            flash('Error with search of group', category='error')
    return jsonify({})

@views.route('/mod-group/<int:groupId>', methods=['GET','POST'])
@login_required
def mod_group(groupId):
    if request.method != "POST":
        group = Group.query.get(groupId)
        if group and group.creator.id == current_user.id:
            return render_template("mod_group.html", group=group)
        else:
            flash('Error with selection group', category='error')
    elif request.method == 'POST':
        try:
            name = request.form.get('name')
            description = request.form.get('description')
            groupId = request.form.get('groupId')
            if len(name) < 1:
                flash('Name must be greater than 1 character', category='error')
                flash(description, category='text')
                return redirect(f'/mod-group/{groupId}')
            else:
                group = Group.query.get(groupId)
                if group:
                    group.name = name
                    group.description = description
                    db.session.commit()
                    flash('Group modificated', category='success')
                    flash(description, category='text')
                    return redirect(f'/mod-group/{groupId}')
        except Exception as e:
            current_password = request.form.get('current_password')
            password = request.form.get('password')
            password2 = request.form.get('password2')
            groupId = request.form.get('groupId')
            group = Group.query.get(groupId)
            if group and check_password_hash(group.password, current_password):
                if len(password) < 7:
                    flash('Password must be greater than 7 characters', category='error')
                    return redirect(f'/mod-group/{groupId}')
                elif password != password2:
                    flash('Passwords not match', category='error')
                    return redirect(f'/mod-group/{groupId}')
                else:
                    group.password = generate_password_hash(password, method="pbkdf2:sha256")
                    db.session.commit()
                    flash('Password changed', category='success')
                    return redirect(f'/mod-group/{groupId}')
            else:
                flash('Current password not correct', category='error')
                return redirect(f'/mod-group/{groupId}')
    return render_template("my_groups.html")

@views.route('/group/<int:groupId>', methods=['GET'])
@login_required
def group(groupId):
    group = Group.query.get(groupId)
    if group and current_user in group.users:
        return render_template("group.html", group=group)
    else:
        flash("Error to access in this group", category='error')
        return redirect(url_for('views.my_groups'))

@views.route('/enter-group', methods=['GET','POST'])
@login_required
def enter_group():
    if request.method == 'POST':
        groupId = request.form.get('groupId')
        password = request.form.get('password')
        group = Group.query.get(groupId)
        if group:
            if check_password_hash(group.password, password):
                current_user.groups.append(group)
                db.session.commit()
                flash(f'Join in {group.name}', category='success')
                return redirect(url_for('views.my_groups'))
            else:
                flash('Password not correct', category='error')
        else:
            flash('Group doesn\'t exists', category='error')
    return render_template("enter_group.html")

@views.route('/leave-group', methods=['POST'])
@login_required
def leave_group():
    if request.method == 'POST':
        group = json.loads(request.data)
        groupId = group['groupId']
        group = Group.query.get(groupId)
        if group:
            current_user.groups.remove(group)
            db.session.commit()
            flash("Leaved group", category='success')
        else:
            flash('Errore with leaving group', category='error')
    else:
        flash("No request method", category='error')
    return jsonify({})

@views.route("/members-group/<int:groupId>", methods=['GET'])
@login_required
def members_group(groupId):
    group = Group.query.get(groupId)
    if group and current_user in group.users:
        return render_template("members_group.html", group=group)
    else:
        flash("Error with selection of group", category='error')
        return redirect(url_for('views.my_groups'))

@views.route("/remove-user", methods=['POST'])
@login_required
def remove_user():
    if request.method == 'POST':
        group = json.loads(request.data)
        groupId = group['groupId']
        userId = group['userId']
        group = Group.query.get(groupId)
        user = User.query.get(userId)
        if group and group.creator_id == current_user.id and user and user in group.users:
            user.groups.remove(group)
            db.session.commit()
            flash(f'User: {user.first_name} has been removed from the group', category='success')
        else:
            flash('Error with user removal', category='error')
    return jsonify({})

@views.route("/new-folder", methods=['GET', 'POST'])
@login_required
def new_folder():
    if request.method == 'GET':
        groupId = request.args.get('groupId')
        folderId = request.args.get('folderId')
        return render_template("new_folder.html", groupId = groupId, folderId = folderId)
    else:
        name = request.form.get('name_folder')
        folderId = request.form.get('folderId')
        try:
            groupId = request.form.get('groupId')
        except Exception as e:
            flash("Error with creation of folder", category="error")
            return redirect(url_for("views.notes"))
        if len(name) < 1:
            flash("The name of the folder must be greater than 1 characters", category="error")
            return redirect(f"new-folder/{groupId}")
        if groupId == "None":
            new_folder = Folder(name=name, creator_id=current_user.id, group_id=None, folder_id=None if folderId == "None" else folderId)
            db.session.add(new_folder)
            db.session.commit()
            if folderId != "None":
                flash("Folder created", category='success')
                return redirect(f'/folder/{folderId}')
            else:
                flash("Folder created", category="success")
                return redirect(url_for("views.notes"))
        else:
            group = Group.query.get(groupId)
            if current_user and group in current_user.groups:
                new_folder = Folder(name=name, creator_id=current_user.id, group_id=groupId, folder_id=folderId)
                db.session.add(new_folder)
                db.session.commit()
                flash("Folder created", category="success")
                return redirect(f"group/{groupId}")
            else:
                flash("Error with permission", category="error")
                return redirect(url_for("views.notes"))
    return render_template("new_folder.html")

@views.route("/folder/<int:folder_id>")
@login_required
def view_folder(folder_id):
    folder = Folder.query.get(folder_id)
    if folder:
        if (folder.creator_id == current_user.id) or (current_user and folder.group in current_user.groups):
            return render_template("view_folder.html", folder = folder)
        else:
            flash("Error with permission", category="error")
            return redirect(url_for("views.notes"))
    else:
        flash("Folder not exists", category="error")
        return redirect(url_for("views.notes"))
    
@views.route("/delete-folder", methods=['POST'])
@login_required
def delete_folder():
    if request.method == "POST":
        folder = json.loads(request.data)
        folderId = folder['folderId']
        folder = Folder.query.get(folderId)
        if folder.creator_id == current_user.id:
            db.session.delete(folder)
            db.session.commit()
            flash("Folder eliminated", category="success")
        else:
            flash("Error with permission", category="error")
    return jsonify({})

@views.route("/mod-folder/<int:folderId>", methods=['GET','POST'])
@login_required
def mod_folder(folderId):
    if request.method != "POST":
        folder = Folder.query.get(folderId)
        if folder and folder.creator_id == current_user.id:
            return render_template("mod_folder.html", folder = folder)
        else:
            flash("Error with permission", category='error')
            return redirect(url_for("views.notes"))
    elif request.method == "POST":
        name = request.form.get("name_folder")
        folderId = request.form.get("folderId")
        folder = Folder.query.get(folderId)
        if folder:
            if len(name) < 1:
                flash("The name of the folder must be greater than 1 character", category='error')
                return render_template("mod_folder.html", folder = folder)
            else:
                folder.name = name
                db.session.commit()
                flash("Name changed", category='success')
                return redirect(f"/folder/{folderId}")
    else:
        return redirect(url_for("views.notes"))