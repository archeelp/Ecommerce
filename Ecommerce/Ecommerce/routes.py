import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from ecommerce import app, db, bcrypt, mail
from ecommerce.forms import (RegistrationForm, LoginForm, RequestResetForm, ResetPasswordForm )
from ecommerce.models import User,Product,Cart
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
from datetime import datetime
import PyPDF2
import random
import csv
from ecommerce.predict import predict


@app.route("/")
@app.route("/home")
def home():
    #prediction = predict("chair")
    #print(prediction)
    return render_template('home.html',title="Home")


@app.route("/about")
def about():
    return render_template('about.html', title='About')

@app.route("/shop")
def shop():
    products = Product.query.all()
    products = products[0:10]
    p = []
    for i in range(len(products)):
        p.append([products[i],products[i].image_urls.strip('][').split(', ')])
    
    return render_template('product.html', products=p)


@app.route("/product-detail/<int:pid>")
def product_details(pid):
    product = Product.query.get_or_404(pid)
    return render_template('product-detail.html', title=product.name,prodduct=product)

@app.route("/cart")
@login_required
def cart():
    products_id = Cart.query.filter_by(author=current_user)
    pids =[pid.product_id for pid in products_id]
    products = [ (Product.query.get(pid),pids.count(pid)) for pid in set(pids)]
    for i in range(len(products)):
        products[i][0].image_urls = products[i][0].image_urls.strip('][').split(', ')
    for i in range(len(products)):
        products[i][0].price = int(products[i][0].price)
    subtotal = 0
    for i in range(len(products)):
        subtotal += int(products[i][0].price)*int(products[i][1])

    return render_template('shoping-cart.html', title='About', products=products, subtotal=subtotal)

@app.route("/cart/<int:pid>/", methods=['GET', 'POST'])
@login_required
def add_to_cart(pid):
    product = Product.query.get_or_404(pid)
    cart = Cart(author=current_user, product=product)
    db.session.add(cart)
    db.session.commit()
    flash('Product added to cart', 'success')
    next_page = request.args.get('next')
    return redirect(next_page) if next_page else redirect(url_for('cart'))


@app.route("/removefromcart/<int:cart_id>", methods=['GET', 'POST'])
@login_required
def remove_from_cart(cart_id):
    cart = Cart.query.filter_by(product_id=cart_id)[0]
    #if cart.author != current_user:
    #    abort(403)
    print("Before deleting: ", Cart.query.filter_by(product_id=cart_id)[0])
    db.session.delete(cart)
    print("S: ", cart)
    db.session.commit()
    flash('Product deleted from cart', 'success')
    return redirect(url_for('cart'))




@app.route("/blog")
def blog():
    return render_template('blog.html', title='Blogs')

@app.route("/contact")
def contact():
    return render_template('contact.html', title='Contact')


@app.route("/blog-detail")
def blog_detail():
    return render_template('blog-detail.html', title='Blog')

@app.route("/profile")
@login_required
def profile():
    if not current_user.is_authenticated:
        return redirect(url_for('register'))
    firstname=current_user.firstname
    return render_template('profile.html', title='Profile',firstname=firstname)

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':    
        hashed_password = bcrypt.generate_password_hash(request.form.get('password'))
        user = User(firstname=request.form.get('firstname'), lastname=request.form.get('lastname'), email=request.form.get('email'), instagram_id=request.form.get('instagram_id'), facebook_id=request.form.get('facebook_id'), password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register')

@app.route("/regpro", methods=['GET', 'POST'])
def regpro():
    with open('./ecommerce/flipkart_com-ecommerce_sample.csv', mode='r', encoding="utf8") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
            # l = l.strip('][').split(', ')   to convert a string representation of list into list
            if  row['retail_price'] and row['discounted_price']:
                product = Product(name = row['product_name'],category = row['product_category_tree'],price = row['retail_price'],discounted_price = row['discounted_price'],image_urls = row['image'],info = row['description'],rating = None if 'No rating available' == row['product_rating'] else float(row['product_rating']),overall_rating= None if 'No rating available' == row['overall_rating'] else float(row['overall_rating']),brand = row['brand'])
                db.session.add(product)
            line_count += 1
        db.session.commit()
    return render_template('register.html', title='Register')

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    else:
        user = User.query.filter_by(email=request.form.get('email')).first()
        if user and bcrypt.check_password_hash(user.password,request.form.get('password')):
            login_user(user, remember=request.form.get('remember'))
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            if request.method == 'POST':
                flash('Login failed','danger')
    return render_template('login.html', title='Login')




@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    # if current_user.is_authenticated:
    #     return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    # if current_user.is_authenticated:
    #     return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)


# ADMIN routes

@app.route('/admin-login',methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    else:
        user = User.query.filter_by(email=request.form.get('email')).first()
        if user and bcrypt.check_password_hash(user.password,request.form.get('password')) and user.utype=='admin':
            login_user(user, remember=request.form.get('remember'))
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('admin_home'))
        else:
            if request.method == 'POST':
                flash('Login failed','danger')
    return render_template('admin-login.html', title='Login')


@app.route("/admin-home")
@login_required
def admin_home():
    if current_user.utype == 'admin':
        return render_template('dashboard.html', title='Dashboard')
    else :
        flash('Not an admin','danger')
        return redirect(url_for('home'))
        