from flask import Blueprint, render_template, flash, redirect, request, url_for
from .competency import Competency
from .forms import AddCompetencyForm
from .dbmanager import get_db
from flask_login import current_user

bp = Blueprint("competencies", __name__, url_prefix = "/competencies/")

#Get All Competencies
@bp.route("/")
def get_competencies():
    competencies = []
    try:
        competencies = get_db().get_competencies(page_size=get_db().get_competency_count())[0]
    except:
        flash("An error occured while getting competency from the database.")
    
    return render_template("competencies_overview.html",  competencies=competencies)

#Get A Competency
@bp.route("/<competencyID>")
def get_competency(competencyID):
    
    try:
        competency = get_db().get_competency(competencyID)
        elements = get_db().get_competency_elements(competencyID)
    except:
        flash("An error occured while getting the competency from the database.")
        return redirect(url_for("competencies.get_competencies"))
        
    if competency == None:
        flash("competency could not be found.")
        return redirect(url_for("competencies.get_competencies"))
    else:
        return render_template("specific_competency.html", competency=competency, elements=elements)

#Adding A Competency
@bp.route("/new/", methods=["GET", "POST"])
def add_competency():
    form = AddCompetencyForm()
    
    if request.method == "POST" :
        if(form.validate_on_submit()):
            try:
                competency = Competency(form.competencyID.data, form.competencyName.data, form.competencyAchievement.data, form.competencyType.data)
                try:
                    get_db().add_competency(competency)
                except:
                    flash("An error occured while adding the competency to the database.")
                return redirect(url_for("competencies.get_competency", competencyID=competency.competencyID))
            except:
                flash("Invalid data for a competency.")
    
    return render_template("new_competency.html", form=form)

# Edit a competency
@bp.route("/edit/<competencyID>", methods=["GET", "POST"])
def edit_competency(competencyID):
    form = AddCompetencyForm()
    
    try:
        competency = get_db().get_competency(competencyID)
        elements = get_db().get_competency_elements(competencyID)
    except:
        flash("An error occured while getting the competency from the database.")
        return redirect(url_for("competencies.get_competencies"))
        
    if competency == None:
        flash("competency could not be found.")
        return redirect(url_for("competencies.get_competencies"))
    
    if request.method == "GET":
        form.competencyAchievement.data = competency.competencyAchievement
        form.competencyType.data = competency.competencyType
    
    if request.method == "POST" :
        if(form.validate_on_submit()):
            try:
                editedCompetency = Competency(form.competencyID.data, form.competencyName.data, form.competencyAchievement.data, form.competencyType.data)
                try:
                    get_db().update_competency(competencyID, editedCompetency)
                except:
                    flash("An error occured while adding the competency to the database.")
                return redirect(url_for("competencies.get_competency", competencyID=editedCompetency.competencyID))
            except:
                flash("Invalid data for a competency.")
    
    return render_template("edit_competency.html", competency=competency, elements=elements, form=form)

# Deletes a specific competency
@bp.route("/delete/<competencyID>")
def delete_competency(competencyID):
    
    try:
        get_db().delete_competency(competencyID)
    except:
        flash("An error occured while deleting the competency from the database.")
        return redirect(url_for("competencies.get_competency", competencyID=competencyID))
        
    return redirect(url_for("competencies.get_competencies"))