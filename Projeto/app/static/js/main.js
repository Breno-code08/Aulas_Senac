document.addEventListener("click", (event) => {
    const addResourceButton = event.target.closest("[data-add-resource]");
    if (addResourceButton) {
        const list = document.getElementById(addResourceButton.dataset.addResource);
        const template = document.getElementById(addResourceButton.dataset.resourceTemplate);
        if (list && template) {
            const entry = template.content.firstElementChild.cloneNode(true);
            list.append(entry);
            updateContentEntryTitles();
            entry.querySelector("textarea, input")?.focus();
        }
    }

    const removeResourceButton = event.target.closest("[data-remove-resource]");
    if (removeResourceButton) {
        removeResourceButton.closest(".content-entry")?.remove();
        updateContentEntryTitles();
    }

    const closeButton = event.target.closest(".flash-close");
    if (closeButton) {
        closeButton.closest(".flash").remove();
    }
});

function updateContentEntryTitles() {
    document.querySelectorAll(".content-entry-heading h3").forEach((heading, index) => {
        heading.textContent = `Conteúdo ${index + 1}`;
    });
}

document.addEventListener("submit", (event) => {
    const form = event.target.closest("[data-confirm]");
    if (form && !window.confirm(form.dataset.confirm)) {
        event.preventDefault();
    }
});
