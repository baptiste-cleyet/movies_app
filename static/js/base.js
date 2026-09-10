import { createIcons, icons } from "./icons.js";

const root = document.documentElement;
let theme =
    document.cookie
        .split("; ")
        .find((row) => row.startsWith("theme="))
        ?.split("=")[1] || "light";
root.setAttribute("data-theme", theme);

let id_themes;
let events_id;

document.addEventListener("DOMContentLoaded", function () {
    id_themes = {
        light: ["light-mode-li", "light-mode-mobile-li"],
        dark: ["dark-mode-li", "dark-mode-mobile-li"],
    };
    events_id = ["light-mode", "light-mode-mobile", "dark-mode", "dark-mode-mobile"];
    events_id.forEach((id) => {
        const el = document.getElementById(id);
        if (el) el.addEventListener("click", toggleDarkMode);
    });
    if (id_themes[theme]) {
        id_themes[theme].forEach((id) => {
            const el = document.getElementById(id);
            if (el) el.classList.add("hidden");
        });
        id_themes[theme === "dark" ? "light" : "dark"].forEach((id) => {
            const el = document.getElementById(id);
            if (el) el.classList.remove("hidden");
        });
    }
    // mobile menu outside click
    const container = document.getElementById("mobile-menu");
    const menu = document.getElementById("mobile-ul");
    if (container && menu) {
        window.addEventListener("click", (e) => {
            if (!container.contains(e.target)) {
                menu.classList.add("hidden");
            }
        });
    }
    // delegate menu-icon toggle (replaces inline onclick)
    const menuIcon = document.getElementById("menu-icon");
    if (menuIcon && menu) {
        menuIcon.addEventListener("click", () => toggleHidden(menu));
    }
    // live autocomplete handler (debounced input)
    const titleInput = document.getElementById("title");
    const posterContainer = document.getElementById("corresponding-poster");
    if (titleInput && posterContainer) {
        let debounceTimer;
        let abortController;
        titleInput.addEventListener("input", () => {
            clearTimeout(debounceTimer);
            const value = titleInput.value.trim();
            if (value.length < 2) {
                posterContainer.innerHTML = "";
                const hid = document.getElementById("movie_add");
                if (hid) hid.value = "";
                updateAutocompleteSubmit();
                return;
            }
            if (abortController) abortController.abort();
            abortController = new AbortController();
            debounceTimer = setTimeout(() => {
                addSearchPosters(value, posterContainer, abortController.signal);
            }, 300);
        });
        // keyboard: Escape clears
        titleInput.addEventListener("keydown", (e) => {
            if (e.key === "Escape") {
                posterContainer.innerHTML = "";
            }
        });
    }

    updateScoreColors();
    createIcons({ icons });
});

export function toggleDarkMode() {
    const currentTheme = root.getAttribute("data-theme");
    const newTheme = currentTheme === "dark" ? "light" : "dark";
    root.setAttribute("data-theme", newTheme);
    document.cookie = `theme=${newTheme};path=/;max-age=31536000`;
    if (id_themes) {
        id_themes[newTheme].forEach((id) => {
            const el = document.getElementById(id);
            if (el) el.classList.add("hidden");
        });
        id_themes[currentTheme].forEach((id) => {
            const el = document.getElementById(id);
            if (el) el.classList.remove("hidden");
        });
    }
    theme = newTheme;
}

export function getColor(score) {
    const r = score < 80 ? 255 : Math.floor(255 - (score - 80) * 8);
    const g = score > 80 ? 255 : Math.floor(score * 3);
    return `rgb(${r},${g},0)`;
}

export function updateScoreColors() {
    const noteElements = document.querySelectorAll(".score");
    noteElements.forEach((noteTxt) => {
        const scoreText = noteTxt.textContent.trim();
        const score = parseFloat(scoreText.replace("%", ""));
        if (!isNaN(score)) noteTxt.style.color = getColor(score);
    });
}

export function toggleHidden(element) {
    element.classList.toggle("hidden");
}

export function toggleActive(element) {
    element.classList.toggle("active");
}

// Shared modal helpers (moved from grid.js / movie_detail.js)
export function addOpeners(modalElements) {
    for (const element of modalElements) {
        for (const but of element["buttons"]) {
            if (but) but.addEventListener("click", () => element["modal"].classList.remove("hidden"));
        }
    }
}

export function addClosers(modalElements) {
    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape") {
            for (const element of modalElements) {
                element["modal"].classList.add("hidden");
            }
        }
    });
    for (const element of modalElements) {
        document.addEventListener("mousedown", function (event) {
            if (event.target === element["modal"]) {
                element["modal"].classList.add("hidden");
            }
        });
    }
}

// Grid helpers
export function sortMovies(movies, criterion = "date-sort", increasing = false) {
    const sortFunctions = {
        "rating-sort": (a, b) => a.rating - b.rating,
        "title-sort": (a, b) => a.title.localeCompare(b.title),
        "date-sort": (a, b) => new Date(a.date) - new Date(b.date),
        "year-sort": (a, b) => a.year - b.year,
    };
    if (!sortFunctions[criterion]) {
        console.warn(`Critère de tri inconnu : ${criterion}, tri par date par défaut.`);
        return movies;
    }
    return movies.sort((a, b) => {
        const result = sortFunctions[criterion](a, b);
        return increasing ? result : -result;
    });
}

export function search(movies, title) {
    const correpondingMovies = [];
    movies.forEach((movie) => {
        if (movie.title.toLowerCase().includes(title.toLowerCase())) {
            correpondingMovies.push(movie);
        }
    });
    return correpondingMovies;
}

function ensureTooltip() {
    let tip = document.getElementById("autocomplete-tooltip");
    if (!tip) {
        tip = document.createElement("div");
        tip.id = "autocomplete-tooltip";
        tip.style.position = "fixed";
        tip.style.pointerEvents = "none";
        tip.style.zIndex = "9999";
        tip.style.background = "rgba(0,0,0,0.85)";
        tip.style.color = "white";
        tip.style.padding = "6px 8px";
        tip.style.borderRadius = "6px";
        tip.style.fontSize = "12px";
        tip.style.lineHeight = "1.2";
        tip.style.maxWidth = "160px";
        tip.style.display = "none";
        tip.style.boxShadow = "0 4px 12px rgba(0,0,0,0.3)";
        document.body.appendChild(tip);
    }
    return tip;
}

function updateAutocompleteSubmit() {
    const hid = document.getElementById("movie_add");
    const val = hid ? hid.value : "";
    document.querySelectorAll("#watchlist-submit, #grid-submit").forEach((btn) => {
        if (btn) btn.disabled = !val;
    });
}

export function addSearchPosters(title, posterContainer, signal) {
    if (!posterContainer) return;
    posterContainer.innerHTML = '<p class="col-span-3 text-center text-sm text-gray-500">Recherche...</p>';
    const hiddenInput = document.getElementById("movie_add");
    if (hiddenInput) hiddenInput.value = "";
    updateAutocompleteSubmit();
    fetch("/search_movie", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title: title }),
        signal,
    })
        .then((response) => response.json())
        .then((data) => {
            posterContainer.innerHTML = "";
            if (data.error) {
                posterContainer.innerHTML = `<p class="col-span-3 text-center text-sm">${data.error}</p>`;
                return;
            }
            if (typeof data.results === "string") {
                posterContainer.innerHTML = `<p class="col-span-3 text-center text-sm">${data.results}</p>`;
                return;
            }
            if (!data.results || data.results.length === 0) {
                posterContainer.innerHTML = '<p class="col-span-3 text-center text-sm">Aucun film trouvé</p>';
                return;
            }
            data.results.forEach((movie) => {
                const year = (movie.release_date || "").split("-")[0] || "";
                const card = document.createElement("div");
                card.className = "search-card cursor-pointer border-2 border-transparent rounded-lg text-center hover:border-(--secondary-color) transition flex-shrink-0 relative overflow-hidden";
                card.style.width = "110px";
                card.setAttribute("role", "option");
                card.dataset.id = movie.id;
                const imgSrc = movie.poster_path ? "https://image.tmdb.org/t/p/w500" + movie.poster_path : "";
                card.innerHTML = `${imgSrc ? `<img src="${imgSrc}" alt="${movie.title}" style="width:100%;height:110px;object-fit:cover;" class="rounded">` : `<div style="width:100%;height:110px;" class="bg-gray-300 rounded flex items-center justify-center text-xs">Pas d'affiche</div>`}`;
                const tooltip = ensureTooltip();
                const showTip = (e) => {
                    tooltip.innerHTML = `<div style="font-weight:600;">${movie.title}</div><div style="opacity:0.8;">${year}</div>`;
                    tooltip.style.display = "block";
                    const x = e.clientX + 12;
                    const y = e.clientY + 12;
                    // keep inside viewport
                    const rect = tooltip.getBoundingClientRect();
                    const maxX = window.innerWidth - rect.width - 8;
                    const maxY = window.innerHeight - rect.height - 8;
                    tooltip.style.left = Math.min(x, maxX) + "px";
                    tooltip.style.top = Math.min(y, maxY) + "px";
                };
                const moveTip = (e) => {
                    if (tooltip.style.display === "none") return;
                    const x = e.clientX + 12;
                    const y = e.clientY + 12;
                    const rect = tooltip.getBoundingClientRect();
                    const maxX = window.innerWidth - rect.width - 8;
                    const maxY = window.innerHeight - rect.height - 8;
                    tooltip.style.left = Math.min(x, maxX) + "px";
                    tooltip.style.top = Math.min(y, maxY) + "px";
                };
                const hideTip = () => { tooltip.style.display = "none"; };
                card.addEventListener("mouseenter", showTip);
                card.addEventListener("mousemove", moveTip);
                card.addEventListener("mouseleave", hideTip);
                card.addEventListener("click", () => {
                    posterContainer.querySelectorAll(".search-card").forEach((c) => c.classList.remove("ring-2", "ring-(--secondary-color)", "border-(--secondary-color)"));
                    card.classList.add("ring-2", "ring-(--secondary-color)", "border-(--secondary-color)");
                    if (hiddenInput) hiddenInput.value = movie.id;
                    updateAutocompleteSubmit();
                });
                posterContainer.appendChild(card);
            });
            createIcons({ icons });
        })
        .catch((err) => {
            if (err.name === "AbortError") return;
            console.error("Erreur :", err);
        });
}

// Keep globals for inline handlers (onclick="toggleHidden(...)" in base.html)
window.toggleHidden = toggleHidden;
window.toggleActive = toggleActive;
