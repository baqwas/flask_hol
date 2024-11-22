#!/usr/bin/env python3
"""
    db.py
    g is a special object that is unique for each request.
    It is used to store data that might be accessed by multiple functions during the request.
    The connection is stored and reused instead of creating a new connection if you
    get_db is called a second time in the same request.
    current_app is another special object that points to the Flask application handling
    the request. Since you used an application factory, there is no application object when
    writing the rest of your code. get_db will be called when the application has been
    created and is handling a request, so current_app can be used.
    sqlite3.connect() establishes a connection to the file pointed at by the
    DATABASE configuration key. This file doesn't have to exist yet, and won?t until
    you initialize the database later.
    sqlite3.Row tells the connection to return rows that behave like dicts.
    This allows accessing the columns by name.
    close_db checks if a connection was created by checking if g.db was set.
    If the connection exists, it is closed.
"""
import sqlite3
from datetime import datetime

import click
from flask import current_app, g


"""
get_db returns a database connection, which is used to execute the commands read from the file.
"""
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

# commands to run the schema data description language commands
def init_db():
    db = get_db()
    """
    opens a file relative to the flaskr package, since you won?t necessarily know where 
    that location is when deploying the application later. 
    """
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

"""
interpret timestamp values in the database. convert the value to a datetime.datetime.
"""
sqlite3.register_converter(
    "timestamp", lambda v: datetime.fromisoformat(v.decode())
)


# register close_db() and init_db()
def init_app(app):
    # tell Flask to call that function when cleaning up after returning the response.
    app.teardown_appcontext(close_db)
    # add a new command that can be called with the flask command
    app.cli.add_command(init_db_command)