document.addEventListener('DOMContentLoaded', init);

function init() {
    /** Initializing DOM elements and variables */
    movieGrid = document.getElementById('movie-grid');
    sortRadios = document.getElementById('sort-radios');
    searchInput = document.getElementById('search-input');
    resetSearchButton = document.getElementById('reset-search');
    searchModal = document.getElementById('search-modal');
    modalElements = [
        {
            modal: document.getElementById('sort-modal'),
            buttons: [
                document.getElementById('sort-button'),
                document.getElementById('sort-button-mobile'),
            ],
        },
        {
            modal: document.getElementById('search-modal'),
            buttons: [
                document.getElementById('search-button'),
                document.getElementById('search-button-mobile'),
            ],
        },
        {
            modal: document.getElementById('add-modal'),
            buttons: [
                document.getElementById('add-button'),
                document.getElementById('add-button-mobile'),
            ],
        },
    ];
    sortChoices = ['order', 'criterion'];

    movies = JSON.parse(movieGrid.dataset.movies);

    /** Initialize the grid and set up all event listeners */
    displayGrid();
    addOpeners();
    addClosers();
    addSortActions();
    addSearchAction();
}

/**
 * Add the movies to the grid.
 * @param {list(dict)} moviesToDisplay
 */
function displayGrid(moviesToDisplay = movies) {
    movieGrid.innerHTML = '';
    moviesToDisplay.forEach((movie) => {
        const card = document.createElement('div');
        card.className = 'movie-card';

        card.innerHTML = `
            <div class='poster-info text-gray-400 left-2.5'>
                <span class="score">${movie.rating} %</span>
            </div>
            <div class='poster-info text-(--ivory-cream) right-2.5'>
                <span>${movie.year}</span>
            </div>
            <button onclick="deleteMovieWatchlist(${movie.tmdb_id})" class='delete-button text-(--ivory-cream) justify-center z-40'">
                <i data-lucide="trash-2" class="w-10 h-12"></i>
            </button>
            <a id="${movie.tmdb_id}" class="block">
                <img 
                    src="${movie.poster}" 
                    alt="${movie.title}" 
                    class="w-full object-cover transition-opacity hover:opacity-50"
                >
            </a>
        `;
        movieGrid.appendChild(card);
    });
    updateScoreColors();
    lucide.createIcons();
}

async function deleteMovieWatchlist(tmdbId) {
    const response = await fetch(`/delete_movie_watchlist/${tmdbId}`, {
        method: 'POST'
    });
    
    if (response.ok) {
        window.location.reload();
    }
}