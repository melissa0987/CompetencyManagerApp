from flask import Blueprint, render_template, flash, redirect, request, url_for
from .domain import Domain
from .forms import AddDomainForm
from .dbmanager import get_db
from flask_login import current_user

bp = Blueprint("domains", __name__, url_prefix = "/domains/")

#Get All Domains
@bp.route("/")
def get_domains():
    domains = []
    try:
        domains = get_db().get_domains(page_size=get_db().get_domain_count())[0]
    except:
        flash("An error occured while getting domains from the database.")
    
    return render_template("domains_overview.html",  domains=domains)

#Get A Domain
@bp.route("/<int:domainID>")
def get_domain(domainID):
    
    try:
        domain = get_db().get_domain(domainID)
        courses = get_db().get_domain_courses(domainID)
    except:
        flash("An error occured while getting the domain from the database.")
        return redirect(url_for("domains.get_domains"))
        
    if domain == None:
        flash("Domain could not be found.")
        return redirect(url_for("domains.get_domains"))
    else:
        return render_template("specific_domain.html", domain=domain, courses=courses)

#Adding A Domain
@bp.route("/new/", methods=["GET", "POST"])
def add_domain():
    form = AddDomainForm()
    
    if request.method == "POST" :
        if(form.validate_on_submit()):
            try:
                domain = Domain(domainName=form.domainName.data, description=form.description.data)
                try:
                    domainID = get_db().add_domain(domain)
                except:
                    flash("An error occured while adding the domain to the database.")
                
                return redirect(url_for("domains.get_domain", domainID=domainID))
            except:
                flash("Invalid data for a domain.")
    
    return render_template("new_domain.html", form=form)

#Edit A Domain
@bp.route("/edit/<int:domainID>/", methods=["GET", "POST"])
def edit_domain(domainID):
    form = AddDomainForm()
    
    domain = get_db().get_domain(domainID)
    courses = get_db().get_domain_courses(domainID)
    
    if request.method == "GET":
        form.description.data = domain.description
    
    if request.method == "POST" :
        if(form.validate_on_submit()):
            try:
                editedDomain = Domain(form.domainName.data, form.description.data)
                try:
                    get_db().update_domain(domainID, editedDomain)
                except:
                    flash("An error occured while editing the domain in the database.")
                return redirect(url_for("domains.get_domain", domainID=domainID))
            except:
                flash("Invalid data for a domain.")
    
    return render_template("edit_domain.html", form=form, courses=courses, domain=domain)

#Delete A Specific Domain
@bp.route("/delete/<int:domainID>")
def delete_domain(domainID):
    
    try:
        get_db().delete_domain(domainID)
    except:
        flash("An error occured while deleting the domain from the database.")
        return redirect(url_for("domains.get_domain", domainID=domainID))
        
    return redirect(url_for("domains.get_domains"))