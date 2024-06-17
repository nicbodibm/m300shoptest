from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Konfiguration für die Datenbank
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Konfiguration für Flask-Mail mit Gmail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'nico.bodmer1@gmail.com'
app.config['MAIL_PASSWORD'] = 'aaom torj swfi lcae'

db = SQLAlchemy(app)
mail = Mail(app)

# Datenbankmodelle
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    product = db.relationship('Product', backref=db.backref('cart_items', lazy=True))

# Admin-Ansicht
admin = Admin(app, name='Shop Admin', template_mode='bootstrap3')
admin.add_view(ModelView(Product, db.session))
admin.add_view(ModelView(CartItem, db.session))

@app.route('/')
def index():
    products = Product.query.all()
    return render_template('index.html', products=products)

@app.route('/cart')
def cart():
    cart = session.get('cart', [])
    total_price = sum(item['price'] for item in cart)
    return render_template('cart.html', cart=cart, total_price=total_price)

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    cart = session.get('cart', [])
    product = Product.query.get(product_id)
    if product:
        cart.append({'id': product.id, 'name': product.name, 'price': product.price})
        session['cart'] = cart
    return redirect(url_for('index'))

@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    cart = session.get('cart', [])
    cart = [item for item in cart if item['id'] != product_id]
    session['cart'] = cart
    return redirect(url_for('cart'))

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        
        msg = Message('Neue Nachricht von deiner Website',
                      sender='nico.bodmer1@gmail.com',
                      recipients=['nico.bodmer@edu.tbz.ch'])
        msg.body = f"Name: {name}\nEmail: {email}\n\nNachricht:\n{message}"
        mail.send(msg)
        
        return redirect(url_for('cart'))
    return render_template('contact.html')

if __name__ == '__main__':
    db.create_all()
    port = app.config.get("PORT", 8080)
    app.run(host='0.0.0.0', port=port, debug=True)
