function updateDisplay(item) {
  const span = document.getElementById('qty-' + item);
  const qty = cart[item] ? cart[item].qty : 0;
  span.textContent = qty > 0 ? qty : '';
  localStorage.setItem('cart', JSON.stringify(cart));
}