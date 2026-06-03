from flask import Flask, render_template

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

@app.route('/receipt')
def receipt_page():
    return render_template('receipt.html')

@app.route('/order')
def order():
    return render_template('order.html')

@app.route('/order-menu')
def order_menu():
    return render_template('order-menu.html')

if __name__ == '__main__':
    app.run(debug=True)