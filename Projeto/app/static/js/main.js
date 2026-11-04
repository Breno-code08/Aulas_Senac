document.addEventListener("click", (event) => {
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
