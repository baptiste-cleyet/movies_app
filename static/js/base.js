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
    // menu mobile plein écran : pilule = ouvre/ferme, overlay = échappe + clic fond/item
    // état porté par la classe .open (CSS custom), pas .hidden (écrasée par .mobile-overlay)
    const menuBtn = document.getElementById("menu-icon");
    const overlay = document.getElementById("mobile-ul");
    const closeBtn = document.getElementById("menu-close");
    const setMenu = (openKeep) => {
        if (!overlay) return;
        overlay.classList.toggle("open", openKeep);
        document.body.classList.toggle("overflow-hidden", openKeep);
        overlay.setAttribute("aria-hidden", String(!openKeep));
        menuBtn?.setAttribute("aria-expanded", String(openKeep));
    };
    if (menuBtn && overlay) {
        menuBtn.addEventListener("click", () => setMenu(!overlay.classList.contains("open")));
        closeBtn?.addEventListener("click", () => setMenu(false));
        overlay.addEventListener("click", (e) => {
            const onLink = e.target.closest("a");
            // bascule de thème : le menu reste ouvert pour voir le changement
            if (onLink && onLink.id.endsWith("-mode-mobile")) return;
            if (e.target === overlay || onLink) setMenu(false);
        });
        document.addEventListener("keydown", (e) => {
            if (e.key === "Escape" && overlay.classList.contains("open")) setMenu(false);
        });
        // marque l'item de la page courante
        overlay.querySelectorAll("a[href]").forEach((a) => {
            const href = a.getAttribute("href");
            if (href && !href.startsWith("http") && href === window.location.pathname) {
                a.classList.add("current");
            }
        });
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

    // Summary/Review length warning (>4500/5000) - select textareas only, not <p> with same id on detail page
    ["summary", "review"].forEach((field) => {
        // Handle both add and update modals; use textarea selector to avoid <p id="summary"> collision
        const tas = document.querySelectorAll(`textarea[name="${field}"]`);
        if (tas.length === 0) return;
        tas.forEach((ta) => {
            // Find warning/count relative to this textarea: look in same form or next sibling
            const form = ta.closest("form");
            const warning = form ? form.querySelector(`#${field}-warning`) : document.getElementById(`${field}-warning`);
            const countEl = form ? form.querySelector(`#${field}-count`) : document.getElementById(`${field}-count`);
            // Fallback to global warning if form-scoped not found (handles duplicate IDs)
            const warningEl = warning || document.getElementById(`${field}-warning`);
            const countElement = countEl || document.getElementById(`${field}-count`);
            if (!warningEl) return;
            function check() {
                const len = (ta.value || "").length;
                if (countElement) countElement.textContent = len;
                if (len > 4500) {
                    warningEl.classList.remove("hidden");
                    if (len >= 5000) {
                        warningEl.classList.add("text-red-600");
                        warningEl.classList.remove("text-amber-500");
                    } else {
                        warningEl.classList.add("text-amber-500");
                        warningEl.classList.remove("text-red-600");
                    }
                } else {
                    warningEl.classList.add("hidden");
                }
            }
            ta.addEventListener("input", check);
            check();
        });
    });
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
    document.addEventListener("mousedown", function (event) {
        for (const element of modalElements) {
            // Search modal stays when clicking outside (per UX requirement)
            if (element["modal"].id === "search-modal") continue;
            if (event.target === element["modal"]) {
                element["modal"].classList.add("hidden");
            }
        }
    });
}

// Grid helpers
export function sortMovies(movies, criterion = "date-sort", increasing = false) {
    const sortFunctions = {
        "rating-sort": (a, b) => (a.rating ?? -1) - (b.rating ?? -1),
        "title-sort": (a, b) => a.title.localeCompare(b.title),
        "date-sort": (a, b) => new Date(a.date) - new Date(b.date),
        "year-sort": (a, b) => (a.year ?? 0) - (b.year ?? 0),
    };
    if (!sortFunctions[criterion]) {
        console.warn(`Critère de tri inconnu : ${criterion}, tri par date par défaut.`);
        return movies;
    }
    return [...movies].sort((a, b) => {
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

function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
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
    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;
    fetch("/search_movie", {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-CSRFToken": csrfToken || "" },
        body: JSON.stringify({ title: title }),
        signal,
    })
        .then((response) => response.json())
        .then((data) => {
            posterContainer.innerHTML = "";
            if (data.error) {
                posterContainer.innerHTML = `<p class="col-span-3 text-center text-sm">${escapeHtml(data.error)}</p>`;
                return;
            }
            if (typeof data.results === "string") {
                posterContainer.innerHTML = `<p class="col-span-3 text-center text-sm">${escapeHtml(data.results)}</p>`;
                return;
            }
            if (!data.results || data.results.length === 0) {
                posterContainer.innerHTML = '<p class="col-span-3 text-center text-sm">Aucun film trouvé</p>';
                return;
            }
            const isGrid = posterContainer.classList.contains("grid");
            data.results.forEach((movie) => {
                const year = (movie.release_date || "").split("-")[0] || "";
                const card = document.createElement("div");
                card.className = "search-card cursor-pointer border-2 border-transparent rounded-lg hover:border-(--secondary-color) transition relative overflow-hidden";
                if (isGrid) {
                    // Grille : cartes portrait pleine largeur, titre en tooltip (desktop)
                    card.classList.add("text-center", "flex-shrink-0");
                    card.style.width = "100%";
                } else {
                    // Watchlist : carte paysage (titre visible) sur mobile, portrait + tooltip sur desktop
                    card.classList.add("flex", "items-center", "gap-3", "w-full", "p-2", "text-left", "flex-shrink-0", "sm:block", "sm:w-auto", "sm:p-0", "sm:text-center");
                }
                card.setAttribute("role", "option");
                card.dataset.id = movie.id;
                const imgSrc = movie.poster_path ? "https://image.tmdb.org/t/p/w500" + movie.poster_path : "";
                if (imgSrc) {
                    const img = document.createElement("img");
                    img.src = imgSrc;
                    img.alt = movie.title;
                    img.loading = "lazy";
                    if (isGrid) {
                        img.style.width = "100%";
                        img.style.height = "140px";
                        img.style.objectFit = "cover";
                        img.className = "rounded";
                    } else {
                        img.className = "rounded object-cover h-24 w-16 sm:h-[140px] sm:w-[140px] shrink-0";
                    }
                    card.appendChild(img);
                } else {
                    const placeholder = document.createElement("div");
                    placeholder.textContent = "Pas d'affiche";
                    if (isGrid) {
                        placeholder.style.width = "100%";
                        placeholder.style.height = "140px";
                        placeholder.className = "bg-gray-300 rounded flex items-center justify-center text-xs";
                    } else {
                        placeholder.className = "bg-gray-300 rounded flex items-center justify-center text-xs h-24 w-16 sm:h-[140px] sm:w-[140px] shrink-0";
                    }
                    card.appendChild(placeholder);
                }
                if (!isGrid) {
                    // Titre + année : visibles sur mobile (pas de tooltip au toucher)
                    const info = document.createElement("div");
                    info.className = "flex-1 min-w-0 sm:hidden";
                    const title = document.createElement("p");
                    title.className = "font-semibold text-sm leading-snug line-clamp-2";
                    title.textContent = movie.title;
                    const yearEl = document.createElement("p");
                    yearEl.className = "text-xs opacity-60 mt-0.5";
                    yearEl.textContent = year;
                    info.appendChild(title);
                    info.appendChild(yearEl);
                    card.appendChild(info);
                }
                const tooltip = ensureTooltip();
                const showTip = (e) => {
                    tooltip.innerHTML = `<div style="font-weight:600;">${escapeHtml(movie.title)}</div><div style="opacity:0.8;">${escapeHtml(year)}</div>`;
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
                    // Watchlist: click on poster directly submits the form (no validate button)
                    const form = document.getElementById("add-form");
                    if (form && form.action.includes("/add_movie_watchlist")) {
                        // hide tooltip before navigation
                        const tip = document.getElementById("autocomplete-tooltip");
                        if (tip) tip.style.display = "none";
                        form.requestSubmit();
                    }
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
