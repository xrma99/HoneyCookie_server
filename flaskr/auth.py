import functools

from flask import(
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db
from time import time
import os

bp = Blueprint('auth',__name__,url_prefix='/auth')

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))
        return view(**kwargs)

    return wrapped_view

def attacker_measures(user_name,time):
    f = open("attackerInfo.txt","a+")
    tmp_str = str(request.remote_addr) +':'+ str(request.environ.get('REMOTE_PORT'))
    f.write(tmp_str+'\n')
    f.close()

    db = get_db()

    db.execute(
        "INSERT INTO fakeuser (username, password,legal) VALUES (?,?,?)",(user_name,generate_password_hash(tmp_str),0)
        )#sql command
    db.commit()

    user_id = db.execute(
        "SELECT id FROM fakeuser WHERE username = ? and legal = ?",(user_name,0)
        ).fetchone()
    user_id = user_id['id']

    db.execute(
        "INSERT OR REPLACE INTO cookie (user_id, user_name,honey_security, content, legal) VALUES (? , ?, ?, ?,?)",(user_id,user_name,time,"Attacker",0)
        )  # sql command
    db.commit()

    # cwd = os.getcwd()
    dirpath = "flaskr/fakeblogs/"
    dir_list = os.listdir(dirpath)
    for item in dir_list:
        f = open(dirpath+item,'r')
        body = f.readline()#temporay read one line
        title = item[:len(item)-4]
        db.execute(
            "INSERT INTO fakeblogs (title, body, author_id) VALUES (?,?,?)",(title,body,user_id)
            )
        db.commit()
        f.close()
        print("fake")

    g.user = get_db().execute(
        'SELECT * FROM fakeuser WHERE username = ? and legal = ?', (user_name,0)
    ).fetchone()
    g.posts = db.execute(
        'SELECT f.id, title, body, created, author_id, username '
        'FROM fakeblogs f JOIN fakeuser u ON f.author_id = u.id '
        'WHERE author_id = ?',(g.user['id'],)
    ).fetchall()


#runs before the view functions
@bp.before_app_request
def load_logged_in_user():
    #print(session.get('user_id'))
    user_name = request.cookies.get("username")
    time = request.cookies.get("honey_security")

    #user_id = session.get('user_id')
    #user_name = session.get('user_name')
    flag = 0
    #time = session.get('time_established')

    isAttacker = 0

    if user_name is None or time is None:
        g.user = None
    else:
        print("User Name: "+user_name)
        #Honey cookie here!!!!!!!

        db = get_db()

        lines = db.execute(
            'SELECT * FROM cookie WHERE user_name = ?', (user_name,)
        ).fetchall()
        
        if len(lines)==0: # No session for this user
            isAttacker = 1
        else:
            #time = session.get('time_established')
            
            for line in lines:
                if(line['honey_security']==time and line['user_name']==user_name):
                    print("success")
                    if line['legal']==1:
                        g.user = get_db().execute(
                            'SELECT * FROM user WHERE username = ?', (user_name,)
                        ).fetchone()

                        flag = 1
                        g.posts = db.execute(
                            'SELECT p.id, title, body, created, author_id, username '
                            'FROM post p JOIN user u ON p.author_id = u.id '
                            'WHERE author_id = ?',(g.user['id'],)
                        ).fetchall()
                    else:#this is an old attacker
                        print("old attacker")
                        g.user = get_db().execute(
                            'SELECT * FROM fakeuser WHERE username = ?', (user_name,)
                        ).fetchone()
                        print(g.user['id'])

                        flag = 1
                        g.posts = get_db().execute(
                            'SELECT f.id, title, body, created, author_id, username '
                            'FROM fakeblogs f JOIN fakeuser u ON f.author_id = u.id '
                            'WHERE author_id = ?',(g.user['id'],)
                        ).fetchall()
                        for post in g.posts:
                            print(post['title'])

                    
                    break
            if (flag==0):
                isAttacker = 1

        if(isAttacker == 1):#this is a new attacker
            attacker_measures(user_name,time)



#associate url /register with the register view function
# request to /auth/register would call this function
@bp.route('/register',methods=('GET','POST'))
def register():
    #POST method: registerer input register info
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = "username is required"
        elif not password:
            error = "password is required"
        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password,legal) VALUES (?,?,?)",(username,generate_password_hash(password),1)
                    )#sql command
                db.commit()

            except db.IntegrityError:
                error = f"User {username} is already registered"
            
            else:
                #successfully register, redirect to login page
                return redirect(url_for("auth.login"))
                #auth.login means login function in the Blueprint auth
        
        flash(error)
    print("get is called")
    # GET mothod: return register page
    return render_template('auth/register.html')

@bp.route('login',methods = ('GET','POST'))
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        #return one row from the query
        #if no user, return None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?',(username,)
        ).fetchone()
        if user is None:
            error = 'user name not exist'
        elif not check_password_hash(user['password'],password):
            error = 'incorrect password'
        
        if error is None:
            # session is a dict that stores data across requests.
            # When validation succeeds, the user’s id is stored in a new session.
            # The data is stored in a cookie that is sent to the browser, and the browser then sends it back with subsequent requests.
            # Flask securely signs the data so that it can’t be tampered with.
            session.clear()

            # Two Cookies:
            # 1. user_name: authentication cookie
            # 2. time_established: session-oriented cookie
            #session['user_name'] = username
            timenow= time()
            timenow = str(timenow)
            #session["time_established"] = timenow
            session.permanent = True
            # cookie SQL
            content = request.cookies.get("session")#?
            #print("content: "+content)
            db.execute(
                "INSERT OR REPLACE INTO cookie (user_id, user_name,honey_security, content, legal) VALUES (? , ?, ?, ?,?)",(user['id'],username,timenow,content,1)
            )  # sql command
            db.commit()
            response = redirect(url_for('index'))
            response.set_cookie('username',username)
            response.set_cookie('honey_security',timenow)
            #return redirect(url_for('index'))
            return response

        flash(error)
    
    return render_template("auth/login.html")

@bp.route("/logout")
def logout():
    db = get_db()
    db.execute(
        "DELETE FROM cookie WHERE honey_security = ?",(request.cookies.get("honey_security"),)
    )
    db.commit()
    # clear the current session
    session.clear()
    response = redirect(url_for("index"))
    response.delete_cookie('username')
    response.delete_cookie('honey_security')
    return response