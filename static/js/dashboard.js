// Prevenir execução múltipla do script
if (window.dashboardScriptLoaded) {
  console.log("Script já foi carregado, evitando duplicação");
  return;
}
window.dashboardScriptLoaded = true;
console.log("Carregando script do dashboard");

document.addEventListener("DOMContentLoaded", function () {
  console.log("DOM carregado, inicializando dashboard");

  // Flag global para controlar animações
  let animationsStarted = false;
  let dashboardInitialized = false;

  // Header Tab functionality
  const headerTabs = document.querySelectorAll(".header-tab");
  headerTabs.forEach((tab) => {
    tab.addEventListener("click", function () {
      headerTabs.forEach((t) => t.classList.remove("active"));
      this.classList.add("active");

      const tabType = this.dataset.tab;
      if (tabType === "geral") {
        window.location.href = "/dashboard";
      } else if (tabType === "detalhado") {
        window.location.href = "/relatorio-tarefas";
      }
    });
  });

  // Export Excel functionality
  const exportBtn = document.querySelector(".btn-export");
  if (exportBtn) {
    exportBtn.addEventListener("click", function () {
      console.log("Export Excel clicked");
      alert("Funcionalidade de exportação será implementada");
    });
  } else {
    console.log("Botão de exportação não encontrado");
  }

  // Initialize dashboard
  console.log("Chamando initializeDashboard()");
  initializeDashboard();

  // Tooltips functionality
  const tooltipEnabled = document.querySelectorAll(
    ".metric-card .chart-container"
  );
  tooltipEnabled.forEach((container) => {
    container.addEventListener("mouseenter", function (e) {
      const tooltip = document.createElement("div");
      tooltip.className = "chart-tooltip";
      tooltip.style.display = "none";
      document.body.appendChild(tooltip);
    });

    container.addEventListener("mouseleave", function () {
      const tooltip = document.querySelector(".chart-tooltip");
      if (tooltip) {
        tooltip.remove();
      }
    });
  });

  // Função para inicializar gráficos
  function initializeCharts() {
    console.log("Inicializando gráficos");
    const progressCircles = document.querySelectorAll(".circular-chart");
    console.log(`Encontrados ${progressCircles.length} círculos`);

    progressCircles.forEach((circle, index) => {
      const circleProgress = circle.querySelector(".circle");

      if (circleProgress && !circleProgress.getAttribute("data-initialized")) {
        console.log(`Inicializando círculo ${index}`);
        circleProgress.setAttribute("data-initialized", "true");

        const radius = 15.9155;
        const circumference = 2 * Math.PI * radius;

        circleProgress.style.animation = "none";
        circleProgress.style.strokeDasharray = circumference;
        circleProgress.style.strokeDashoffset = circumference;
        circleProgress.removeAttribute("stroke-dasharray");
        circleProgress.getBoundingClientRect();

        console.log(
          `Círculo ${index} inicializado com circunferência: ${circumference}`
        );
      }
    });
  }

  // Função para inicializar tooltips
  function initializeTooltips() {
    const progressCircles = document.querySelectorAll(".circular-chart");
    progressCircles.forEach((circle) => {
      const card = circle.closest(".metric-card");
      const label = card.querySelector(".metric-label").textContent;
      const circleProgress = circle.querySelector(".circle");
      const circleBackground = circle.querySelector(".circle-bg");

      if (circleProgress) {
        circleProgress.addEventListener("mouseenter", (e) =>
          showTooltip(e, label, "progress")
        );
        circleProgress.addEventListener("mousemove", (e) =>
          updateTooltipPosition(e)
        );
        circleProgress.addEventListener("mouseleave", hideTooltip);
      }

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

  // Função para mostrar tooltip
  function showTooltip(event, label, type) {
    const tooltip = document.querySelector(".chart-tooltip");
    const card = event.target.closest(".metric-card");
    const percentageText = card.querySelector(".percentage");
    const percentage = parseInt(percentageText.textContent) || 0;

    let tooltipText = "";
    if (type === "progress") {
      tooltipText = `${label}: ${percentage}%`;
    } else if (type === "remaining") {
      tooltipText = `${label}: ${100 - percentage}% restante`;
    }

    tooltip.innerHTML = tooltipText.replace(/\n/g, "<br>");
    tooltip.classList.add("visible");
    updateTooltipPosition(event);
  }

  // Função para atualizar posição do tooltip
  function updateTooltipPosition(event) {
    const tooltip = document.querySelector(".chart-tooltip");
    const rect = tooltip.getBoundingClientRect();
    const x = event.clientX;
    const y = event.clientY;

    let left = x - rect.width / 2;
    let top = y - rect.height - 10;

    if (left < 0) left = 0;
    if (left + rect.width > window.innerWidth)
      left = window.innerWidth - rect.width;
    if (top < 0) top = y + 10;

    tooltip.style.left = left + "px";
    tooltip.style.top = top + "px";
  }

  // Função para esconder tooltip
  function hideTooltip() {
    const tooltip = document.querySelector(".chart-tooltip");
    if (tooltip) {
      tooltip.classList.remove("visible");
    }
  }

  // Função para inicializar dashboard
  function initializeDashboard() {
    console.log("=== Inicializando dashboard ===");

    if (dashboardInitialized) {
      console.log("Dashboard já foi inicializado, saindo...");
      return;
    }

    dashboardInitialized = true;
    console.log("Dashboard sendo inicializado pela primeira vez");

    // Inicializar gráficos
    initializeCharts();

    // Inicializar tooltips
    initializeTooltips();

    // Iniciar animações após um delay
    setTimeout(() => {
      console.log("=== Iniciando animações ===");
      startAnimations();
    }, 1000);
  }

  // Função simplificada para iniciar animações
  function startAnimations() {
    console.log("Função startAnimations chamada");

    const percentageElements = document.querySelectorAll(".percentage");
    console.log(
      `Encontrados ${percentageElements.length} elementos de percentual`
    );

    percentageElements.forEach((element, index) => {
      const currentText = element.textContent.trim();
      const targetValue = parseInt(currentText.replace("%", "")) || 0;

      console.log(
        `Elemento ${index}: texto="${currentText}", valor alvo=${targetValue}%`
      );

      const delay = index * 300;

      setTimeout(() => {
        console.log(`Iniciando animação para elemento ${index}`);

        // Animar texto
        animatePercentageElement(element, targetValue);

        // Animar círculo
        setTimeout(() => {
          const card = element.closest(".metric-card");
          const circleElement = card ? card.querySelector(".circle") : null;
          if (circleElement) {
            console.log(`Animando círculo para elemento ${index}`);
            animateCircleElement(circleElement, targetValue, 0);
          } else {
            console.log(`Círculo não encontrado para elemento ${index}`);
          }
        }, 100);
      }, delay);
    });
  }

  // Função para animar elemento de percentagem
  function animatePercentageElement(element, targetValue) {
    console.log(`Animando percentual para ${targetValue}%`);
    const startValue = 0;
    const duration = 1200;
    const startTime = Date.now();

    function easeOut(t) {
      return 1 - Math.pow(1 - t, 3);
    }

    element.textContent = "0%";

    function animate() {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const easedProgress = easeOut(progress);
      const currentValue = Math.round(
        startValue + (targetValue - startValue) * easedProgress
      );

      element.textContent = currentValue + "%";

      if (progress < 1) {
        requestAnimationFrame(animate);
      } else {
        console.log(`Animação do percentual concluída para ${targetValue}%`);
      }
    }

    animate();
  }

  // Função para animar elemento de círculo
  function animateCircleElement(circle, targetValue, delay = 0) {
    if (circle.getAttribute("data-circle-animating") === "true") {
      return;
    }

    console.log(`Animando círculo para ${targetValue}%`);
    circle.setAttribute("data-circle-animating", "true");

    const radius = 15.9155;
    const circumference = 2 * Math.PI * radius;
    const duration = 1500;

    circle.style.animation = "none";
    circle.style.transition = "none";
    circle.style.strokeDasharray = circumference;
    circle.style.strokeDashoffset = circumference;
    circle.removeAttribute("stroke-dasharray");
    circle.getBoundingClientRect();

    function easeOut(t) {
      return 1 - Math.pow(1 - t, 3);
    }

    setTimeout(() => {
      const startTime = Date.now();
      const finalOffset = circumference - (targetValue / 100) * circumference;

      console.log(
        `Circunferência: ${circumference}, Offset final para ${targetValue}%: ${finalOffset}`
      );

      function animate() {
        const elapsed = Date.now() - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const easedProgress = easeOut(progress);
        const currentOffset =
          circumference - (circumference - finalOffset) * easedProgress;

        circle.style.strokeDashoffset = currentOffset;

        if (progress < 1) {
          requestAnimationFrame(animate);
        } else {
          circle.setAttribute("data-circle-animating", "false");
          console.log(`Animação do círculo concluída para ${targetValue}%`);
        }
      }

      animate();
    }, delay);
  }

  // Função para atualizar dashboard
  function updateDashboard() {
    const filters = {
      data_inicio: document.querySelector("#data-inicio")?.value || "",
      data_fim: document.querySelector("#data-fim")?.value || "",
      colaborador: document.querySelector("#colaborador")?.value || "",
      produto: document.querySelector("#produto")?.value || "",
      servico: document.querySelector("#servico")?.value || "",
      tipo_tarefa: document.querySelector("#tipo-tarefa")?.value || "",
    };

    const queryParams = new URLSearchParams();
    Object.keys(filters).forEach((key) => {
      if (filters[key]) {
        queryParams.append(key, filters[key]);
      }
    });

    const refreshUrl = `/dashboard/refresh?${queryParams.toString()}`;
    window.location.href = refreshUrl;
  }
}); // End of DOMContentLoaded

// Marcar que o script foi carregado e executado completamente
window.dashboardScriptExecuted = true;
