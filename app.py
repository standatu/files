from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///eshop.db'
app.config['SECRET_KEY'] = 'tajny_klic'

db = SQLAlchemy(app)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<Product {self.name}>'

class ProductForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    price = StringField('Price', validators=[DataRequired()])
    submit = SubmitField('Add Product')


@app.route('/', methods=['GET', 'POST'])
def index():
    products = Product.query.all()
    return render_template('index.html', products=products)


#pridat produkt
@app.route('/add', methods=['GET', 'POST'])
def add_product():
    form = ProductForm()

    if form.validate_on_submit():
        name = form.name.data
        price = form.price.data

        new_product = Product(name=name, price=price)
        db.session.add(new_product)
        db.session.commit()

        return redirect(url_for('index'))

    return render_template('add_product.html', form=form)


#uprava produktu
@app.route('/edit/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    form = ProductForm()

    if form.validate_on_submit():
        product.name = form.name.data
        product.price = form.price.data
        db.session.commit()
        return redirect(url_for('index'))

    form.name.data = product.name
    form.price.data = product.price
    return render_template('edit_product.html', form=form)

#smazat produkt
@app.route('/delete/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('index'))

#zobrazit produkty
@app.route('/')
def index():
    products = Product.query.all()
    return render_template('index.html', products=products)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product_detail.html', product=product)

@app.route('/cart', methods=['GET', 'POST'])
def cart():
    # Implementace logiky košíku
    return render_template('cart.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Implementace logiky přihlášení
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    # Implementace logiky registrace
    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True)