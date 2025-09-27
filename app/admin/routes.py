from flask import Blueprint, render_template, url_for, flash
from werkzeug.utils import redirect, secure_filename
from ..db_models import Order, Item, db, User , Login_history
from ..admin.forms import AddItemForm, OrderEditForm
from ..funcs import admin_only
import bleach


admin = Blueprint("admin", __name__, url_prefix="/admin", static_folder="static", template_folder="templates")


@admin.route('/')
@admin_only
def dashboard():
    try:
        orders = Order.query.all()
        return render_template("admin/home.html", orders=orders)
    except Exception:
        raise


@admin.route('/items')
@admin_only
def items():
    try:
        items = Item.query.all()
        return render_template("admin/items.html", items=items)
    except Exception:
        raise


@admin.route('/add', methods=['POST', 'GET'])
@admin_only
def add():
    try:
        form = AddItemForm()
        if form.validate_on_submit():

            name = bleach.clean(form.name.data)
            price = form.price.data
            category = bleach.clean(form.category.data)
            details = bleach.clean(form.details.data)
            form.image.data.save('app/static/uploads/' + secure_filename(form.image.data.filename))
            print('not kaching')
            image = url_for('static', filename=f'uploads/{form.image.data.filename}')
            item = Item(name=name, price=price, category=category, details=details, image=image)
            db.session.add(item)
            db.session.commit()

            flash(f'{name} added successfully!','success')
            return redirect(url_for('admin.items'))
        return render_template("admin/add.html", form=form)
    except Exception:
        raise


@admin.route('/edit/<string:type>/<int:id>', methods=['POST', 'GET'])
@admin_only
def edit(type, id):
    try:
        if type == "item":
            item = Item.query.get(id)

            form = AddItemForm(

                name = item.name,
                price = item.price,
                category = item.category,
                details = item.details,
                image = item.image,
            )

            if form.validate_on_submit():

                item.name = bleach.clean(form.name.data)
                item.price = form.price.data
                item.category = bleach.clean(form.category.data)
                item.details = bleach.clean(form.details.data)
                form.image.data.save('app/static/uploads/' + form.image.data.filename)
                item.image = url_for('static', filename=f'uploads/{form.image.data.filename}')

                db.session.commit()
                return redirect(url_for('admin.items'))

        elif type == "order":
            order = Order.query.get(id)

            form = OrderEditForm(status = order.status)
            if form.validate_on_submit():
                order.status = form.status.data
                db.session.commit()
                return redirect(url_for('admin.dashboard'))

        return render_template('admin/add.html', form=form)
    except Exception:
        raise


@admin.route('/delete/<int:id>')
@admin_only
def delete(id):
    try:
        to_delete = Item.query.get(id)

        db.session.delete(to_delete)
        db.session.commit()

        flash(f'{to_delete.name} deleted successfully', 'error')
        return redirect(url_for('admin.items'))
    except Exception:
        raise


@admin.route('/history')
@admin_only
def view_logs():
    try:
        logs = Login_history.query.all()
        return render_template("admin/history.html", logs=logs)
    except Exception:
        raise


def allowed_file(filename):
    try:
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_FILE_TYPES
    except Exception:
        raise



