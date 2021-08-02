from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import Post, User, Comment
from . import db

views = Blueprint('views', __name__)

@views.route('/')
@views.route('/home')
@login_required
def home():
    posts = Post.query.all()
    return render_template('home.html', user=current_user, posts=posts)

@views.route('/create-post', methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == 'POST':
        text = request.form.get('text')
        if not text:
            flash('Post Cannot Be Empty!', category='error')
        else:
            post = Post(text=text, author=current_user.id)
            db.session.add(post)
            db.session.commit()
            flash('Post Created!', category='success')
            return redirect(url_for('views.home'))
    return render_template('create_post.html', user=current_user)

@views.route('/delete-post/<id>')
def delete_post(id):
    post = Post.query.filter_by(id=id).first()

    if not post:
        flash('Post Doesn\'t Exist', category='error')
    elif current_user.id != post.author:
        flash('You do not have permission to delete this post.', category='error')
    else:
        comments = Comment.query.filter_by(post_id=id).all()
        for comment in comments:
            db.session.delete(comment)
        db.session.delete(post)
        db.session.commit()
        flash('Post Deleted!',category='success')
        
    return redirect(url_for('views.home'))

@views.route('/posts/<username>')
@login_required
def posts(username):
    user = User.query.filter_by(username=username).first()
    
    if not user:
        flash(f'User {username} Doesn\'t Exist!', category='error')
        return redirect(url_for('views.home'))
        
    posts = user.posts
    return render_template('posts.html', user=current_user, posts=posts, username=username)

@views.route('/create-comment/<post_id>', methods=['POST'])
@login_required
def create_comment(post_id):
    text = request.form.get('text')

    if not text:
        flash('Comment Cannot Be Empty!', category='error')
    else:
        post = Post.query.filter_by(id=post_id)
        if post:
            comment = Comment(text=text, author=current_user.id, post_id=post_id)
            db.session.add(comment)
            db.session.commit()
            flash('Comment Added!', category='success')
        else:
            flash('Post Doesn\'t Exist', category='error')
    
    return redirect(url_for('views.home'))

@views.route('/delete-comment/<comment_id>')
@login_required
def delete_comment(comment_id):
    comment = Comment.query.filter_by(id=comment_id).first()

    if not comment:
        flash('Comment Doesn\'t Exist', category='error')
    elif current_user.id != comment.author and current_user.id != comment.post.author:
        flash('You Do Not Have Permission To Delete This Comment', category='error')
    else:
        flash('Comment Deleted!',category='success')
        db.session.delete(comment)
        db.session.commit()

    return redirect(url_for('views.home'))
