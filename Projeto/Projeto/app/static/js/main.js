document.addEventListener("click", (event) => {
    const removePrimaryContentButton = event.target.closest("[data-remove-primary-content]");
    if (removePrimaryContentButton && window.confirm("Remover o conteúdo principal? Você poderá salvar a matéria se houver outro conteúdo escrito.")) {
        const form = removePrimaryContentButton.closest("form");
        form.querySelector('[name="content"]').value = "";
        form.querySelector('[name="remove_primary_content"]').value = "1";
        removePrimaryContentButton.remove();
    }

    const addResourceButton = event.target.closest("[data-add-resource]");
    if (addResourceButton) {
        const list = document.getElementById(addResourceButton.dataset.addResource);
        const template = document.getElementById(addResourceButton.dataset.resourceTemplate);
        if (list && template) {
            const entry = template.content.firstElementChild.cloneNode(true);
            list.append(entry);
            entry.querySelector("textarea, input")?.focus();
        }
    }

    const removeResourceButton = event.target.closest("[data-remove-resource]");
    if (removeResourceButton) {
        removeResourceButton.closest(".repeatable-entry")?.remove();
    }

    const closeButton = event.target.closest(".flash-close");
    if (closeButton) {
        closeButton.closest(".flash").remove();
    }
});

document.addEventListener("submit", (event) => {
    const form = event.target.closest("[data-confirm]");
    if (form && !window.confirm(form.dataset.confirm)) {
        event.preventDefault();
    }
});
