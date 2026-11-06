(() => {
    const storageKey = "study-theme";
    let theme = "dark";

    try {
        const savedTheme = localStorage.getItem(storageKey);
        if (savedTheme === "light" || savedTheme === "dark") {
            theme = savedTheme;
        }
    } catch (error) {
        theme = "dark";
    }

    document.documentElement.dataset.theme = theme;

    document.addEventListener("DOMContentLoaded", () => {
        const toggle = document.querySelector("[data-theme-toggle]");
        if (!toggle) {
            return;
        }

        const updateToggleLabel = () => {
            const nextTheme = document.documentElement.dataset.theme === "dark" ? "claro" : "escuro";
            toggle.setAttribute("aria-label", `Ativar tema ${nextTheme}`);
            toggle.title = `Ativar tema ${nextTheme}`;
            toggle.querySelector(".sidebar-label").textContent = `Tema ${nextTheme}`;
        };

        updateToggleLabel();
        toggle.addEventListener("click", () => {
            const nextTheme = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
            document.documentElement.dataset.theme = nextTheme;
            updateToggleLabel();
            try {
                localStorage.setItem(storageKey, nextTheme);
            } catch (error) {
                // Keep the selected theme for this page when browser storage is unavailable.
            }
        });
    });
})();
