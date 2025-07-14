document.addEventListener("DOMContentLoaded", function () {
  // Header Tab functionality
  const headerTabs = document.querySelectorAll(".header-tab");

  headerTabs.forEach((tab) => {
    tab.addEventListener("click", function () {
      // Remove active class from all tabs
      headerTabs.forEach((t) => t.classList.remove("active"));
      // Add active class to clicked tab
      this.classList.add("active");

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
    // Get filter values using label-based approach
    const filters = {};

    const filterGroups = document.querySelectorAll(".filter-group");
    filterGroups.forEach((group) => {
      const label = group.querySelector("label");
      const input = group.querySelector("input, select");

      if (!label || !input) return;

      const labelText = label.textContent.toLowerCase();

      if (labelText.includes("inicial")) {
        filters.dataInicial = input.value;
      } else if (labelText.includes("final")) {
        filters.dataFinal = input.value;
      } else if (labelText.includes("produto")) {
        filters.produto = input.value;
      } else if (labelText.includes("serviço")) {
        filters.servico = input.value;
      } else if (labelText.includes("tipo")) {
        filters.tipoTarefa = input.value;
      } else if (labelText.includes("colaborador")) {
        filters.colaborador = input.value;
      }
    });

    console.log("Filters applied:", filters);

    // Here you can add logic to filter the data
    // For now, we'll just show a message
    alert("Consulta realizada com os filtros selecionados");
  });

  // Animate circular charts and percentages on load
  function animateCharts() {
    const circles = document.querySelectorAll(".circle");
    circles.forEach((circle) => {
      const dashArray = circle.getAttribute("stroke-dasharray");
      const percentage = dashArray.split(",")[0];
      circle.style.strokeDasharray = `${percentage}, 100`;
    });

    // Animate percentages simultaneously with charts ONLY if they have real data-target values
    animatePercentagesWithRealData();
  }

  // Animate percentage counters with real data only
  function animatePercentagesWithRealData() {
    const percentageElements = document.querySelectorAll(
      ".percentage[data-target]"
    );

    percentageElements.forEach((element) => {
      const targetValue = parseInt(element.getAttribute("data-target"));

      // Only animate if we have a real value (not the initial 0)
      if (targetValue > 0) {
        let currentValue = 0;
        const increment = targetValue / 50; // 50 frames for smooth but faster animation
        const duration = 1000; // 1 second (reduced from 2 seconds)
        const stepTime = duration / 50;

        const timer = setInterval(() => {
          currentValue += increment;
          if (currentValue >= targetValue) {
            currentValue = targetValue;
            clearInterval(timer);
          }
          element.textContent = Math.round(currentValue) + "%";
        }, stepTime);
      }
    });
  }

  // Legacy function for compatibility - remove initial animation
  function animatePercentages() {
    // This function is now empty to avoid conflicts with real data animation
  }

  // Initialize chart tooltips
  initializeChartTooltips();

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
      }
      // Remove o else para não mostrar mensagens de erro desnecessárias
    })
    .catch((error) => {
      // Erro silencioso para não incomodar o usuário
      console.log("Sincronização de produtos não executada");
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
      }
      // Remove o else para não mostrar mensagens de erro desnecessárias
    })
    .catch((error) => {
      // Erro silencioso para não incomodar o usuário
      console.log("Sincronização de serviços não executada");
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
      }
      // Remove o else para não mostrar mensagens de erro desnecessárias
    })
    .catch((error) => {
      // Erro silencioso para não incomodar o usuário
      console.log("Sincronização de colaboradores não executada");
    });
}

// Função para carregar filtros
function loadFilters() {
  fetch("/api/dashboard/filters/options")
    .then((response) => response.json())
    .then((data) => {
      console.log("Dashboard - Dados de filtros carregados:", data);

      // Busca todos os filter-groups
      const filterGroups = document.querySelectorAll(".filter-group");

      filterGroups.forEach((group) => {
        const label = group.querySelector("label");
        const select = group.querySelector("select");

        if (!label || !select) return;

        const labelText = label.textContent.toLowerCase();

        // Limpa o select antes de popular
        select.innerHTML = "";

        // Determina qual dados usar baseado no label
        if (labelText.includes("produto")) {
          select.innerHTML = '<option value="">Todos os produtos</option>';
          if (data.produtos) {
            data.produtos.forEach((produto) => {
              const option = document.createElement("option");
              option.value = produto.id;
              option.textContent = produto.nome;
              select.appendChild(option);
            });
          }
        } else if (labelText.includes("serviço")) {
          select.innerHTML = '<option value="">Todos os serviços</option>';
          if (data.servicos) {
            data.servicos.forEach((servico) => {
              const option = document.createElement("option");
              option.value = servico.id;
              option.textContent = servico.nome;
              select.appendChild(option);
            });
          }
        } else if (labelText.includes("tipo")) {
          select.innerHTML = '<option value="">Todos os tipos</option>';
          if (data.tipos_tarefa) {
            data.tipos_tarefa.forEach((tipo) => {
              const option = document.createElement("option");
              option.value = tipo.id;
              option.textContent = tipo.nome;
              select.appendChild(option);
            });
          }
        } else if (labelText.includes("colaborador")) {
          select.innerHTML = '<option value="">Todos os colaboradores</option>';
          if (data.colaboradores) {
            data.colaboradores.forEach((colaborador) => {
              const option = document.createElement("option");
              option.value = colaborador.id;
              option.textContent = colaborador.nome;
              select.appendChild(option);
            });
          }
        }
      });
    })
    .catch((error) => {
      console.log("Dashboard - Erro ao carregar filtros:", error);
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
      console.log("Dados do dashboard não puderam ser carregados:", error);
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

  // Usa os percentuais que vêm do banco de dados
  const percentuais = data.percentuais || {};

  // FATURAMENTO TOTAL sempre deve ser 100%
  updatePercentageByLabel("FATURAMENTO TOTAL", 100);

  // Percentuais de participação no faturamento total
  updatePercentageByLabel(
    "FATURAMENTO PRODUTO",
    Math.round(percentuais.faturamento_produto || 0)
  );
  updatePercentageByLabel(
    "FATURAMENTO SERVIÇO",
    Math.round(percentuais.faturamento_servico || 0)
  );

  // Percentuais de margem de lucro (lucro/faturamento)
  updatePercentageByLabel(
    "LUCRO TOTAL",
    Math.round(percentuais.margem_lucro || 0)
  );
  updatePercentageByLabel(
    "LUCRO PRODUTO",
    Math.round(percentuais.lucro_produto || 0)
  );
  updatePercentageByLabel(
    "LUCRO SERVIÇO",
    Math.round(percentuais.lucro_servico || 0)
  );

  // Atualiza período se disponível
  if (data.periodo) {
    console.log(`Período: ${data.periodo.inicio} até ${data.periodo.fim}`);
  }

  // Inicia animações dos gráficos circulares após dados serem carregados
  // Agora as porcentagens são animadas dentro de updatePercentageByLabel
  setTimeout(() => {
    const circles = document.querySelectorAll(".circle");
    circles.forEach((circle) => {
      const dashArray = circle.getAttribute("stroke-dasharray");
      if (dashArray) {
        const percentage = dashArray.split(",")[0];
        circle.style.strokeDasharray = `${percentage}, 100`;
      }
    });
  }, 200);
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
        // Limpa qualquer animação anterior
        if (percentageText.animationTimer) {
          clearInterval(percentageText.animationTimer);
        }

        // Atualiza o data-target com o valor real
        const roundedPercentage = Math.round(percentage);
        percentageText.setAttribute("data-target", roundedPercentage);

        // Reseta para 0% antes de iniciar a animação
        percentageText.textContent = "0%";

        // Inicia animação do contador após um pequeno delay
        setTimeout(() => {
          animatePercentageElement(percentageText, roundedPercentage);
        }, 100);
      }
    }
  });
}

// Função para animar um elemento de porcentagem específico
function animatePercentageElement(element, targetValue) {
  let currentValue = 0;
  const increment = targetValue / 50; // 50 frames for smooth but faster animation
  const duration = 1000; // 1 second (reduced from 2 seconds)
  const stepTime = duration / 50;

  element.animationTimer = setInterval(() => {
    currentValue += increment;
    if (currentValue >= targetValue) {
      currentValue = targetValue;
      clearInterval(element.animationTimer);
      element.animationTimer = null;
    }
    element.textContent = Math.round(currentValue) + "%";
  }, stepTime);
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

// Chart Tooltip Functionality
function initializeChartTooltips() {
  // Create tooltip element
  const tooltip = document.createElement("div");
  tooltip.className = "chart-tooltip";
  document.body.appendChild(tooltip);

  // Add data attributes and event listeners to chart elements
  const metricCards = document.querySelectorAll(".metric-card");

  metricCards.forEach((card) => {
    const label = card.querySelector(".metric-label").textContent.trim();
    const circleProgress = card.querySelector(".circle");
    const circleBackground = card.querySelector(".circle-bg");

    // Add data attributes
    if (circleProgress) {
      circleProgress.setAttribute("data-label", label);
      circleProgress.setAttribute("data-type", "progress");
    }

    if (circleBackground) {
      circleBackground.setAttribute("data-label", label);
      circleBackground.setAttribute("data-type", "remaining");
    }

    // Add event listeners for progress circle (colored part)
    if (circleProgress) {
      circleProgress.addEventListener("mouseenter", (e) =>
        showTooltip(e, label, "progress")
      );
      circleProgress.addEventListener("mousemove", (e) =>
        updateTooltipPosition(e)
      );
      circleProgress.addEventListener("mouseleave", hideTooltip);
    }

    // Add event listeners for background circle (white part)
    if (circleBackground) {
      circleBackground.addEventListener("mouseenter", (e) =>
        showTooltip(e, label, "remaining")
      );
      circleBackground.addEventListener("mousemove", (e) =>
        updateTooltipPosition(e)
      );
      circleBackground.addEventListener("mouseleave", hideTooltip);
    }
  });
}

function showTooltip(event, label, type) {
  const tooltip = document.querySelector(".chart-tooltip");
  const card = event.target.closest(".metric-card");
  const percentageText = card.querySelector(".percentage");
  const valueText = card.querySelector(".metric-value");
  const percentage = parseInt(percentageText.textContent) || 0;
  const monetaryValue = valueText ? valueText.textContent : "";

  let tooltipText = "";

  if (type === "progress") {
    // Parte colorida do gráfico
    if (label.includes("FATURAMENTO")) {
      tooltipText = `${label}\n${percentage}% realizado\nValor: ${monetaryValue}`;
    } else if (label.includes("LUCRO")) {
      tooltipText = `${label}\n${percentage}% de margem\nValor: ${monetaryValue}`;
    }
  } else {
    // Parte branca do gráfico
    const remaining = 100 - percentage;
    if (label.includes("FATURAMENTO")) {
      tooltipText = `${label}\n${remaining}% restante para meta`;
    } else if (label.includes("LUCRO")) {
      tooltipText = `${label}\n${remaining}% de potencial não convertido`;
    }
  }

  tooltip.innerHTML = tooltipText.replace(/\n/g, "<br>");
  tooltip.classList.add("visible");
  updateTooltipPosition(event);
}

function updateTooltipPosition(event) {
  const tooltip = document.querySelector(".chart-tooltip");
  const rect = tooltip.getBoundingClientRect();
  const x = event.clientX;
  const y = event.clientY;

  // Position tooltip above the cursor with some offset
  let left = x - rect.width / 2;
  let top = y - rect.height - 10;

  // Adjust if tooltip goes outside viewport
  if (left < 5) left = 5;
  if (left + rect.width > window.innerWidth - 5)
    left = window.innerWidth - rect.width - 5;
  if (top < 5) top = y + 20; // Show below cursor if no space above

  tooltip.style.left = left + "px";
  tooltip.style.top = top + "px";
}

function hideTooltip() {
  const tooltip = document.querySelector(".chart-tooltip");
  tooltip.classList.remove("visible");
}

// Função de fallback com dados mock em caso de erro
function loadMockData() {
  console.log("Carregando dados mock...");
  const mockData = {
    faturamento_total: 1840.0,
    lucro_total: 1420.0,
    faturamento_produto: 840.0,
    faturamento_servico: 1000.0,
    lucro_produto: 420.0,
    lucro_servico: 1000.0,
    percentuais: {
      margem_lucro: 77.0, // 1420/1840 * 100
      faturamento_produto: 45.7, // 840/1840 * 100
      faturamento_servico: 54.3, // 1000/1840 * 100
      lucro_produto: 50.0, // 420/840 * 100 (margem do produto)
      lucro_servico: 100.0, // 1000/1000 * 100 (margem do serviço)
    },
  };
  updateDashboardDisplay(mockData);
}
