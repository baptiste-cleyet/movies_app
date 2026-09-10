import { setupGrid } from "./grid_controller.js";

function renderGrid(moviesToDisplay, movieGrid) {
    moviesToDisplay.forEach((movie) => {
        const card = document.createElement("div");
        card.className = "movie-card";
        const date = movie.date ? new Date(movie.date) : null;
        const dateStr = date && !isNaN(date) ? date.toLocaleDateString("fr-FR") : "";
        const posterSrc = movie.poster || "/static/images/icon.png";
        card.innerHTML = `
            <div class='poster-info text-gray-400 left-2.5'>
                <span class="score">${movie.rating ?? ""} %</span>
            </div>
            <div class='poster-info text-(--ivory-cream) right-2.5'>
                <span>${dateStr}</span>
            </div>
            <a href="/${movie.tmdb_id}" id="${movie.tmdb_id}" class="block">
                <img src="${posterSrc}" alt="${movie.title}" loading="lazy" class="w-full object-cover transition-opacity hover:opacity-80">
            </a>
        `;
        movieGrid.appendChild(card);
    });
}

setupGrid(renderGrid);
