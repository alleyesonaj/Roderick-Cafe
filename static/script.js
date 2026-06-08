function updateDisplay(item) {
  const span = document.getElementById('qty-' + item);
  const qty = cart[item] ? cart[item].qty : 0;
  span.textContent = qty > 0 ? qty : '';
  localStorage.setItem('cart', JSON.stringify(cart));
}

document.querySelectorAll('.payment-method-btn').forEach(btn => {
  btn.addEventListener('click', function() {
    document.querySelectorAll('.payment-method-btn').forEach(b => b.classList.remove('selected'));
    this.classList.add('selected');
    localStorage.setItem('paymentMethod', this.id === 'cashPaymentBtn' ? 'Cash' : 'Card');
  });
});