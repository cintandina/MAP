
// static/js/crear_solicitud.js
document.addEventListener('DOMContentLoaded', function () {
  const cajasInput = document.getElementById('cajasInput');
  if (cajasInput) {
    cajasInput.addEventListener('input', () => {
      const cajas = parseInt(cajasInput.value) || 0;
      document.getElementById('rollosOutput').textContent = cajas * 36;
      document.getElementById('serialesOutput').textContent = cajas * 544;
    });
  }
});
