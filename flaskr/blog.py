from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('blog', __name__)

@bp.route('/')
def index():
    if g.user is None:
        return render_template('blog/index.html')
    
    # except TypeError:
    #     usern = 'You need to log in'
    #     posts = None

    return render_template('blog/index.html',posts = g.posts)


@bp.route("/create",methods=('GET','POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            if(g.user['legal'] == 1):
                db.execute(
                    'INSERT INTO post (title, body, author_id) VALUES (?, ?, ?)',
                    (title,body,g.user["id"])
                    )
            else:
                db.execute(
                    'INSERT INTO fakeblogs (title, body, author_id) VALUES (?, ?, ?)',
                    (title,body,g.user["id"])
                    )
            db.commit()
            return redirect(url_for('blog.index'))
    
    return render_template('blog/create.html')

def get_post(id,islegal,check_author = True):
    print("islegal: "+str(islegal))
    if (islegal==1):
        post = get_db().execute(
            'SELECT p.id, title, body, created, author_id, username FROM post p JOIN user u ON p.author_id = u.id WHERE p.id = ?',
            (id,)
        ).fetchone()
    else:
        post = get_db().execute(
            'SELECT f.id, title, body, created, author_id, username FROM fakeblogs f JOIN fakeuser u ON f.author_id = u.id WHERE f.id = ?',
            (id,)
        ).fetchone()
    if post is None:
        abort(404,f"Post id {id} does not exist.")
    # if check_author and (post['author_id']!= g.user['id']):
    #     abort(403)
    return post



@bp.route('/<int:id>/update',methods = ('GET','POST'))
@login_required
def update(id):
    post = get_post(id,g.user['legal'])
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None
        
        if not title:
            error = 'Title is required.'
        
        if error is not None:
            flash(error)
        else:
            db = get_db()
            if (g.user['legal']==1):
                db.execute(
                    'UPDATE post SET title = ?, body = ? WHERE id = ?',
                    (title,body,id)
                )
            else:
                db.execute(
                    'UPDATE fakeblogs SET title = ?, body = ? WHERE id = ?',
                    (title,body,id)
                )

            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html',post=post)


@bp.route('/<int:id>/delete',methods= ('POST',))
@login_required
def delete(id):
    get_post(id,g.user['legal'])#check if this blog exist and if the user is authorized to delete it
    db = get_db()
    if (g.user['legal']==1):
        db.execute('DElETE FROM post WHERE id = ?',(id,))
    else:
        db.execute('DElETE FROM fakeblogs WHERE id = ?',(id,))
    db.commit()
    return redirect(url_for('blog.index'))