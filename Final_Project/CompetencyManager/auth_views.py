import os, shutil
from glob import escape
from flask import Blueprint, current_app, redirect, request, flash, render_template, send_from_directory, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_required, login_user, logout_user, current_user
from .member import SignupForm, LoginForm, Member, EditUserForm, EditAsAdminUserForm, ChangeOwnPasswordForm, ChangeOtherPasswordForm, AddUser
from .dbmanager import get_db

bp = Blueprint('authentication', __name__, url_prefix='/authentication/')

# To signup
@bp.route('/signup/', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            if get_db().get_user(form.email.data):
                flash("This user already exists")
            else:
                if form.avatar.data:
                    file = form.avatar.data
                    avatar_dir = os.path.join(current_app.config['IMAGE_PATH'], form.email.data)
                    avatar_path = os.path.join(avatar_dir, 'avatar.png')
                    if not os.path.exists(avatar_dir):
                        os.makedirs(avatar_dir)
                    file.save(avatar_path)
                else:
                    default_avatar = os.path.join( os.getcwd(), 'CompetencyManager/images/avatar.png')
                    avatar_dir = os.path.join(current_app.config['IMAGE_PATH'], form.email.data)
                    avatar_path = os.path.join(avatar_dir, 'avatar.png')
                    if not os.path.exists(avatar_dir):
                        os.makedirs(avatar_dir) # create new folder
                    shutil.copy (default_avatar, avatar_path)
                    
                hash = generate_password_hash(form.password.data)
                member = Member(form.email.data, hash, form.name.data, avatar_path, account_type='MEMBER', is_locked=0)
                get_db().add_user(member)
                flash("You have successfully signed up!")
                return redirect(url_for('authentication.login')) #redirects to login page
                
    return render_template('signup.html', form=form)


# To login
@bp.route('/login/', methods=['GET', 'POST'])
def login():
    add_instructor()
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            #check our user
            user = get_db().get_user(form.email.data)
            if user:
                #check the password
                if check_password_hash(user.password, form.password.data):
                    #user can login
                    login_user(user, form.remember_me.data)
                    # if the account is lock
                    if current_user.is_locked == 1:
                        flash("Your account is locked. Contact the one of the administrators to unlock your account ")
                        logout_user()
                    else:
                        return redirect(url_for('home.index')) #redirects to home page
                else:
                    flash("Login failed. You entered a wrong password")
            else:
                flash("Login failed. Not a registered member")
        else:
            flash("Cannot login")
    
    add_instructor()
    return render_template('login.html', form=form)

# To logout
@bp.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect(url_for('authentication.login'))


# Adds default user (instructor) to the database
def add_instructor():
    # avatar_path = os.path.join(current_app.config['IMAGE_PATH'], 'avatar.png')
    default_avatar = os.path.join( os.getcwd(), 'CompetencyManager/images/avatar.png')
    avatar_dir = os.path.join(current_app.config['IMAGE_PATH'], "instructor@gmail.com")
    avatar_path = os.path.join(avatar_dir, 'avatar.png')
    if not os.path.exists(avatar_dir):
        os.makedirs(avatar_dir) # create new folder
    shutil.copy (default_avatar, avatar_path)
    instructor = Member('instructor@gmail.com', generate_password_hash('Python420'), 'Instructor', avatar_path, account_type='ADMINISTRATOR_GP', is_locked=0)
    
    if get_db().get_user(instructor.email) == None:
        try:
            get_db().add_user(instructor)
        except ValueError:
            flash("An error occured")
    return instructor

    