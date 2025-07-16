/**
 * Filtros Centralizados - JavaScript
 *
 * Este arquivo contém todas as funcionalidades relacionadas aos filtros
 * que são compartilhadas entre o Dashboard e o Relatório de Tarefas.
 */

// Classe para gerenciar filtros centralizados
class FilterManager {
  constructor() {
    // REMOVIDO: this.apiUrl = "/api/filters/options"; (API não existe mais)
    this.initialized = false;
  }

  /**
   * Inicializa os filtros para a página atual
   * @param {string} pageType - Tipo da página ('dashboard' ou 'relatorio')
   */
  async initialize(pageType = "dashboard") {
    try {
      this.pageType = pageType;
      // REMOVIDO: await this.loadFilterOptions(); (API não existe mais)
      this.setupDateDefaults();
      this.initialized = true;
      console.log(`✅ Filtros inicializados para ${pageType}`);
    } catch (error) {
      console.error("❌ Erro ao inicializar filtros:", error);
    }
  }

  /**
   * REMOVIDO: Carrega as opções dos filtros da API
   * Os filtros agora são carregados diretamente no HTML pelo servidor
   */
  // async loadFilterOptions() {
  //   // REMOVIDA: Carregamento via API não é mais necessário
  // }

  /**
   * REMOVIDO: Popula os selects com as opções de filtros
   * Os selects agora são populados diretamente no HTML pelo servidor
   */
  // populateFilterSelects(data) {
  //   // REMOVIDA: Função não é mais necessária
  // }

  /**
   * Atualiza um select com as opções fornecidas
   * @param {HTMLSelectElement} select - Elemento select a ser atualizado
   * @param {Array} options - Array de opções
   * @param {string} defaultText - Texto da opção padrão
   */
  updateSelectWithOptions(select, options, defaultText) {
    // Limpa opções existentes
    select.innerHTML = `<option value="">${defaultText}</option>`;

    // Adiciona novas opções se existirem
    if (options && Array.isArray(options)) {
      options.forEach((option) => {
        const optionElement = document.createElement("option");
        optionElement.value = option.id;
        optionElement.textContent = option.nome;
        select.appendChild(optionElement);
      });
    }
  }

  /**
   * Define datas padrão para os campos de data
   */
  setupDateDefaults() {
    const today = new Date().toISOString().split("T")[0];
    const dateInputs = document.querySelectorAll('input[type="date"]');

    dateInputs.forEach((input) => {
      if (!input.value) {
        input.value = today;
      }
    });
  }

  /**
   * Coleta os valores dos filtros baseado nos labels
   * @returns {Object} Objeto com os valores dos filtros
   */
  collectFilterValues() {
    const filters = {};
    const filterGroups = document.querySelectorAll(".filter-group");

    filterGroups.forEach((group) => {
      const label = group.querySelector("label");
      const input = group.querySelector("input, select");

      if (!label || !input) return;

      const labelText = label.textContent.toLowerCase().trim();

      // Mapeia os labels para as chaves dos filtros
      if (labelText.includes("inicial")) {
        filters.data_inicial = input.value;
      } else if (labelText.includes("final")) {
        filters.data_final = input.value;
      } else if (labelText.includes("produto")) {
        filters.produto = input.value;
      } else if (labelText.includes("serviço")) {
        filters.servico = input.value;
      } else if (labelText.includes("tipo")) {
        filters.tipo_tarefa = input.value;
      } else if (labelText.includes("colaborador")) {
        filters.colaborador = input.value;
      }
    });

    // Remove valores vazios
    Object.keys(filters).forEach((key) => {
      if (!filters[key]) {
        delete filters[key];
      }
    });

    return filters;
  }

  /**
   * Recarrega os filtros (útil após sincronização de dados)
   */
  async reload() {
    if (this.initialized) {
      try {
        await this.loadFilterOptions();
        console.log("🔄 Filtros recarregados com sucesso");
      } catch (error) {
        console.error("❌ Erro ao recarregar filtros:", error);
      }
    }
  }

  /**
   * Valida se os filtros obrigatórios estão preenchidos
   * @returns {Object} Resultado da validação
   */
  validateFilters() {
    const filters = this.collectFilterValues();
    const errors = [];

    // Validação de data inicial e final
    if (filters.data_inicial && filters.data_final) {
      const dataInicial = new Date(filters.data_inicial);
      const dataFinal = new Date(filters.data_final);

      if (dataInicial > dataFinal) {
        errors.push("A data inicial não pode ser maior que a data final");
      }
    }

    return {
      isValid: errors.length === 0,
      errors: errors,
      filters: filters,
    };
  }

  /**
   * Aplica filtros e executa callback
   * @param {Function} callback - Função a ser executada com os filtros
   */
  applyFilters(callback) {
    const validation = this.validateFilters();

    if (validation.isValid) {
      console.log("Filtros aplicados:", validation.filters);
      if (typeof callback === "function") {
        callback(validation.filters);
      }
    } else {
      console.error("Erros de validação:", validation.errors);
      alert("Erro nos filtros: " + validation.errors.join(", "));
    }
  }

  /**
   * Limpa todos os filtros
   */
  clearFilters() {
    const filterGroups = document.querySelectorAll(".filter-group");

    filterGroups.forEach((group) => {
      const input = group.querySelector("input, select");
      if (input) {
        if (input.type === "date") {
          const today = new Date().toISOString().split("T")[0];
          input.value = today;
        } else {
          input.value = "";
        }
      }
    });

    console.log("🧹 Filtros limpos");
  }
}

// Instância global do gerenciador de filtros
window.filterManager = new FilterManager();

// Funções utilitárias globais para compatibilidade
window.loadFilters = function () {
  return window.filterManager.reload();
};

window.loadFilterOptions = function () {
  return window.filterManager.reload();
};

window.getFilterValues = function () {
  return window.filterManager.collectFilterValues();
};

window.clearAllFilters = function () {
  window.filterManager.clearFilters();
};

// Auto-inicialização quando o DOM estiver pronto
document.addEventListener("DOMContentLoaded", function () {
  // Detecta o tipo de página baseado na URL
  const path = window.location.pathname;
  let pageType = "dashboard";

  if (path.includes("relatorio-tarefas")) {
    pageType = "relatorio";
  }

  // Inicializa filtros automaticamente
  window.filterManager.initialize(pageType);
});

// Exporta para uso em módulos ES6 se necessário
if (typeof module !== "undefined" && module.exports) {
  module.exports = { FilterManager };
}
