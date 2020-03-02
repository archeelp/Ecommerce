from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from ecommerce import db, login_manager , app 
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(20), unique=True, nullable=False)
    lastname = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    utype = db.Column(db.String(60), default='user')
    cart = db.relationship('Cart', backref='author', lazy=True)
    instagram_id = db.Column(db.String(60),nullable=True)
    facebook_id = db.Column(db.String(60), nullable=True)

    
    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    brand = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Float, nullable=True)
    overall_rating = db.Column(db.Float, nullable=True)
    category = db.Column(db.String(1000), nullable=False)
    price = db.Column(db.String(100), nullable=False)
    discounted_price = db.Column(db.String(100), nullable=False,default=0.0)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    info = db.Column(db.Text, nullable=False , default="No Information Available")
    image_urls = db.Column(db.String(1000), nullable=False)
    cart = db.relationship('Cart', backref='product', lazy=True)

class Cart(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

    def __repr__(self):
        return f"Cart('{self.user_id}', '{self.product_id}')"
