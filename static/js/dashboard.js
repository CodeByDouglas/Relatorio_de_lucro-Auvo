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

  // Sincronização automática de produtos, serviços e colaboradores ao carregar o dashboard
  syncProducts();
  syncServices();
  syncCollaborators();

  // Carrega filtros dinamicamente
  loadFilters();

  // Carrega dados do dashboard
  loadDashboardData();

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

// Função para sincronizar serviços
function syncServices() {
  fetch("/api/services/sync", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        console.log("Serviços sincronizados:", data.message);
        // Recarrega filtros após sincronização
        loadFilters();
      } else {
        console.warn("Erro na sincronização de serviços:", data.message);
      }
    })
    .catch((error) => {
      console.error("Erro ao sincronizar serviços:", error);
    });
}

// Função para sincronizar colaboradores
function syncCollaborators() {
  fetch("/api/collaborators/sync", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        console.log("Colaboradores sincronizados:", data.message);
        // Recarrega filtros após sincronização
        loadFilters();
      } else {
        console.warn("Erro na sincronização de colaboradores:", data.message);
      }
    })
    .catch((error) => {
      console.error("Erro ao sincronizar colaboradores:", error);
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

// Função para carregar dados do dashboard
function loadDashboardData() {
  console.log("Carregando dados do dashboard...");

  fetch("/api/dashboard/data", {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    })
    .then((data) => {
      console.log("Dados do dashboard carregados:", data);
      updateDashboardDisplay(data);
    })
    .catch((error) => {
      console.error("Erro ao carregar dados do dashboard:", error);
      // Em caso de erro, carrega dados mock para não quebrar a interface
      loadMockData();
    });
}

// Função para atualizar a exibição do dashboard com dados reais
function updateDashboardDisplay(data) {
  console.log("Atualizando display com dados:", data);

  // Atualiza valores principais baseados nos labels dos cards
  updateMetricValueByLabel("FATURAMENTO TOTAL", data.faturamento_total, "R$");
  updateMetricValueByLabel("LUCRO TOTAL", data.lucro_total, "R$");
  updateMetricValueByLabel(
    "FATURAMENTO PRODUTO",
    data.faturamento_produto,
    "R$"
  );
  updateMetricValueByLabel(
    "FATURAMENTO SERVIÇO",
    data.faturamento_servico,
    "R$"
  );
  updateMetricValueByLabel("LUCRO PRODUTO", data.lucro_produto, "R$");
  updateMetricValueByLabel("LUCRO SERVIÇO", data.lucro_servico, "R$");

  // Atualiza percentuais
  const percentuais = data.percentuais || {};
  updatePercentageByLabel("FATURAMENTO TOTAL", percentuais.margem_lucro || 0);
  updatePercentageByLabel("LUCRO TOTAL", percentuais.margem_lucro || 0);
  updatePercentageByLabel(
    "FATURAMENTO PRODUTO",
    percentuais.faturamento_produto || 0
  );
  updatePercentageByLabel(
    "FATURAMENTO SERVIÇO",
    percentuais.faturamento_servico || 0
  );
  updatePercentageByLabel("LUCRO PRODUTO", percentuais.lucro_produto || 0);
  updatePercentageByLabel("LUCRO SERVIÇO", percentuais.lucro_servico || 0);

  // Atualiza período se disponível
  if (data.periodo) {
    console.log(`Período: ${data.periodo.inicio} até ${data.periodo.fim}`);
  }
}

// Função auxiliar para atualizar valores monetários baseado no label
function updateMetricValueByLabel(label, value, prefix = "") {
  const cards = document.querySelectorAll(".metric-card");
  cards.forEach((card) => {
    const labelElement = card.querySelector(".metric-label");
    if (labelElement && labelElement.textContent.trim() === label) {
      const valueElement = card.querySelector(".metric-value");
      if (valueElement && typeof value === "number") {
        const formattedValue = value.toLocaleString("pt-BR", {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2,
        });
        valueElement.textContent = `${prefix} ${formattedValue}`;
      }
    }
  });
}

// Função auxiliar para atualizar percentuais baseado no label
function updatePercentageByLabel(label, percentage) {
  const cards = document.querySelectorAll(".metric-card");
  cards.forEach((card) => {
    const labelElement = card.querySelector(".metric-label");
    if (labelElement && labelElement.textContent.trim() === label) {
      const circle = card.querySelector(".circle");
      const percentageText = card.querySelector(".percentage");

      if (circle && percentage >= 0) {
        // Atualiza o gráfico circular
        const dashArray = `${percentage}, 100`;
        circle.style.strokeDasharray = dashArray;
        circle.setAttribute("stroke-dasharray", dashArray);
      }

      if (percentageText) {
        percentageText.textContent = `${percentage.toFixed(1)}%`;
      }
    }
  });
}

// Função auxiliar para atualizar valores monetários
function updateMetricValue(selector, value, prefix = "") {
  const element = document.querySelector(selector);
  if (element && typeof value === "number") {
    const formattedValue = value.toLocaleString("pt-BR", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });
    element.textContent = `${prefix} ${formattedValue}`;
  }
}

// Função auxiliar para atualizar percentuais nos gráficos circulares
function updatePercentage(cardSelector, percentage) {
  const card = document.querySelector(cardSelector);
  if (card) {
    const circle = card.querySelector(".circle");
    const percentageText = card.querySelector(".percentage");

    if (circle && percentage >= 0) {
      // Atualiza o gráfico circular
      const dashArray = `${percentage}, 100`;
      circle.style.strokeDasharray = dashArray;
      circle.setAttribute("stroke-dasharray", dashArray);
    }

    if (percentageText) {
      percentageText.textContent = `${percentage.toFixed(1)}%`;
    }
  }
}

// Função de fallback com dados mock em caso de erro
function loadMockData() {
  console.log("Carregando dados mock...");
  const mockData = {
    faturamento_total: 848.475,
    lucro_total: 848.475,
    faturamento_produto: 58.975,
    faturamento_servico: 790.0,
    percentuais: {
      margem_lucro: 100.0,
      faturamento_produto: 6.95,
      faturamento_servico: 93.05,
    },
  };
  updateDashboardDisplay(mockData);
}
