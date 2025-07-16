from flask import Blueprint, render_template, request
from .forms import SearchForm
from .dbmanager import get_db

bp = Blueprint('home', __name__, url_prefix='/')

#Home page
@bp.route('/', methods=["GET", "POST"])
def index():
    form = SearchForm()
    searchResults = []
    queryType = ""
    
    if request.method == "POST":
        queryType = form.entity.data
        if form.validate_on_submit():
            if queryType == "Courses":
                searchResults = get_db().search_courses(form.query.data)
            elif queryType == "Competencies":
                searchResults = get_db().search_competencies(form.query.data)
            elif queryType == "Elements":
                searchResults = get_db().search_elements(form.query.data)
            elif queryType == "Domains":
                searchResults = get_db().search_domains(form.query.data)
    
    return render_template('home.html', form=form, searchResults=searchResults, queryType=queryType)
