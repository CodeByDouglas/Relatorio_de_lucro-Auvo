document.addEventListener("DOMContentLoaded", function () {
  const form = document.querySelector("form");
  const submitButton = document.querySelector(".btn-consultar");

  form.addEventListener("submit", function (e) {
    e.preventDefault(); // Previne o submit padrão do formulário

    const appkey = document.getElementById("appkey").value.trim();
    const token = document.getElementById("token").value.trim();

    // Validação básica
    if (!appkey || !token) {
      showError("Por favor, preencha ambos os campos: AppKey e Token.");
      return;
    }

    // Desabilita o botão durante a requisição
    submitButton.disabled = true;
    submitButton.textContent = "Consultando...";

    // Dados para enviar
    const loginData = {
      appkey: appkey,
      token: token,
    };

    // Faz a requisição AJAX
    fetch("/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(loginData),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          // Sucesso - redireciona para o dashboard
          showSuccess(data.message);
          setTimeout(() => {
            window.location.href = data.redirect_url;
          }, 1500);
        } else {
          // Erro - mostra mensagem de erro
          showError(data.message);
        }
      })
      .catch((error) => {
        console.error("Erro na requisição:", error);
        showError("Erro de conexão. Tente novamente.");
      })
      .finally(() => {
        // Reabilita o botão
        submitButton.disabled = false;
        submitButton.textContent = "Consultar";
      });
  });
});

function showError(message) {
  // Remove alertas anteriores
  removeAlerts();

  // Cria o alerta de erro
  const alert = document.createElement("div");
  alert.className = "alert alert-error";
  alert.innerHTML = `
        <div class="alert-content">
            <span class="alert-icon">❌</span>
            <span class="alert-message">${message}</span>
        </div>
    `;

  // Adiciona o alerta ao formulário
  const form = document.querySelector("form");
  form.insertBefore(alert, form.firstChild);

  // Remove o alerta após 5 segundos
  setTimeout(() => {
    if (alert.parentNode) {
      alert.parentNode.removeChild(alert);
    }
  }, 5000);
}

function showSuccess(message) {
  // Remove alertas anteriores
  removeAlerts();

  // Cria o alerta de sucesso
  const alert = document.createElement("div");
  alert.className = "alert alert-success";
  alert.innerHTML = `
        <div class="alert-content">
            <span class="alert-icon">✅</span>
            <span class="alert-message">${message}</span>
        </div>
    `;

  // Adiciona o alerta ao formulário
  const form = document.querySelector("form");
  form.insertBefore(alert, form.firstChild);
}

function removeAlerts() {
  const alerts = document.querySelectorAll(".alert");
  alerts.forEach((alert) => {
    if (alert.parentNode) {
      alert.parentNode.removeChild(alert);
    }
  });
}
