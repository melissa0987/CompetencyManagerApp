from flask import Blueprint, render_template, flash, redirect, request, url_for, request
from .course import Course
from .forms import AddCourseForm
from .dbmanager import get_db
from flask_login import current_user

bp = Blueprint("courses", __name__, url_prefix = "/courses/")

#Get All Courses
@bp.route("/")
def get_courses():
    courses = []
    courses = get_db().get_courses(page_size=get_db().get_course_count())[0]
    
    return render_template("courses_overview.html", courses=courses)

#Get A Course
@bp.route("/<courseID>/")
def get_course(courseID):
    
    try:
        course = get_db().get_course(courseID)
        term = get_db().get_course_term(courseID)
        domain = get_db().get_course_domain(courseID)
        competencies = get_db().get_course_competencies(courseID)
    except:
        flash("An error occured while getting the course from the database.")
        return redirect(url_for("courses.get_courses"))
        
    if course == None:
        flash("Course could not be found.")
        return redirect(url_for("courses.get_courses"))
    else:
        return render_template("specific_course.html", course=course, term=term, domain=domain, competencies=competencies)

#Adding A Course
@bp.route("/new/", methods=["GET", "POST"])
def add_course():
    form = AddCourseForm()
    
    domainChoices = [] 
    for domain in get_db().get_domains(page_size=get_db().get_domain_count())[0]:
        domainChoices.append((f"{domain.domainID}", f"{domain}"))
    
    termChoices = [] 
    for term in get_db().get_terms(page_size=get_db().get_term_count())[0]:
        termChoices.append((f"{term.termID}", f"{term}"))
    
    form.domain.choices = domainChoices
    form.term.choices = termChoices
    
    if request.method == "POST" :
        if(form.validate_on_submit()):
            try:
                course = Course(form.courseID.data, form.courseTitle.data, form.theoryHours.data, form.labHours.data, form.workHours.data, form.description.data, form.domain.data, form.term.data)
                try:
                    get_db().add_course(course)
                except:
                    flash("An error occured while adding the course to the database.")
                return redirect(url_for("courses.get_course", courseID=course.courseID))
            except:
                flash("Invalid data for a course.")
    
    return render_template("new_course.html", form=form)

#Edit A Course
@bp.route("/edit/<courseID>/", methods=["GET", "POST"])
def edit_course(courseID):
    form = AddCourseForm()
    
    course = get_db().get_course(courseID)
    competencies = get_db().get_course_competencies(courseID)
    
    domainChoices = [] 
    for domain in get_db().get_domains(page_size=get_db().get_domain_count())[0]:
        domainChoices.append((f"{domain.domainID}", f"{domain}"))
    
    termChoices = [] 
    for term in get_db().get_terms(page_size=get_db().get_term_count())[0]:
        termChoices.append((f"{term.termID}", f"{term}"))
    
    form.domain.choices = domainChoices
    form.term.choices = termChoices
    
    if request.method == "GET":
        form.description.data = course.description
        form.domain.data = course.domainID
        form.term.data = course.termID
    
    if request.method == "POST" :
        if(form.validate_on_submit()):
            try:
                editedCourse = Course(form.courseID.data, form.courseTitle.data, form.theoryHours.data, form.labHours.data, form.workHours.data, form.description.data, form.domain.data, form.term.data)
                try:
                    get_db().update_course(courseID, editedCourse)
                except:
                    flash("An error occured while editing the course to the database.")
                return redirect(url_for("courses.get_course", courseID=editedCourse.courseID))
            except:
                flash("Invalid data for a course.")
    
    return render_template("edit_course.html", form=form, course=course, competencies=competencies)

# Deleting A Course
@bp.route("/delete/<courseID>")
def delete_course(courseID):
    
    try:
        get_db().delete_course(courseID)
    except:
        flash("An error occured while deleting course from the database.")
        return redirect(url_for("courses.get_course", courseID=courseID))
        
    return redirect(url_for("courses.get_courses"))