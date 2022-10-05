# БД - Таблицы - Записи
# Таблица:
# id   title   price   isActive
# 1    Some    100     True
# 2    Some2   200     False
# 3    Some3   40      True
from App2.main import db


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    isActive = db.Column(db.Boolean, default=True)

    # text = db.Column(db.Text, nullable=False)
    def __repr__(self):
        return self.title


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return self.password
