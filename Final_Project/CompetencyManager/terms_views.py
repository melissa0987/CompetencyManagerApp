from flask import Blueprint, render_template, flash, redirect, request, url_for
from .term import Term
from .forms import AddTermForm
from .dbmanager import get_db
from flask_login import current_user

bp = Blueprint("terms", __name__, url_prefix = "/terms/")

#Get All Terms
@bp.route("/")
def get_terms():
    terms = []
    try:
        terms = get_db().get_terms(page_size=get_db().get_term_count())[0]
    except:
        flash("An error occured while getting terms from the database.")
    
    return render_template("terms_overview.html",  terms=terms)

#Get A Term
@bp.route("/<int:termID>")
def get_term(termID):
    
    try:
        term = get_db().get_term(termID)
        courses = get_db().get_term_courses(termID)
    except:
        flash("An error occured while getting the term from the database.")
        return redirect(url_for("terms.get_terms"))
        
    if term == None:
        flash("Term could not be found.")
        return redirect(url_for("terms.get_terms"))
    else:
        return render_template("specific_term.html", term=term, courses=courses)
    
#Adding A Term
@bp.route("/new/", methods=["GET", "POST"])
def add_term():
    form = AddTermForm()
    
    termIDs = []
    for term in get_db().get_terms(page_size = get_db().get_term_count())[0]:
        termIDs.append(term.termID)
    
    if request.method == "POST" :
        if(form.validate_on_submit()):
            try:
                term = Term(form.termID.data, form.termName.data)
                if term.termID in termIDs:
                    raise Exception()
                try:
                    get_db().add_term(term)
                except:
                    flash("An error occured while adding the term to the database.")
                return redirect(url_for("terms.get_term", termID=term.termID))
            except:
                flash("Invalid data for a term.")
    
    return render_template("new_term.html", form=form)

#Edit A Term
@bp.route("/edit/<int:termID>/", methods=["GET", "POST"])
def edit_term(termID):
    form = AddTermForm()
    
    term = get_db().get_term(termID)
    courses = get_db().get_term_courses(termID)
    
    if request.method == "GET":
        form.termName.data = term.termName
    
    if request.method == "POST" :
        if(form.validate_on_submit()):
            try:
                editedTerm = Term(form.termID.data, form.termName.data)
                try:
                    get_db().update_term(termID, editedTerm)
                except:
                    flash("An error occured while editing the term in the database.")
                return redirect(url_for("terms.get_term", termID=editedTerm.termID))
            except:
                flash("Invalid data for a term.")
    
    return render_template("edit_term.html", form=form, courses=courses, term=term)

#Delete A Term
@bp.route("/delete/<int:termID>")
def delete_term(termID):
    try:
        get_db().delete_term(termID)
    except:
        flash("An error occured while deleting the term from the database.")
        return redirect(url_for("terms.get_term", termID=termID))
        
    return redirect(url_for("terms.get_terms"))