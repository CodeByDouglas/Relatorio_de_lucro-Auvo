document.addEventListener("DOMContentLoaded", function () {
  // Função para alternar entre as abas do header
  const headerTabs = document.querySelectorAll(".header-tab");

  headerTabs.forEach((tab) => {
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
  if (exportBtn) {
    exportBtn.addEventListener("click", function () {
      console.log("Export Excel clicked - Relatório Detalhado");
      // Implementar lógica específica para exportar tabela
      exportTableToExcel();
    });
  }

  // Consultar button functionality
  const consultarBtn = document.querySelector(".btn-consultar");
  if (consultarBtn) {
    consultarBtn.addEventListener("click", function () {
      // Get filter values using FilterManager
      const filters = filterManager.collectFilterValues();
      console.log("Filters applied:", filters);

      // Fazer requisição para API
      fetchDetailedData(filters);
    });
  }

  // Set current date as default for date inputs
  const today = new Date().toISOString().split("T")[0];
  const dateInputs = document.querySelectorAll('input[type="date"]');
  dateInputs.forEach((input) => {
    if (!input.value) {
      input.value = today;
    }
  });

  // Initialize FilterManager and load filter options
  const filterManager = new FilterManager();
  filterManager.initialize();

  // Função para exportar tabela para Excel
  function exportTableToExcel() {
    const table = document.querySelector(".data-table");
    const rows = [];

    // Cabeçalho
    const headers = Array.from(table.querySelectorAll("th")).map(
      (th) => th.textContent
    );
    rows.push(headers);

    // Dados
    const dataRows = Array.from(table.querySelectorAll("tbody tr"));
    dataRows.forEach((row) => {
      const cells = Array.from(row.querySelectorAll("td")).map(
        (td) => td.textContent
      );
      rows.push(cells);
    });

    console.log("Dados para exportação:", rows);
    alert("Funcionalidade de exportação da tabela será implementada");
  }

  // Função para buscar dados detalhados
  function fetchDetailedData(filters) {
    // Implementar chamada para API
    fetch("/api/relatorio/detailed-data?" + new URLSearchParams(filters))
      .then((response) => response.json())
      .then((data) => {
        console.log("Dados recebidos:", data);
        updateTable(data);
      })
      .catch((error) => {
        console.error("Erro ao buscar dados:", error);
        alert("Erro ao consultar dados");
      });
  }

  // Função para atualizar a tabela
  function updateTable(data) {
    const tbody = document.querySelector(".data-table tbody");
    tbody.innerHTML = "";

    data.forEach((item) => {
      const row = document.createElement("tr");
      row.innerHTML = `
                <td>${item.cliente}</td>
                <td>${item.tipo_tarefa}</td>
                <td>${item.data}</td>
                <td>${item.produto}</td>
                <td class="lucro-value">R$ ${item.lucro}</td>
            `;
      tbody.appendChild(row);
    });
  }
});
