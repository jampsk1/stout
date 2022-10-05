import datetime
from typing import List

from flask import Flask, render_template, request, redirect, make_response
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, asc, desc

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Item(db.Model):
    __tablename__ = 'item'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    isActive = db.Column(db.Boolean, default=True)
    category = db.Column(db.Integer, ForeignKey('Category.id'))
    definition = db.Column(db.String(100))

    def __repr__(self):
        return self.title


class Category(db.Model):
    __tablename__ = 'Category'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return self.title


class FeedBack(db.Model):
    __tablename__ = 'FeedBack'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    feedBackText = db.Column(db.String(256), nullable=False)
    idUser = db.Column(db.Integer, ForeignKey('user.id'))

    def __repr__(self):
        return self.title


class Order(db.Model):
    __tablename__ = 'Order'
    id = db.Column(db.Integer, primary_key=True)
    idUser = db.Column(db.Integer, ForeignKey('user.id'))
    dateOrder = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    isDelivery = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return self.id

    def __str__(self):
        return self.dateOrder.date().__str__()


class OrderItem(db.Model):
    __tablename__ = 'OrderItem'
    id = db.Column(db.Integer, primary_key=True)
    idOrder = db.Column(db.Integer, ForeignKey('Order.id'))
    idItem = db.Column(db.Integer, ForeignKey('item.id'))
    count = db.Column(db.Integer, default=1)

    def __repr__(self):
        return self.id


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return self.password


class Basket(db.Model):
    __tablename__ = 'basket'
    id = db.Column(db.Integer, primary_key=True)
    idUser = db.Column(db.Integer, ForeignKey('user.id'))
    idItem = db.Column(db.Integer, ForeignKey('item.id'))
    count = db.Column(db.Integer, default=1)

    def __repr__(self):
        return self.id


@app.route('/')
@app.route('/sort=<string:sort>')
@app.route('/category=<int:category>')
def index(sort=None, category=None):
    categories = Category.query.all()
    if sort is not None:
        if sort == 'desc':
            items = Item.query.order_by(desc(Item.price)).all()
        else:
            items = Item.query.order_by(asc(Item.price)).all()
    else:
        items = Item.query.order_by(asc(Item.price)).all()
    if category is not None:
        categoryEntity = Category.query.filter(Category.id == category).first()
        if categoryEntity is not None:
            items = filter(lambda x: x.category == categoryEntity.id, items)
    return render_template('index.html', data=items, categories=categories)


@app.route('/sort=desc')
def sort():
    items = Item.query.order_by(desc(Item.price)).all()
    return render_template('index.html', data=items)


# Блок для корзины
@app.route('/basket')
def basket():
    idUser = request.cookies.get('user')
    res = db.session.query(Item, Basket).filter(Item.id == Basket.idItem).join(Basket, Basket.idUser == idUser).filter(
        Basket.count > 0).all()
    sum = 0
    for r in res:
        sum += r.Basket.count * r.Item.price
    return render_template('basket.html', data=res, sum=sum)


@app.route('/orders', methods=['POST', 'GET'])
def orders():
    idUser = request.cookies.get('user')
    orders = db.session.query(Order).filter(idUser == Order.idUser).all()
    res = list()
    if idUser == 'admin':
        orders = db.session.query(Order).all()
    for order in orders:
        items = db.session.query(Item).join(OrderItem, OrderItem.idOrder == order.id).filter(
            Item.id == OrderItem.idItem).all()
        res.append((order, items))
    if idUser == 'admin':
        return render_template('orders.html', orders=res)
    return render_template('order.html', orders=res)


@app.route('/orderDelivery/<int:id>', methods=['POST', 'GET'])
def delivery(id):
    idUser = request.cookies.get('user')
    if idUser == 'admin':
        order: Order = Order.query.filter_by(id=id).first()
        order.isDelivery = True
        try:
            db.session.update(order)
            db.session.commit()
            return redirect('/')
        except:
            return "Получилась ошибка"


@app.route('/deleteFeedBack/<int:id>', methods=['POST', 'GET'])
def deleteFeedBack(id):
    idUser = request.cookies.get('user')
    if idUser == 'admin':
        feedBack: FeedBack = FeedBack.query.filter(FeedBack.id==id).first()
        try:
            db.session.delete(feedBack)
            db.session.commit()
            return redirect('/admin')
        except:
            return "Получилась ошибка"


@app.route('/addItem/<int:id>', methods=['POST', 'GET'])
def addItem(id):
    idUser = request.cookies.get('user')
    basket = Basket.query.filter_by(idItem=id, idUser=idUser).first()
    if basket:
        basket.count = basket.count + 1
    else:
        basket = Basket(idUser=idUser, idItem=id)
    try:
        db.session.add(basket)
        db.session.commit()
        return redirect('/')
    except:
        return "Получилась ошибка"


@app.route('/deleteItem/<int:id>', methods=['POST', 'GET'])
def deleteItem(id):
    idUser = request.cookies.get('user')
    try:
        basket = Basket.query.filter_by(idItem=id, idUser=idUser).first()
        basket.count = basket.count - 1
        db.session.add(basket)
        db.session.commit()
        return redirect('/basket')
    except:
        return "Получилась ошибка"


# Логин и регистрация
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        log = request.form['login']
        password = request.form['password']
        response = db.session.query(User).filter_by(name=log).first()
        # чек пароля
        if str(response) == password:
            if log == "admin":
                resp = setcookie1('/admin', log)
            else:
                resp = setcookie1('/', log)
            return resp
        else:
            return render_template('login.html', mes="Неверный пароль")
    else:
        return render_template('login.html')


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    resp = make_response(redirect('/'))
    resp.set_cookie('user', '', 0)
    return resp


def setcookie1(url, name):
    resp = make_response(redirect(url))
    resp.set_cookie('user', name)
    return resp


@app.route('/registr', methods=['POST', 'GET'])
def registr():
    if request.method == "POST":
        log = request.form['login']
        password = request.form['password']
        response = db.session.query(User).filter_by(name=log).first()
        print(response)
        if response is None:
            user = User(name=log, password=password)
            db.session.add(user)
            db.session.commit()
            print('Все хорошо')
            return render_template('registr.html', mes="Регистрация прошла успешно")
        else:
            return render_template('registr.html', mes="Пользователь с этим логином уже зарегистрирован")
    else:
        return render_template('registr.html')


# кабинет администратора
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


@app.route('/buy')
def item_buy():
    idUser = request.cookies.get('user')
    baskets = Basket.query.filter_by(idUser=idUser).all()
    order = Order(idUser=idUser)
    try:
        db.session.add(order)
        db.session.commit()
    except:
        return "Получилась ошибка1"
    for basket in baskets:
        orderItem = OrderItem(idOrder=order.id, idItem=basket.idItem, count=basket.count)
        try:
            db.session.add(orderItem)
            db.session.commit()
        except:
            return "Получилась ошибка2"
    return redirect("/")


@app.route('/cart')
def cart():
    return render_template('cart.html')


@app.route('/feedback')
def feedback():
    feedbacks = FeedBack.query.all()
    return render_template('feedback.html', feedbacks=feedbacks)


@app.route('/createFeedBack', methods=['POST', 'GET'])
def createFeedBack():
    idUser = request.cookies.get('user')
    if request.method == "GET":
        return render_template('CreateFeedBack.html')
    if request.method == "POST":
        title = request.form['title']
        allText = request.form['allText']
        feedback = FeedBack(title=title, feedBackText=allText, idUser=idUser)
        try:
            db.session.add(feedback)
            db.session.commit()
            return redirect('/')
        except:
            return "Получилась ошибка2"


@app.route('/create', methods=['POST', 'GET'])
def create():
    if request.method == "GET":
        categories = Category.query.all()
        return render_template('create.html', categories=categories)
    if request.method == "POST":
        ar = request
        title = request.form['title']
        price = request.form['price']
        category = request.form['category']
        definition = request.form['definition']
        check = Category.query.filter(Category.id == category).one()
        item = None
        if check is not None:
            item = Item(title=title, price=price, category=check.id, definition=definition)
        else:
            item = Item(title=title, price=price, definition=definition)
        try:
            db.session.add(item)
            db.session.commit()
            return redirect('/')
        except:
            return "Получилась ошибка"
    else:
        return render_template('create.html')


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
