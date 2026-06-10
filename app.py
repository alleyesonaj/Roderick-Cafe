from flask import Flask, render_template, request, jsonify
from Database import get_db_connection

app = Flask(__name__)


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

@app.route('/admin')
def admin():
    return render_template('admin-page.html')


@app.route('/api/get-stock')
def get_stock():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:

            # SELECT Query: Retrieves the name and current stock of all
            # menu items to display out-of-stock status on the order page
            cursor.execute("""
                SELECT itemName, stock FROM menu_items
            """)
            items = cursor.fetchall()

        return jsonify({"status": "success", "items": items})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

    finally:
        connection.close()


@app.route('/api/get-receipt/<int:order_id>')
def get_receipt(order_id):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:

            # JOIN Query: Retrieves the full order summary including customer name,
            # service type, payment option, total amount, item names, item price,
            # quantities, and customizations for a specific order
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

        return jsonify({"status": "success", "receipt": rows})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

    finally:
        connection.close()


@app.route('/api/place-order', methods=['POST'])
def place_order():
    data = request.get_json()

    customer_name = data.get('customerName')
    service_type = data.get('serviceType')
    payment_option = data.get('paymentOption')
    total_amount = data.get('totalAmount')
    cart_items = data.get('items')

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:

            # INSERT Query: Stores the customer's name into the customers table
            # and retrieves the generated customer_id for linking to the order
            cursor.execute("""
                INSERT INTO customers (customerName)
                VALUES (%s)
            """, (customer_name,))
            customer_id = cursor.lastrowid

            # INSERT Query: Stores the order summary including customer ID,
            # service type, payment option, and total amount into the orders table
            cursor.execute("""
                INSERT INTO orders (customer_id, serviceType, paymentOption, totalAmount)
                VALUES (%s, %s, %s, %s)
            """, (customer_id, service_type, payment_option, total_amount))
            order_id = cursor.lastrowid

            for item in cart_items:

                # SELECT Query with WHERE: Retrieves the item_id and current stock
                # of a specific menu item by name to validate and process the order
                cursor.execute("""
                    SELECT item_id, stock FROM menu_items WHERE itemName = %s
                """, (item['name'],))
                menu_item = cursor.fetchone()

                if menu_item:

                    # Stock validation: Cancels the order if requested
                    # quantity exceeds available stock
                    if menu_item['stock'] < item['qty']:
                        raise Exception(f"{item['name']} is out of stock or has insufficient stock.")

                    # INSERT Query: Stores each ordered item's details including
                    # order ID, item ID, quantity, and customization notes
                    cursor.execute("""
                        INSERT INTO order_details (order_id, item_id, quantity, customization)
                        VALUES (%s, %s, %s, %s)
                    """, (order_id, menu_item['item_id'], item['qty'], item.get('customization', '')))

                    # UPDATE Query: Deducts the ordered quantity from the
                    # menu item's stock to keep inventory accurate
                    cursor.execute("""
                        UPDATE menu_items SET stock = stock - %s WHERE item_id = %s
                    """, (item['qty'], menu_item['item_id']))

        connection.commit()
        return jsonify({"status": "success", "order_id": order_id})

    except Exception as e:
        connection.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

    finally:
        connection.close()


if __name__ == '__main__':
    app.run(debug=True)