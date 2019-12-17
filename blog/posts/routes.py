from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint)
from flask_login import current_user, login_required
from blog import db
from blog.models import Post, Travel, Comment
from blog.posts.forms import PostForm, CommentForm

posts = Blueprint('posts', __name__)


@posts.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    form.trip.choices =  [(g.id, g.destination) for g in Travel.query.order_by(Travel.date_posted.desc())]
    form.trip.choices.insert(0, (0, ''))
    if form.validate_on_submit():
        if form.trip.data=='':
            post = Post(title=form.title.data, content=form.content.data, author=current_user)
        else:
            trip = Travel.query.get(form.trip.data)
            post = Post(title=form.title.data, content=form.content.data, author=current_user, trip=trip)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('main.home'))
    return render_template('create_post.html', title='New Post',
                           form=form, legend='New Post')


@posts.route("/post/<int:post_id>", methods=['GET', 'POST'])
@login_required
def post(post_id):
    post = Post.query.get_or_404(post_id)
    comments = Comment.query.filter_by(topic=post).order_by(Comment.date_commented.desc())
    form = CommentForm()
    if form.validate_on_submit():
        newcomment = Comment(commenter=current_user, topic=post, content=form.content.data )
        db.session.add(newcomment)
        db.session.commit()
        flash('Your comment has been added!', 'success')
    return render_template('post.html', title=post.title, post=post, comments=comments, form=form, legend='Add Comment')


@posts.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    form.trip.choices = [(g.id, g.destination) for g in Travel.query.order_by(Travel.date_posted.desc())]
    if form.validate_on_submit():
        trip = Travel.query.get(form.trip.data)
        post.trip = trip
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('posts.post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post',
                           form=form, legend='Update Post')


@posts.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('main.home'))