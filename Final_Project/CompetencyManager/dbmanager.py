import click
import os
from flask import current_app, g
from .db import Database

#Get the database
def get_db():
    if "db" not in g:
        g.db = Database()
        
    return g.db

#Close the connection to the database
def close_db(_):
    db = g.pop("db", None)
    if db is not None:
        db.close()

#Initialize the database
def init_db():
    get_db().run_file(f"{os.path.join(os.path.join(current_app.root_path, 'sql'), 'setup.sql')}")
    
#Initialize the database with a message
@click.command('init-db')
def init_db_command():
    init_db()
    click.echo("Initialised the database.")