from flask_login import UserMixin

class Member(UserMixin):
    def __init__(self, email, password, name, avatar_path, account_type, is_locked, id=None):
        if not isinstance(email, str):
            raise TypeError("Email must be a string")
        if not isinstance(name, str):
            raise TypeError("Name must be a string")
        if not isinstance(password, str):
            raise TypeError("Password must be a string")
        if not isinstance(is_locked, int):
            raise TypeError("The value of islocked must be an integer (0=False, 1=True)")
        if not isinstance(avatar_path, str):
            raise TypeError("Avatar path must be a string")
        if not isinstance(account_type, str):
            raise TypeError("Account type must be a string")
        
        self.email = email
        self.name = name
        self.password = password
        self.avatar_path = avatar_path
        self.account_type = account_type
        self.is_locked = is_locked
        self.id = id


from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import EmailField, PasswordField, StringField, BooleanField, TextAreaField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange, EqualTo
#Form to signup
class SignupForm(FlaskForm):
    email = EmailField('email')
    name = StringField('name')
    password = PasswordField('password', validators=[DataRequired()])
    avatar = FileField('Avatar', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Please upload a valid image file.')], render_kw={"accept": "image/*"})

#Form to login
class LoginForm(FlaskForm):
    email = EmailField('email')
    password = PasswordField('password')
    remember_me = BooleanField('remember me')

#Form to edit a user (for group administrator)
class EditUserForm(FlaskForm):
    name = StringField('Name:', validators=[DataRequired()])
    account_type = SelectField("Role: ", choices=[("MEMBER"), ("ADMIN_USER_GP"), ("ADMINISTRATOR_GP")])
    is_locked =  SelectField("Locked: ", choices=[(0, 'False'), (1, 'True')], coerce=int)
    
#Form to edit a user (for admin user)
class EditAsAdminUserForm(FlaskForm):
    name = StringField('Name:', validators=[DataRequired()])
    account_type = SelectField("Role: ", choices=[("MEMBER"), ("ADMIN_USER_GP")])
    is_locked =  SelectField("Locked: ", choices=[(0, 'False'), (1, 'True')], coerce=int)

#Form to change the password by the current user
class ChangeOwnPasswordForm(FlaskForm):
    old_password = PasswordField('Old Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), EqualTo('confirm_password', message='Passwords must match')])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired()])
    submit = SubmitField('Change Password')

#Form to change the password by both admins
class ChangeOtherPasswordForm(FlaskForm):
    new_password = PasswordField('New Password', validators=[DataRequired(), EqualTo('confirm_password', message='Passwords must match')])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired()])
    submit = SubmitField('Change Password')

#Form to add a user
class AddUser(FlaskForm):
    email = EmailField('email')
    name = StringField('name')
    password = PasswordField('password', validators=[DataRequired()])
    avatar = FileField('Avatar', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Please upload a valid image file.')], render_kw={"accept": "image/*"})
    account_type = SelectField("Role: ", choices=[("MEMBER"), ("ADMIN_USER_GP"), ("ADMINISTRATOR_GP")])
    is_locked =  SelectField("Locked: ", choices=[(0, 'False'), (1, 'True')], coerce=int)

#Form to change the avatar
class ChangeAvatar(FlaskForm):
    avatar = FileField('Avatar', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Please upload a valid image file.')], render_kw={"accept": "image/*"})
    submit = SubmitField('Update Avatar')