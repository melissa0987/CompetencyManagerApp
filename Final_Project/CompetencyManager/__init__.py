from datetime import timedelta
import secrets, os, click
from flask import Flask, render_template, current_app
from flask_login import LoginManager
from .dbmanager import get_db, close_db, init_db_command
from .courses_views import bp as courses_blueprint
from .domains_view import bp as domain_blueprint
from .terms_views import bp as term_blueprint
from .auth_views import bp as authentication_bp
from .elements_view import bp as element_bp
from .competencies_view import bp as competency_bp
from .home_view import bp as home_bp
from .rest_api.api_courses import bp as api_courses_bp
from .rest_api.api_elements import bp as api_elements_bp
from .rest_api.api_competencies import bp as api_competencies_bp
from .rest_api.api_terms import bp as api_terms_bp
from .rest_api.api_domains import bp as api_domains_bp
from .user_views import bp as user_bp

def create_app(test_config=None):

    app = Flask(__name__)

    app.config.from_mapping(
        SECRET_KEY=secrets.token_urlsafe(32),
        IMAGE_PATH= os.path.join(app.instance_path, 'images')
    )

    #for the remember me
    app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=7)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)


    login_manager = LoginManager()
    login_manager.login_view = 'authentication.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return get_db().get_user_by_id(int(user_id))

    
    with app.app_context():
        init_app(app)

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('page_not_found.html'), 404
    
    
    return app

def init_app(app):
    # tearing down previous things
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    # registering blueprints
    app.register_blueprint(authentication_bp)
    app.register_blueprint(courses_blueprint)
    app.register_blueprint(domain_blueprint)
    app.register_blueprint(term_blueprint)
    app.register_blueprint(element_bp)
    app.register_blueprint(competency_bp)
    app.register_blueprint(home_bp)
    app.register_blueprint(api_courses_bp)
    app.register_blueprint(api_elements_bp)
    app.register_blueprint(api_competencies_bp)
    app.register_blueprint(api_terms_bp)
    app.register_blueprint(api_domains_bp)
    app.register_blueprint(user_bp)

@click.command('my-command')
def click_command():
    get_db().run_file(os.path.join(os.path.join(current_app.root_path, 'sql'), 'setup.sql'))
    click.echo('Running schemal.sql')
