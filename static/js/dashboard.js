document.addEventListener("DOMContentLoaded", function () {
  // Tab functionality
  const tabs = document.querySelectorAll(".tab");

  tabs.forEach((tab) => {
    tab.addEventListener("click", function () {
      const tabType = this.dataset.tab;

      if (tabType === "geral") {
        // Redireciona para a página do dashboard
        window.location.href = "/dashboard";
      } else if (tabType === "detalhado") {
        // Redireciona para a página de relatório detalhado
        window.location.href = "/relatorio-tarefas";
      }
    });
  });

  // Export Excel functionality
  const exportBtn = document.querySelector(".btn-export");
  exportBtn.addEventListener("click", function () {
    // Add export logic here
    console.log("Export Excel clicked");
    alert("Funcionalidade de exportação será implementada");
  });

  // Consultar button functionality
  const consultarBtn = document.querySelector(".btn-consultar");
  consultarBtn.addEventListener("click", function () {
    // Get filter values
    const filters = {
      dataInicial: document.querySelector(".filter-group:nth-child(1) input")
        .value,
      dataFinal: document.querySelector(".filter-group:nth-child(2) input")
        .value,
      produto: document.querySelector(".filter-group:nth-child(3) select")
        .value,
      servico: document.querySelector(".filter-group:nth-child(4) select")
        .value,
      tipoTarefa: document.querySelector(".filter-group:nth-child(5) select")
        .value,
      colaborador: document.querySelector(".filter-group:nth-child(6) select")
        .value,
    };

    console.log("Filters applied:", filters);

    // Here you can add logic to filter the data
    // For now, we'll just show a message
    alert("Consulta realizada com os filtros selecionados");
  });

  // Animate circular charts on load
  function animateCharts() {
    const circles = document.querySelectorAll(".circle");
    circles.forEach((circle) => {
      const dashArray = circle.getAttribute("stroke-dasharray");
      const percentage = dashArray.split(",")[0];
      circle.style.strokeDasharray = `${percentage}, 100`;
    });
  }

  // Call animation after a short delay
  setTimeout(animateCharts, 500);

  // Sincronização automática de produtos ao carregar o dashboard
  syncProducts();

  // Carrega filtros dinamicamente
  loadFilters();

  // Set current date as default for date inputs
  const today = new Date().toISOString().split("T")[0];
  const dateInputs = document.querySelectorAll('input[type="date"]');
  dateInputs.forEach((input) => {
    if (!input.value) {
      input.value = today;
    }
  });
});

// Função para sincronizar produtos
function syncProducts() {
  fetch("/api/products/sync", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        console.log("Produtos sincronizados:", data.message);
        // Recarrega filtros após sincronização
        loadFilters();
      } else {
        console.warn("Erro na sincronização de produtos:", data.message);
      }
    })
    .catch((error) => {
      console.error("Erro ao sincronizar produtos:", error);
    });
}

// Função para carregar filtros
function loadFilters() {
  fetch("/api/dashboard/filters")
    .then((response) => response.json())
    .then((data) => {
      // Atualiza select de produtos
      const produtoSelect = document.querySelector(
        ".filter-group:nth-child(3) select"
      );
      if (produtoSelect && data.produtos) {
        produtoSelect.innerHTML = '<option value="">Todos os produtos</option>';
        data.produtos.forEach((produto) => {
          const option = document.createElement("option");
          option.value = produto.id;
          option.textContent = produto.nome;
          produtoSelect.appendChild(option);
        });
      }

      // Atualiza outros selects conforme necessário
      updateSelectOptions(
        ".filter-group:nth-child(4) select",
        data.servicos,
        "Todos os serviços"
      );
      updateSelectOptions(
        ".filter-group:nth-child(5) select",
        data.tipos_tarefa,
        "Todos os tipos"
      );
      updateSelectOptions(
        ".filter-group:nth-child(6) select",
        data.colaboradores,
        "Todos os colaboradores"
      );
    })
    .catch((error) => {
      console.error("Erro ao carregar filtros:", error);
    });
}

// Função auxiliar para atualizar selects
function updateSelectOptions(selector, items, defaultText) {
  const select = document.querySelector(selector);
  if (select && items) {
    select.innerHTML = `<option value="">${defaultText}</option>`;
    items.forEach((item) => {
      const option = document.createElement("option");
      option.value = item.id;
      option.textContent = item.nome;
      select.appendChild(option);
    });
  }
}
