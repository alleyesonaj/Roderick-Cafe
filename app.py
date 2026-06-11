from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from Database import get_db_connection

app = Flask(__name__)
app.secret_key = 'roderick_cafe_secret_key'


# ─────────────────────────────────────────
#  HELPER DECORATORS
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
#  ADMIN / MANAGEMENT LAYOUT ROUTES
# ─────────────────────────────────────────

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if session.get('admin_logged_in'):
        return redirect(url_for('admin_dashboard'))

    error = None
    if request.method == 'POST':
        username_input = request.form.get('username', '').strip()
        password_input = request.form.get('password', '').strip()

        if username_input == "admin" and password_input == "admin123":
            session['admin_logged_in'] = True
            session['admin_user'] = "admin"
            return redirect(url_for('admin_dashboard'))

        try:
            connection = get_db_connection()
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM admin WHERE username = %s", (username_input,))
                admin_account = cursor.fetchone()

                if admin_account:
                    db_password = admin_account.get('password_hash') or admin_account.get('password')
                    if db_password == password_input:
                        session['admin_logged_in'] = True
                        session['admin_user'] = admin_account['username']
                        return redirect(url_for('admin_dashboard'))
                    else:
                        error = "Invalid admin username or password details."
                else:
                    error = "Invalid admin username or password details."
            connection.close()
        except Exception as e:
            error = f"Database Error: {str(e)}"

    return render_template('admin-login.html', error=error)


@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) AS total_orders FROM orders")
            total_orders = cursor.fetchone()['total_orders'] or 0

            cursor.execute("SELECT SUM(totalAmount) AS total FROM orders")
            total_rev = cursor.fetchone()['total'] or 0

            cursor.execute("SELECT SUM(totalAmount) AS cash FROM orders WHERE paymentOption = 'Cash'")
            cash_rev = cursor.fetchone()['cash'] or 0

            cursor.execute("SELECT SUM(totalAmount) AS card FROM orders WHERE paymentOption = 'Card'")
            card_rev = cursor.fetchone()['card'] or 0

            cursor.execute("SELECT COUNT(*) AS total_customers FROM customers")
            total_customers = cursor.fetchone()['total_customers'] or 0

            cursor.execute("""
                SELECT m.itemName, SUM(od.quantity) as total_qty
                FROM order_details od
                JOIN menu_items m ON od.item_id = m.item_id
                GROUP BY od.item_id
                ORDER BY total_qty DESC
                LIMIT 1
            """)
            popular_row = cursor.fetchone()
            most_ordered_item = popular_row['itemName'] if popular_row else "None yet"

            cursor.execute("""
                SELECT o.order_id, c.customerName, o.serviceType, o.paymentOption, o.totalAmount
                FROM orders o
                JOIN customers c ON o.customer_id = c.customer_id
                ORDER BY o.order_id DESC
            """)
            orders_history = cursor.fetchall()

            cursor.execute("SELECT itemName, stock FROM menu_items ORDER BY itemName ASC")
            stock_levels = cursor.fetchall()

        connection.close()

        return render_template(
            'admin-page.html',
            total_orders=total_orders,
            total_rev=total_rev,
            cash_rev=cash_rev,
            card_rev=card_rev,
            total_customers=total_customers,
            most_ordered_item=most_ordered_item,
            orders_history=orders_history,
            stock_levels=stock_levels
        )

    except Exception as e:
        return f"Dashboard Error: {str(e)}"


@app.route('/admin/logout')
def admin_logout():
    session.clear()
    return redirect(url_for('admin_login'))


@app.route('/admin')
def admin():
    return redirect(url_for('admin_dashboard'))


# ─────────────────────────────────────────
#  API
# ─────────────────────────────────────────

@app.route('/api/get-receipt/<int:order_id>')
def get_receipt(order_id):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
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


@app.route('/api/place-order', methods=['POST'])
def place_order():
    try:
        data = request.json
        if not data:
            return jsonify({"status": "error", "message": "No payload data received"}), 400

        customer_name = data.get('customerName', '').strip() or "Anonymous"
        service_type = data.get('serviceType', 'Dine-in')
        payment_option = data.get('paymentOption', 'Cash')
        total_amount = data.get('totalAmount', 0)
        cart_items = data.get('items', [])

        if not cart_items:
            return jsonify({"status": "error", "message": "The cart is empty"}), 400

        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO customers (customerName) VALUES (%s)",
                (customer_name,)
            )
            customer_id = cursor.lastrowid

            cursor.execute("""
                INSERT INTO orders (customer_id, serviceType, paymentOption, totalAmount)
                VALUES (%s, %s, %s, %s)
            """, (customer_id, service_type, payment_option, total_amount))
            order_id = cursor.lastrowid

            for item in cart_items:
                item_name = item.get('name', '').strip()
                item_qty = int(item.get('qty', 1))

                cursor.execute(
                    "SELECT item_id, stock FROM menu_items WHERE itemName = %s",
                    (item_name,)
                )
                menu_item = cursor.fetchone()

                if not menu_item:
                    raise Exception(f"'{item_name}' was not found in the menu.")

                if menu_item['stock'] < item_qty:
                    raise Exception(f"'{item_name}' has insufficient stock.")

                cursor.execute("""
                    INSERT INTO order_details (order_id, item_id, quantity, customization)
                    VALUES (%s, %s, %s, %s)
                """, (order_id, menu_item['item_id'], item_qty, item.get('customization', '')))

                cursor.execute(
                    "UPDATE menu_items SET stock = stock - %s WHERE item_id = %s",
                    (item_qty, menu_item['item_id'])
                )

        connection.commit()
        return jsonify({"status": "success", "order_id": order_id})

    except Exception as e:
        if 'connection' in locals():
            connection.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

    finally:
        if 'connection' in locals():
            connection.close()


# ─────────────────────────────────────────
#  RUN
# ─────────────────────────────────────────

if __name__ == '__main__':
    app.run(debug=True)