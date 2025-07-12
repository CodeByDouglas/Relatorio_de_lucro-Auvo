document.querySelector('form').addEventListener('submit', function(e) {
    const appkey = document.getElementById('appkey').value.trim();
    const token = document.getElementById('token').value.trim();
    if (!appkey || !token) {
        alert('Por favor, preencha ambos os campos: AppKey e Token.');
        e.preventDefault();
    }
});
