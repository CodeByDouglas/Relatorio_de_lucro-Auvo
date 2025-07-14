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

  // Load filter options from API
  loadFilterOptions();

  // Função para carregar opções dos filtros
  function loadFilterOptions() {
    fetch("/api/dashboard/filters/options")
      .then((response) => response.json())
      .then((data) => {
        console.log("Dados dos filtros recebidos:", data);

        // Popular filtros corretamente identificando cada campo pelo label
        const filterGroups = document.querySelectorAll(".filter-group");
        filterGroups.forEach((group) => {
          const label = group.querySelector("label");
          const select = group.querySelector("select");

          if (label && select) {
            const labelText = label.textContent.toLowerCase().trim();

            if (labelText.includes("produto")) {
              // Limpa opções existentes exceto a primeira
              while (select.children.length > 1) {
                select.removeChild(select.lastChild);
              }

              data.produtos.forEach((produto) => {
                const option = document.createElement("option");
                option.value = produto.id;
                option.textContent = produto.nome;
                select.appendChild(option);
              });
            } else if (labelText.includes("serviço")) {
              // Limpa opções existentes exceto a primeira
              while (select.children.length > 1) {
                select.removeChild(select.lastChild);
              }

              data.servicos.forEach((servico) => {
                const option = document.createElement("option");
                option.value = servico.id;
                option.textContent = servico.nome;
                select.appendChild(option);
              });
            } else if (labelText.includes("tipo")) {
              // Limpa opções existentes exceto a primeira
              while (select.children.length > 1) {
                select.removeChild(select.lastChild);
              }

              data.tipos_tarefa.forEach((tipo) => {
                const option = document.createElement("option");
                option.value = tipo.id;
                option.textContent = tipo.nome;
                select.appendChild(option);
              });
            } else if (labelText.includes("colaborador")) {
              // Limpa opções existentes exceto a primeira
              while (select.children.length > 1) {
                select.removeChild(select.lastChild);
              }

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
        console.error("Erro ao carregar opções de filtro:", error);
      });
  }

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
    fetch("/api/dashboard/detailed-data?" + new URLSearchParams(filters))
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
