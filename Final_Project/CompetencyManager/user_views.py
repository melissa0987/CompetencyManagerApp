import os, shutil
from flask import Blueprint, current_app, redirect, request, flash, render_template, send_from_directory, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_required, login_user, logout_user, current_user
from .member import SignupForm, Member, EditUserForm, EditAsAdminUserForm, ChangeOwnPasswordForm, ChangeOtherPasswordForm, AddUser, ChangeAvatar
from .dbmanager import get_db

bp = Blueprint('users', __name__, url_prefix='/users/')

#avatar display
@bp.route('/avatars/<email>/avatar.png')
def show_avatar(email):
    path = os.path.join(current_app.config['IMAGE_PATH'], email)
    return send_from_directory(path, 'avatar.png')


#===========GET ===============
# fetches all users
@bp.route('/')
@login_required
def get_all_users():
    users = []
    try:
        users = get_db().get_all_users()
    except:
        flash("An error occured while getting all users from the database.")
    return render_template("users_overview.html",  users=users)


# get user methods for different account_tpe
@bp.route('/roles/<account_type>')
@login_required
def get_users_account_type(account_type): # gets all members
    users = []
    try:
        users = get_db().get_users_by_account_type(account_type)
    except:
        flash(f"An error occured while getting all users with {account_type} from the database.")
    return render_template("users_overview.html",  users=users)


#fetches a specific account by email
@bp.route('/<email>')
@login_required
def get_profile_by_email(email):
    user = []
    try:
        user = get_db().get_user(email)
    except:
        flash("An error occured while getting current user's profile from the database.")

    if user == None:
        flash("User could not be found.")
    
    return render_template("specific_user.html",  user=user)


#fetches a specific account by user_id
@bp.route("/<user_id>/")
@login_required
def get_profile(user_id):
    try:
        user = get_db().get_user_by_id(user_id)
    except:
        flash("An error occured while getting current user's profile from the database.")
    
    if user == None:
        flash("User could not be found.")
        return redirect(url_for("users.get_users_account_type", account_type=current_user.account_type))
    
    return render_template("specific_user.html",  user=user)



#for blocked users
@bp.route('/blocked-users')
@login_required
def get_blocked_users():
    if current_user.account_type != "MEMBER":
        users = []
        try:
            users = get_db().get_blocked_users()
        except:
            flash("An error occured while getting all blocked from the database.")
        return render_template("blocked_users.html",  users=users)
    
    flash("Not authorized to view blocked users")
    redirect(url_for("users.get_all_users", user=users))


# for editing 
@bp.route('/edit/<user_id>', methods=["GET", "POST"])
@login_required
def edit_user(user_id):

    user = get_db().get_user_by_id(user_id)
    
    if current_user.account_type == 'ADMIN_USER_GP':
        if user.account_type == 'ADMINISTRATOR_GP':
            flash(f"You lack authorization to edit user:({user.name}) account")
            return redirect(url_for("users.get_profile", user_id=user.id))
        form = EditAsAdminUserForm()
        if request.method == "GET":
            form.name.data = user.name
            form.account_type.data = user.account_type
            form.is_locked.data = user.is_locked
    else:
        form = EditUserForm()
        if request.method == "GET":
            form.name.data = user.name
            form.account_type.data = user.account_type
            form.is_locked.data = user.is_locked
        
    if request.method == "POST" :
        if(form.validate_on_submit()):
            new_name =  form.name.data 
            new_role = form.account_type.data
            new_status =  form.is_locked.data
                
            edited_user = Member(user.email, user.password, new_name, user.avatar_path, new_role, new_status)
            try:
                get_db().update_user(user_id, edited_user)
                flash(f"User({edited_user.name}) information has been updated.")
            except:
                flash("An error occurred while editing the user in the database.")
            return redirect(url_for("users.get_profile", user_id=user.id))
    
    return render_template("edit_user.html", form=form, user=user)



#method for changing password
@bp.route('/change-password/<user_id>', methods=['GET', 'POST'])
@login_required
def change_password(user_id):
    user = get_db().get_user_by_id(user_id)
    
    if current_user.email == user.email:
        form = ChangeOwnPasswordForm()
        if request.method == "POST":
            if form.validate_on_submit():
                old_password = form.old_password.data
                new_password = form.new_password.data
                confirm_password = form.confirm_password.data
                
                if old_password == new_password:
                    flash("Create a new password. Don't use old password combination!")
                    return redirect(url_for('users.change_password', user_id=user.id))
                
                #form validation pass
                edited_user = Member(user.email, generate_password_hash(new_password), user.name, user.avatar_path, user.account_type, user.is_locked)
                try:
                    get_db().update_user(user_id, edited_user)
                    flash(f"Your password was changed successfully.")
                except:
                    flash("An error occurred while saving the user's password to the database.")
                return redirect(url_for("users.get_profile", user_id=user.id))
            
            #form validation FAIL
            if not check_password_hash(current_user.password, form.old_password.data):
                flash('Incorrect password')
                return redirect(url_for('users.change_password', user_id=user.id))
            
            if form.new_password.data != form.confirm_password.data:
                flash("Password do not match. New password should matched")
                return redirect(url_for("users.change_password", user_id=user.id))
            
        return render_template('change_password.html', form=form, user=user)
    
    else:
        
        # ADMINISTRATOR_GP can change anyone's password
        if current_user.account_type == 'ADMINISTRATOR_GP':
            form = ChangeOtherPasswordForm()
            if request.method == "POST":
                if form.validate_on_submit():
                    new_password = form.new_password.data
                    confirm_password = form.confirm_password.data
                    
                    #form validation pass
                    edited_user = Member(user.email, generate_password_hash(new_password), user.name, user.avatar_path, user.account_type, user.is_locked)
                    try:
                        get_db().update_user(user_id, edited_user)
                        flash(f"User ({edited_user.name}) password was changed successfully.")
                    except:
                        flash("An error occurred while saving the user's password to the database.")
                    
                    return redirect(url_for("users.get_profile", user_id=user.id))
                
                #form validation FAIL
                if form.new_password.data != form.confirm_password.data:
                    flash("Password do not match. New password should matched")
                    return redirect(url_for("users.change_password", user_id=user.id))
                
            return render_template('change_password.html', form=form, user=user)
        
        
        if current_user.account_type == 'ADMIN_USER_GP':
            if user.account_type == 'MEMBER' :
                form = ChangeOtherPasswordForm()
                if request.method == "POST":
                    if form.validate_on_submit():
                        new_password = form.new_password.data
                        confirm_password = form.confirm_password.data
                        
                        #form validation pass
                        edited_user = Member(user.email, generate_password_hash(new_password), user.name, user.avatar_path, user.account_type, user.is_locked)
                        try:
                            get_db().update_user(user_id, edited_user)
                            flash(f"User ({edited_user.name}) password was changed successfully.")
                        except:
                            flash("An error occurred while saving the user's password to the database.")
                        return redirect(url_for("users.get_profile", user_id=user.id))
                    
                    #form validation FAIL
                    if form.new_password.data != form.confirm_password.data:
                        flash("Passwords do not match")
                        return redirect(url_for("users.change_password", user_id=user.id))
                    
                return render_template('change_password.html', form=form, user=user)
            
            # user.account_type == ADMINISTRATOR_GP, then ADMIN_USER_GP cannot modify administrators account
            else:
                flash("You are not authorized to change this user's passwords.")
                return redirect(url_for("users.get_profile", user_id=user.id))
  
  
# for deleting
@bp.route('/delete/<user_id>')
@login_required
def delete_user(user_id):
    user = get_db().get_user_by_id(user_id)
    
    if current_user.account_type == "ADMIN_USER_GP" and user.account_type == "ADMINISTRATOR_GP":
        flash(f"You lack authorization to delete user:({user.name}) account")
        return redirect(url_for("users.get_profile", user_id=user.id))
    
    try:
        get_db().delete_user(user.email)
    except:
        flash(f"An error occured while deleting user: {user.name} from the database.")
        return redirect(url_for("users.get_profile", user_id=user.id))
    
    flash(f"User:({user.name})'s information has been deleted from the database.")
    users = get_db().get_users_by_account_type(user.account_type) #gets all remaining users from db
    return render_template("users_overview.html",  users=users)
        

# for adding a new user 
# members cannot add 
# ADMIN_USER_GP are able to add new members
#ADMINISTRATOR_GP create new user with different roles
@bp.route('/users/add-user', methods=['GET', 'POST'])
@login_required
def add_new_user():
    if current_user.account_type == 'ADMINISTRATOR_GP':
        form = AddUser()
        if request.method == 'POST' and form.validate_on_submit():
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
                        #default image
                        default_avatar = os.path.join( os.getcwd(), 'CompetencyManager/images/avatar.png')
                        avatar_dir = os.path.join(current_app.config['IMAGE_PATH'], form.email.data)
                        avatar_path = os.path.join(avatar_dir, 'avatar.png')
                        if not os.path.exists(avatar_dir):
                            os.makedirs(avatar_dir) # create new folder
                        shutil.copy (default_avatar, avatar_path)
                        
                    hash = generate_password_hash(form.password.data)
                    member = Member(form.email.data, hash, form.name.data, avatar_path, form.account_type.data, form.is_locked.data)
                    get_db().add_user(member)
                    user = get_db().get_user(member.email)
                    if user is None:
                        flash("new user not saved")
                        return render_template('new_user.html', form=form)
                    flash(f"Successfully created user: {user.name}!")
                    return redirect(url_for("users.get_profile", user_id=user.id))
                    
        return render_template('new_user.html', form=form)
    
    elif current_user.account_type == 'ADMIN_USER_GP':
        form = SignupForm()
        if request.method == 'POST' and form.validate_on_submit():
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
                        #default image
                        default_avatar = os.path.join( os.getcwd(), 'CompetencyManager/images/avatar.png')
                        avatar_dir = os.path.join(current_app.config['IMAGE_PATH'], form.email.data)
                        avatar_path = os.path.join(avatar_dir, 'avatar.png')
                        if not os.path.exists(avatar_dir):
                            os.makedirs(avatar_dir) # create new folder
                        shutil.copy (default_avatar, avatar_path)
                        
                    hash = generate_password_hash(form.password.data)
                    member = Member(form.email.data, hash, form.name.data, avatar_path, account_type='MEMBER', is_locked=0)
                    get_db().add_user(member)
                    user = get_db().get_user(member.email)
                    if user is None:
                        flash("new user not saved")
                        return render_template('new_user.html', form=form)
                    flash(f"Successfully created user: {user.name}!")
                    return redirect(url_for("users.get_profile", user_id=user.id))
                    
        return render_template('new_user.html', form=form)
    else:
        flash("Not Authorize to add new user")
        redirect(url_for("users.get_all_users"))

        
#To change the avatar
@bp.route('/change-avatar/<user_id>',  methods=['GET', 'POST'])
@login_required
def change_avatar(user_id):
    user = get_db().get_user_by_id(user_id)
    if current_user.email == user.email:
        form = ChangeAvatar()

        if request.method == 'POST' and form.validate_on_submit():
            file = form.avatar.data
            if file:
                avatar_dir = os.path.join(current_app.config['IMAGE_PATH'], user.email)
                avatar_path = os.path.join(avatar_dir, 'avatar.png')
                    
                if not os.path.exists(avatar_dir):
                    os.makedirs(avatar_dir) # create new folder
                    
                if os.path.exists(avatar_path):
                    os.remove(avatar_path) #removes the old folder
                        
                file.save(avatar_path)
                    

            # edited_user = Member(user.email, user.password, user.name, avatar_path, user.account_type, user.is_locked)
            # get_db().update_user(user.id, user)
            flash("Avatar updated successfully!")
            return redirect(url_for('users.get_profile', user_id=user.id))
            
        return render_template('change_avatar.html', form=form, user_id=user.id)
    
    else:
        flash(f"You are not authorized to change this user's avatar")
        return redirect(url_for("users.get_profile", user_id=user.id))
