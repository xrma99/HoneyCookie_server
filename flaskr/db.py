import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
	#g is a special object that is unique for each request. It is used to store data that might be accessed by multiple functions during the request. The connection is stored and reused instead of creating a new connection if get_db is called a second time in the same request.

	if 'db' not in g:
		g.db = sqlite3.connect(
			current_app.config['DATABASE'],
			detect_types=sqlite3.PARSE_DECLTYPES
			)
		g.db.row_factory = sqlite3.Row

	return g.db

def close_db(e=None):
	#If this request connected to the database, close the connection.
	db = g.pop('db',None)

	if db is not None:
		db.close()

def init_db():
	db = get_db()
	with current_app.open_resource("schema.sql") as f:
		db.executescript(f.read().decode("utf8"))

@click.command("init-db")
@with_appcontext
def init_db_command():
	init_db()
	click.echo('Initialized the databases.')

def init_app(app):
	#register the functions in the application
	app.teardown_appcontext(close_db)
	app.cli.add_command(init_db_command)

