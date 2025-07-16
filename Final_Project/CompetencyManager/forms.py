from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, TextAreaField, DecimalField
from wtforms.validators import DataRequired, NumberRange, Length
from .dbmanager import get_db

#Form to add a course
class AddCourseForm(FlaskForm):
    courseID = StringField("Course ID", validators=[DataRequired(), Length(10,10)])
    courseTitle = StringField("Title", validators=[DataRequired()])
    theoryHours = IntegerField("Theory Hours", validators=[NumberRange(0)])
    labHours = IntegerField("Laboratory Hours", validators=[NumberRange(0)])
    workHours = IntegerField("Homework Hours", validators=[NumberRange(0)])
    description = TextAreaField("Description", validators=[DataRequired()])
    domain = SelectField("Domain", validators=[DataRequired()])
    term = SelectField("Term", validators=[DataRequired()])
    
#Form to add a term
class AddTermForm(FlaskForm):
    termID = IntegerField("Term Number", validators=[NumberRange(1)])
    termName = SelectField("Term Name", choices=[("Fall", "Fall"),("Winter", "Winter")])
    
#Form to add a domain
class AddDomainForm(FlaskForm):
    domainName = StringField("Domain Name", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])
    
#Form to add an element
class AddElementForm(FlaskForm):
    elementOrder = IntegerField("Element Order", validators=[NumberRange(1)])
    elementName = StringField("Element Name", validators=[DataRequired()])
    elementCriteria = TextAreaField("Criteria", validators=[DataRequired()])
    competency = SelectField("Competency", validators=[DataRequired()])
    
#Form to add a competency
class AddCompetencyForm(FlaskForm):
    competencyID = StringField("Competency ID", validators=[DataRequired(), Length(4,4)])
    competencyName = StringField("Competency Name", validators=[DataRequired()])
    competencyAchievement = TextAreaField("Competency Achievement", validators=[DataRequired()])
    competencyType = SelectField("Competency Type", choices=[("Manditory", "Mandatory"),("Optional", "Optional")])
    
#Form to add an element to a given course
class AddElementTaughtByCourseForm(FlaskForm):
    courseID = SelectField("Course", validators=[DataRequired()])
    elementHours = DecimalField("Hours Teaching Element", validators=[NumberRange(0)])
    
#Form to search through all the entities
class SearchForm(FlaskForm):
    entity = SelectField("Desired Result", validators=[DataRequired()], choices=[("Courses", "Courses"),("Competencies", "Competencies"),("Elements", "Elements"),("Domains", "Domains")])
    query = StringField("Search", validators=[DataRequired()])