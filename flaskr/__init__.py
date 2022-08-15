import os
from flask import Flask, session
#from flask_sqlalchemy import SQLAlchemy
#from flask_session import Session
#from datetime import timedelta
def create_app(test_config = None):

	#create flask instance
	app = Flask(__name__, instance_relative_config=True)

	#app.config['SECRET_KEY'] = 'mysecret'
	#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flaskr.sqlite'
	#app.config['SESSION_TYPE'] = 'sqlalchemy'
	##app.permanent_session_lifetime = timedelta(days=7)
	#app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
	#cookie_db = SQLAlchemy(app)
	#app.config['SESSION_SQLALCHEMY'] = cookie_db

	#sess = Session(app)

	#cookie_db.create_all()

	app.config.from_mapping(
		SECRET_KEY="dev",
		DATABASE=os.path.join(app.instance_path, "flaskr.sqlite"),
		)
	if test_config is None:
		app.config.from_pyfile("config.py", silent=True)
	else:
		app.config.update(test_config)

	try:
		os.makedirs(app.instance_path)
	except OSError:
		pass

	@app.route("/hello")
	def hello():
		return "Hello, World!"

	#register db command
	from flaskr import db
	db.init_app(app)

	#apply blueprint
	from flaskr import auth,blog
	app.register_blueprint(auth.bp)
	app.register_blueprint(blog.bp)
	#homepage is blog.index
	app.add_url_rule("/",endpoint="index")

	return app