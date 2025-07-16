from flask import Blueprint, render_template, flash, redirect, request, url_for
from .element import Element
from .forms import AddElementForm, AddElementTaughtByCourseForm
from .dbmanager import get_db
from flask_login import current_user

bp = Blueprint("elements", __name__, url_prefix = "/elements/")

#Get An Element
@bp.route("/<int:elementID>")
def get_element(elementID):
    
    try:
        element = get_db().get_element(elementID)
        competency = get_db().get_element_competency(elementID)
        
        courses_elementHours = []
        for course in get_db().get_element_courses(elementID):
            courses_elementHours.append( (course, get_db().get_element_hours(elementID, course.courseID)) )
            
    except:
        flash("An error occured while getting the element from the database.")
        return redirect(url_for("competencies.get_competencies"))
    
    if element == None:
        flash("element could not be found.")
        return redirect(url_for("competencies.get_competencies"))
    else:
        return render_template("specific_element.html", element=element, competency=competency, courses_elementHours=courses_elementHours)
    
#Adding An Element
@bp.route("/new/<competencyID>", methods=["GET", "POST"])
def add_element(competencyID):
    form = AddElementForm()
    
    competenciesChoices = [] 
    for competency in get_db().get_competencies(page_size=get_db().get_competency_count())[0]:
        competenciesChoices.append((f"{competency.competencyID}", f"{competency}"))
    
    form.competency.choices = competenciesChoices
    
    if request.method == "GET":
        form.competency.data = competencyID
    
    if request.method == "POST" :
        if(form.validate_on_submit()):
            try:
                element = Element(elementOrder=form.elementOrder.data, elementName=form.elementName.data, elementCriteria=form.elementCriteria.data, competencyID=form.competency.data)
                try:
                    get_db().add_element(element)
                except:
                    flash("An error occured while adding the element to the database.")
                return redirect(url_for("competencies.get_competency", competencyID=element.competencyID))
            except:
                flash("Invalid data for an element.")
    
    return render_template("new_element.html", form=form, competencyID=competencyID)

#Edit an element
@bp.route("/edit/<int:elementID>", methods=["GET", "POST"])
def edit_element(elementID):
    form = AddElementForm()
    competenciesChoices = [] 
    for competency in get_db().get_competencies(page_size=get_db().get_competency_count())[0]:
        competenciesChoices.append((f"{competency.competencyID}", f"{competency}"))
    
    form.competency.choices = competenciesChoices
    
    try:
        element = get_db().get_element(elementID)
        courses_elementHours = []
        for course in get_db().get_element_courses(elementID):
            courses_elementHours.append( (course, get_db().get_element_hours(elementID, course.courseID)) )
    except:
        flash("An error occured while getting the element from the database.")
        return redirect(url_for("elements.get_element", elementID=elementID))
        
    if elementID == None:
        flash("Element could not be found.")
        return redirect(url_for("competencies.get_competencies"))
    
    if request.method == "GET":
        form.elementCriteria.data = element.elementCriteria
        form.competency.data = element.competencyID
    
    if request.method == "POST" :
        if(form.validate_on_submit()):
            try:
                editedElement = Element(elementOrder=form.elementOrder.data, elementName=form.elementName.data, elementCriteria=form.elementCriteria.data, competencyID=form.competency.data)
                try:
                    get_db().update_element(elementID, editedElement)
                except:
                    flash("An error occured while editing the element to the database.")
                return redirect(url_for("elements.get_element", elementID=elementID))
            except:
                flash("Invalid data for an element.")
    
    return render_template("edit_element.html", element=element, courses_elementHours=courses_elementHours, form=form)


#Delete A Specific Element
@bp.route("/delete/<int:elementID>")
def delete_element(elementID):
    
    try:
        get_db().delete_element(elementID)
    except:
        flash("An error occured while deleting the element from the database.")
        return redirect(url_for("elements.get_element", elementID=elementID))
        
    return redirect(url_for("competencies.get_competencies"))

#Add Element To A Course
@bp.route("/new-taught-by-course/<elementID>", methods=["GET", "POST"])
def add_course_teaching_element(elementID):
    
    form = AddElementTaughtByCourseForm()
    
    try:
        element = get_db().get_element(elementID)
        competency = get_db().get_element_competency(elementID)
    except:
        flash("An error occured while getting the element from the database.")
        return redirect(url_for("elements.get_element", elementID=elementID))
    
    courseChoices = [] 
    for course in get_db().get_courses(page_size=get_db().get_course_count())[0]:
        courseChoices.append((f"{course.courseID}", f"{course}"))
    
    form.courseID.choices = courseChoices
    
    if request.method == "POST" :
        if(form.validate_on_submit()):
            try:
                get_db().add_course_teaching_element(elementID, form.courseID.data, form.elementHours.data)
            except:
                flash("An error occured while adding the element teaching the course from the database.")
        return redirect(url_for("elements.get_element", elementID=elementID))
                
                
    return render_template("new_element_course.html", form=form, element=element, competency=competency)

#Delete Element From A Course
@bp.route("/delete/<int:elementID>/<courseID>")
def delete_element_teaching_course(elementID, courseID):
    
    try:
        get_db().delete_course_teaching_element(elementID, courseID)
    except:
        flash("An error occured while deleting the element teaching the course from the database.")
        
    return redirect(url_for("elements.get_element", elementID=elementID))

#Edit The Element Hours
@bp.route("/edit/<int:elementID>/<courseID>", methods=["GET", "POST"])
def edit_element_hours(elementID, courseID):
    
    form = AddElementTaughtByCourseForm()
    
    try:
        element = get_db().get_element(elementID)
        competency = get_db().get_element_competency(elementID)
        course = get_db().get_course(courseID)
        elementHours = get_db().get_element_hours(elementID, courseID)
    except:
        flash("An error occured while getting the element from the database.")
        return redirect(url_for("elements.get_element", elementID=elementID))
    
    courseChoice = [(f"{course.courseID}",f"{course}")]
    form.courseID.choices = courseChoice
    form.courseID.data = courseID
    
    if request.method == "POST" :
        if(form.validate_on_submit()):
            try:
                get_db().update_element_hours(elementID, courseID, form.elementHours.data)
            except:
                flash("An error occured while updating the element teaching the course from the database.")
        return redirect(url_for("elements.get_element", elementID=elementID))
                
                
    return render_template("edit_element_hours.html", form=form, element=element, competency=competency, course=course, elementHours=elementHours)
