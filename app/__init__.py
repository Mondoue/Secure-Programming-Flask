from datetime import datetime
from .config import Config
from flask import Flask, render_template, redirect, url_for, flash, request, abort,session
from flask_wtf.csrf import CSRFProtect
from flask_bootstrap import Bootstrap
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeSerializer
from cryptography.fernet import Fernet
import  bleach, time, base64
from .forms import LoginForm, RegisterForm
from .db_models import db, User, Item, Order, Ordered_item, Login_history
from .admin.routes import admin


app = Flask(__name__)
app.register_blueprint(admin)
app.config.from_object(Config)


fernet = Fernet(app.config['ENCRYPTION_KEY'])
serializer = URLSafeSerializer(app.config['SECRET_KEY'])

limiter = Limiter(app=app,key_func=get_remote_address,default_limits=["1000 per hour"])

MAX_LOGIN_ATTEMPTS = 3
LOCKOUT_DURATION = 300


Bootstrap(app)
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.refresh_view = 'login'
csrf = CSRFProtect(app)


with app.app_context():
	try:
		db.create_all()

		user = User.query.filter_by(name='admin').first()
		if not user:
			db.session.add(
				User(name='admin', password=generate_password_hash('adminadmin_123', method='pbkdf2:sha256', salt_length=8),
					 admin=1))
			db.session.commit()

	except Exception:
		raise


@app.context_processor
def inject_now():
	return {'now': datetime.utcnow()}


@login_manager.user_loader
def load_user(user_id):
	return User.query.get(user_id)


@app.route("/")
def home():
	try:
		items = Item.query.all()
		return render_template("home.html", items=items)
	except Exception:
		raise


@app.route("/login", methods=['POST', 'GET'])
@limiter.limit("500 per hour")
def login():
	try:
	
		if current_user.is_authenticated:
			return redirect(url_for('home'))

		form = LoginForm()
		if form.validate_on_submit():

			name = bleach.clean(form.name.data)
			user = User.query.filter_by(name=name).first()
			if user == None:

				flash(f'User with name {name} doesn\'t exist!<br> <a href={url_for("register")}>Register now!</a>', 'error')
				return redirect(url_for('login'))

			elif check_password_hash(user.password, bleach.clean(form.password.data)):
				print("oh no hes locked")
				print(user.locked_until)
				print(time.time())
				if(user.locked_until > time.time()):

					remaining_time = int(user.locked_until - int(time.time()))
					flash(f'User with name {name} is locked for {remaining_time} Seconds!</a>',
						  'error')
					return redirect(url_for('login'))

				else:

					user.login_attempts = 0

					db.session.add(Login_history(name= user.name,date=datetime.utcnow(),ip=request.remote_addr))
					db.session.commit()
					login_user(user)
					session.permanent = True

					return redirect(url_for('home'))
			else:
				user.login_attempts = user.login_attempts + 1

				if user.login_attempts >= MAX_LOGIN_ATTEMPTS:
					user.locked_until = int(time.time() + LOCKOUT_DURATION)
					user.login_attempts = 0

				db.session.commit()
				flash("Name and password incorrect!!", "error")
				return redirect(url_for('login'))
		return render_template("login.html", form=form)
	except Exception:
		raise


@app.route("/register", methods=['POST', 'GET'])
def register():
	
	try:
		if current_user.is_authenticated:
			return redirect(url_for('home'))

		form = RegisterForm()
		if form.validate_on_submit():

			user = User.query.filter_by(name=bleach.clean(form.name.data)).first()
			if user:
				flash(f"User with Name {user.name} already exists!!<br> <a href={url_for('login')}>Login now!</a>", "error")
				return redirect(url_for('register'))


			new_user = User(name=bleach.clean(form.name.data),
							password=generate_password_hash(
										bleach.clean(form.password.data),
										method='pbkdf2:sha256',
										salt_length=8),credit_card=fernet.encrypt(str(form.credit_card.data).encode('utf-8')))
			print(fernet.encrypt(str(form.credit_card.data).encode('utf-8')))
			db.session.add(new_user)
			db.session.commit()

			flash('Thanks for registering! You may login now.', 'success')
			return redirect(url_for('login'))
		return render_template("register.html", form=form)
	except Exception:
		raise


@app.route("/logout")

@login_required
def logout():
	logout_user()
	return redirect(url_for('login'))


@app.route("/add/<id>", methods=['POST'])
def add_to_cart(id):
	try:
		if not current_user.is_authenticated:
			flash(f'You must login first!<br> <a href={url_for("login")}>Login now!</a>', 'error')
			return redirect(url_for('login'))

		item = Item.query.get(id)
		if request.method == "POST":
			quantity = request.form["quantity"]
			current_user.add_to_cart(id, quantity)
			flash(f'''{item.name} successfully added to the <a href=cart>cart</a>.<br> <a href={url_for("cart")}>view cart!</a>''','success')
			return redirect(url_for('home'))
	except Exception:
		raise


@app.route("/cart")

@login_required
def cart():
	try:
		price = 0
		price_ids = []
		items = []
		quantity = []

		for cart in current_user.cart:
			items.append(cart.item)
			quantity.append(cart.quantity)
			price_id_dict = {
				"price": cart.item.price,
				"quantity": cart.quantity,
			}
			price_ids.append(price_id_dict)
			price += cart.item.price*cart.quantity
		return render_template('cart.html', items=items, price=price, price_ids=price_ids, quantity=quantity)
	except Exception:
		raise


@app.route('/orders')
@login_required
def orders():
	try:
		return render_template('orders.html', orders=current_user.orders)
	except Exception:
		raise


@app.route("/remove/<id>/<quantity>")
@login_required
def remove(id, quantity):
	try:
		current_user.remove_from_cart(id, quantity)
		return redirect(url_for('cart'))
	except Exception:
		raise


@app.route('/item/<int:id>')
def item(id):
	try:
		item = Item.query.get(id)
		return render_template('item.html', item=item)
	except Exception:
		raise


@app.route('/search')
def search():
	try:
		query = request.args['query']
		raw_search = "%{}%".format(query)
		search = bleach.clean(raw_search)
		items = Item.query.filter(Item.name.like(search)).all()
		return render_template('home.html', items=items, search=True, query=query)
	except Exception:
		raise


@app.route("/success", methods=['POST', 'GET'])
def success():
	try:
		order = Order(uid=current_user.id, date=datetime.utcnow(), status="processing")
		db.session.add(order)
		db.session.commit()

		for cart in current_user.cart:
			ordered_item = Ordered_item(oid=order.id, itemid=cart.item.id, quantity=cart.quantity)
			db.session.add(ordered_item)
			db.session.commit()
			current_user.remove_from_cart(cart.item.id, cart.quantity)
			db.session.commit()
		return render_template('success.html')
	except Exception:
		raise



@app.errorhandler(Exception)
def go_to_error_page(Exception):
	print(Exception)
	return render_template("500.html", )