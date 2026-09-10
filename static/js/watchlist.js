import { setupGrid } from "./grid_controller.js";

function renderWatchlist(moviesToDisplay, movieGrid) {
    moviesToDisplay.forEach((movie) => {
        const card = document.createElement("div");
        card.className = "movie-card";
        const posterSrc = movie.poster || "/static/images/icon.png";
        card.innerHTML = `
            <div class='poster-info text-gray-400 left-2.5'>
                <span class="score">${movie.rating ?? ""} %</span>
            </div>
            <div class='poster-info text-(--ivory-cream) right-2.5'>
                <span>${movie.year ?? ""}</span>
            </div>
            <button onclick="deleteMovieWatchlist(${movie.tmdb_id})" class='delete-button text-(--ivory-cream) justify-center z-40'>
                <i data-lucide="trash-2" class="w-10 h-12"></i>
            </button>
            <a id="${movie.tmdb_id}" class="block">
                <img src="${posterSrc}" alt="${movie.title}" loading="lazy" class="w-full object-cover transition-opacity hover:opacity-50">
            </a>
        `;
        movieGrid.appendChild(card);
    });
}

window.deleteMovieWatchlist = async function (tmdbId) {
    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;
    const response = await fetch(`/delete_movie_watchlist/${tmdbId}`, {
        method: "POST",
        headers: { "X-CSRFToken": csrfToken },
    });
    if (response.ok) window.location.reload();
};

setupGrid(renderWatchlist);
