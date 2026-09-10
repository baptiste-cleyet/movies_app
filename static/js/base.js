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
    // init search poster blur handler
    const titleInput = document.getElementById("title");
    const posterContainer = document.getElementById("corresponding-poster");
    if (titleInput && posterContainer) {
        titleInput.addEventListener("blur", () => addSearchPosters(titleInput.value, posterContainer));
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

export function addSearchPosters(title, posterContainer) {
    if (!posterContainer) return;
    posterContainer.innerHTML = "";
    fetch("/search_movie", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title: title }),
    })
        .then((response) => response.json())
        .then((data) => {
            if (data.error) {
                posterContainer.innerHTML = data.error;
                return;
            }
            if (typeof data.results === "string") {
                posterContainer.innerHTML = data.results;
                return;
            }
            if (!data.results || data.results.length === 0) {
                posterContainer.innerHTML = "Aucun film trouvé";
                return;
            }
            for (let i = 0; i < data.results.length; i++) {
                const inputChild = document.createElement("input");
                inputChild.type = "radio";
                inputChild.name = "movie_add";
                inputChild.id = i;
                inputChild.value = data.results[i].id;
                if (i === 0) inputChild.checked = true;
                const imgChild = document.createElement("img");
                imgChild.src = "https://image.tmdb.org/t/p/w500" + data.results[i].poster_path;
                imgChild.alt = "inaccessible";
                imgChild.style = "width:100px; height:140px; margin-right: 8px;";
                posterContainer.appendChild(inputChild);
                posterContainer.appendChild(imgChild);
            }
        })
        .catch((err) => console.error("Erreur :", err));
}

// Keep globals for inline handlers (onclick="toggleHidden(...)" in base.html)
window.toggleHidden = toggleHidden;
window.toggleActive = toggleActive;
