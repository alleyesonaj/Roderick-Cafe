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

@app.route('/api/get-stock')
def get_stock():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT itemName, stock FROM menu_items")
            items = cursor.fetchall()
        return jsonify({"status": "success", "items": items})
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

            # 1. Store Customer Data
            cursor.execute("""
                INSERT INTO customers (customerName)
                VALUES (%s)
            """, (customer_name,))
            customer_id = cursor.lastrowid

            # 2. Store Relational Transaction Summary Header
            cursor.execute("""
                INSERT INTO orders (customer_id, serviceType, paymentOption, totalAmount)
                VALUES (%s, %s, %s, %s)
            """, (customer_id, service_type, payment_option, total_amount))
            order_id = cursor.lastrowid

            # 3. Process Individual Itemized Order Details Breakdown
            for item in cart_items:
                cursor.execute("""
                    SELECT item_id, stock FROM menu_items WHERE itemName = %s
                """, (item['name'],))
                menu_item = cursor.fetchone()

                if menu_item:
                    # Check if stock is enough
                    if menu_item['stock'] < item['qty']:
                        raise Exception(f"{item['name']} is out of stock or has insufficient stock.")

                    # Insert order detail
                    cursor.execute("""
                        INSERT INTO order_details (order_id, item_id, quantity, customization)
                        VALUES (%s, %s, %s, %s)
                    """, (order_id, menu_item['item_id'], item['qty'], item.get('customization', '')))

                    # Deduct stock
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