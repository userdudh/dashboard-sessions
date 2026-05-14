(function () {
  const meses = {
    "January": "Janeiro",
    "February": "Fevereiro",
    "March": "Março",
    "April": "Abril",
    "May": "Maio",
    "June": "Junho",
    "July": "Julho",
    "August": "Agosto",
    "September": "Setembro",
    "October": "Outubro",
    "November": "Novembro",
    "December": "Dezembro",
  };

  const dias = {
    "Su": "dom",
    "Mo": "seg",
    "Tu": "ter",
    "We": "qua",
    "Th": "qui",
    "Fr": "sex",
    "Sa": "sáb",
  };

  function traduzirTexto(texto) {
    const limpo = texto.trim();

    if (dias[limpo]) {
      return dias[limpo];
    }

    for (const mesIngles in meses) {
      if (limpo.startsWith(mesIngles + " ")) {
        return limpo.replace(mesIngles, meses[mesIngles]);
      }
    }

    return texto;
  }

  function traduzirCalendario() {
    const walker = document.createTreeWalker(
      document.body,
      NodeFilter.SHOW_TEXT
    );

    const nodes = [];

    while (walker.nextNode()) {
      nodes.push(walker.currentNode);
    }

    nodes.forEach((node) => {
      const original = node.nodeValue;
      const traduzido = traduzirTexto(original);

      if (original !== traduzido) {
        node.nodeValue = traduzido;
      }
    });
  }

  window.addEventListener("load", function () {
    traduzirCalendario();

    const observer = new MutationObserver(function () {
      traduzirCalendario();
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true,
      characterData: true,
    });
  });
})();