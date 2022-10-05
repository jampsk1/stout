from flask import Flask, render_template, request, redirect, url_for, flash, make_response

from cloudipsp import Api, Checkout
#импорты из майна, где инициализация переменных
from .main import app, db
from .models import Item, User
from flask_sqlalchemy import SQLAlchemy

@app.route('/')
def index():
    items = Item.query.order_by(Item.price).all()
    return render_template('index.html', data=items)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        log = request.form['login']
        password = request.form['password']
        print('check')
        response = db.session.query(User).filter_by(name=log).first()
        print(response)
        if log == "admin" and str(response) == password:
            return redirect('/admin')
        else:
            return redirect('/login')

    else:
        return render_template('login.html')


@app.route('/registr', methods=['POST', 'GET'])
def registr():
    if request.method == "POST":
        log = request.form['login']
        password = request.form['password']
        user = User(name=log, password=password)
        db.session.add(user)
        db.session.commit()
        return render_template('registr.html')
    else:
        return render_template('registr.html')


@app.route('/admin', methods=['POST', 'GET'])
def admin():

    items = Item.query.order_by(Item.price).all()

    return render_template('admin.html', data=items)


@app.route('/delete/<int:id>', methods=['POST', 'GET'])
def delete(id):
    item = Item.query.get(id)
    try:
        db.session.delete(item)
        db.session.commit()
        return redirect('/admin')
    except:
        return "Получилась ошибка"


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/cart')
def cart():
    return render_template('cart.html')


@app.route('/buy/<int:id>')
def item_buy(id):
    item = Item.query.get(id)

    api = Api(merchant_id=1396424,
              secret_key='test')
    checkout = Checkout(api=api)
    data = {
        "currency": "RUB",
        "amount": str(item.price) + "00"
    }
    url = checkout.url(data).get('checkout_url')
    return redirect(url)


@app.route('/create', methods=['POST', 'GET'])
def create():
    if request.method == "POST":
        title = request.form['title']
        price = request.form['price']

        item = Item(title=title, price=price)

        try:
            db.session.add(item)
            db.session.commit()
            return redirect('/')
        except:
            return "Получилась ошибка"
    else:
        return render_template('create.html')
