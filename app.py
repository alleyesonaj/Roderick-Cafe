from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.security import check_password_hash
from Database import get_db_connection

app = Flask(__name__)
app.secret_key = 'roderick_cafe_secret_key'


# ─────────────────────────────────────────
#  HELPER
# ─────────────────────────────────────────

def admin_required(f):
    """Decorator that blocks non-admin access to protected routes."""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated


# ─────────────────────────────────────────
#  PUBLIC PAGES
# ─────────────────────────────────────────

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/menu')
def menu():
    return render_template('menu.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/cart')
def cart():
    return render_template('cart.html')


@app.route('/receipt')
def receipt():
    return render_template('receipt.html')


@app.route('/order')
def order():
    return render_template('order.html')


@app.route('/order-menu')
def order_menu():
    return render_template('order-menu.html')


# ─────────────────────────────────────────
#  ADMIN AUTH
# ─────────────────────────────────────────

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if session.get('admin_logged_in'):
        return redirect(url_for('admin'))

    error = None

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if not username or not password:
            error = 'Please enter both username and password.'
        else:
            connection = get_db_connection()
            try:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT password_hash FROM admin WHERE username = %s",
                        (username,)
                    )
                    row = cursor.fetchone()

                if row and check_password_hash(row['password_hash'], password):
                    session['admin_logged_in'] = True
                    session['admin_username'] = username
                    return redirect(url_for('admin'))
                else:
                    error = 'Invalid username or password.'

            except Exception as e:
                error = f'Database error: {str(e)}'

            finally:
                connection.close()

    return render_template('admin-login.html', error=error)


@app.route('/admin/logout')
def admin_logout():
    session.clear()
    return redirect(url_for('admin_login'))


@app.route('/admin')
@admin_required
def admin():
    return render_template('admin-page.html')


# ─────────────────────────────────────────
#  API — STOCK
# ─────────────────────────────────────────

@app.route('/api/get-stock')
def get_stock():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # SELECT: Retrieves item name and stock for all menu items
            # Used to display out-of-stock status on the order-menu page
            cursor.execute("SELECT itemName, stock FROM menu_items")
            items = cursor.fetchall()

        return jsonify({"status": "success", "items": items})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

    finally:
        connection.close()


# ─────────────────────────────────────────
#  API — RECEIPT
# ─────────────────────────────────────────

@app.route('/api/get-receipt/<int:order_id>')
def get_receipt(order_id):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # JOIN: Retrieves full order summary — customer, service type,
            # payment, total, item names, prices, quantities, customizations
            cursor.execute("""
                SELECT c.customerName, o.serviceType, o.paymentOption, o.totalAmount,
                       m.itemName, m.price, od.quantity, od.customization
                FROM orders o
                INNER JOIN customers c ON o.customer_id = c.customer_id
                INNER JOIN order_details od ON o.order_id = od.order_id
                INNER JOIN menu_items m ON od.item_id = m.item_id
                WHERE o.order_id = %s
            """, (order_id,))
            rows = cursor.fetchall()

        if not rows:
            return jsonify({"status": "error", "message": "Order not found."}), 404

        return jsonify({"status": "success", "receipt": rows})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

    finally:
        connection.close()


# ─────────────────────────────────────────
#  API — PLACE ORDER
# ─────────────────────────────────────────

@app.route('/api/place-order', methods=['POST'])
def place_order():
    data = request.get_json()

    if not data:
        return jsonify({"status": "error", "message": "No data received."}), 400

    customer_name  = data.get('customerName')
    service_type   = data.get('serviceType')
    payment_option = data.get('paymentOption')
    total_amount   = data.get('totalAmount')
    cart_items     = data.get('items')

    # Input validation
    if not all([customer_name, service_type, payment_option, total_amount, cart_items]):
        return jsonify({"status": "error", "message": "Missing required fields."}), 400

    if not isinstance(cart_items, list) or len(cart_items) == 0:
        return jsonify({"status": "error", "message": "Cart is empty."}), 400

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:

            # INSERT: Stores customer name, retrieves generated customer_id
            cursor.execute(
                "INSERT INTO customers (customerName) VALUES (%s)",
                (customer_name,)
            )
            customer_id = cursor.lastrowid

            # INSERT: Stores order summary linked to the new customer
            cursor.execute("""
                INSERT INTO orders (customer_id, serviceType, paymentOption, totalAmount)
                VALUES (%s, %s, %s, %s)
            """, (customer_id, service_type, payment_option, total_amount))
            order_id = cursor.lastrowid

            for item in cart_items:
                item_name = item.get('name')
                item_qty  = item.get('qty')

                if not item_name or not item_qty:
                    raise Exception("Invalid item data in cart.")

                # SELECT: Retrieves item_id and stock for the ordered item
                cursor.execute(
                    "SELECT item_id, stock FROM menu_items WHERE itemName = %s",
                    (item_name,)
                )
                menu_item = cursor.fetchone()

                if not menu_item:
                    raise Exception(f"'{item_name}' was not found in the menu.")

                # Stock validation: Rejects order if quantity exceeds stock
                if menu_item['stock'] < item_qty:
                    raise Exception(f"'{item_name}' has insufficient stock.")

                # INSERT: Stores each ordered item with quantity and customization
                cursor.execute("""
                    INSERT INTO order_details (order_id, item_id, quantity, customization)
                    VALUES (%s, %s, %s, %s)
                """, (order_id, menu_item['item_id'], item_qty, item.get('customization', '')))

                # UPDATE: Deducts ordered quantity from stock
                cursor.execute(
                    "UPDATE menu_items SET stock = stock - %s WHERE item_id = %s",
                    (item_qty, menu_item['item_id'])
                )

        connection.commit()
        return jsonify({"status": "success", "order_id": order_id})

    except Exception as e:
        connection.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

    finally:
        connection.close()


# ─────────────────────────────────────────
#  RUN
# ─────────────────────────────────────────

if __name__ == '__main__':
    app.run(debug=False)