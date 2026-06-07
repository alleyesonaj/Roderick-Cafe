from flask import Flask, render_template, request, jsonify
from Database import get_db_connection;

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
            cursor.execute("INSERT INTO Customers (customerName) VALUES (%s)", (customer_name,))
            customer_id = cursor.lastrowid
            
            # 2. Store Relational Transaction Summary Header
            cursor.execute("""
                INSERT INTO Orders (customer_id, serviceType, paymentOption, totalAmount) 
                VALUES (%s, %s, %s, %s)
            """, (customer_id, service_type, payment_option, total_amount))
            order_id = cursor.lastrowid
            
            # 3. Process Indivdual Itemized Order Details Breakdown
            for item in cart_items:
                cursor.execute("SELECT item_id FROM Menu_Items WHERE itemName = %s", (item['itemName'],))
                menu_item = cursor.fetchone()

        connection.commit()
        return jsonify({"status": "success", "order_id": order_id})
    
    except Exception as e:
        connection.rollback()  # Cancels changes if something fails 
        return jsonify({"status": "error", "message": str(e)}), 500

    finally:
        connection.close()

# DI PA TAPOS TANGINA

if __name__ == '__main__':
    app.run(debug=True)