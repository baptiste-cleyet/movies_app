import { createIcons, icons } from "./icons.js";
import { updateScoreColors, addOpeners, addClosers } from "./base.js";
import { addSortActions, addSearchAction } from "./grid.js";

/**
 * Shared grid initialization for movie_grid and watchlist.
 * @param {(moviesToDisplay: any[], movieGrid: HTMLElement) => void} renderFn - renders cards into movieGrid
 */
export function setupGrid(renderFn) {
    let movieGrid = document.getElementById("movie-grid");
    let sortRadios = document.getElementById("sort-radios");
    let searchInput = document.getElementById("search-input");
    let resetSearchButton = document.getElementById("reset-search");
    let searchModal = document.getElementById("search-modal");
    let sortChoices = ["order", "criterion"];
    let moviesRef = { value: [] };

    function displayGrid(moviesToDisplay = moviesRef.value) {
        if (!movieGrid) return;
        movieGrid.innerHTML = "";
        renderFn(moviesToDisplay, movieGrid);
        updateScoreColors();
        createIcons({ icons });
    }

    function init() {
        movieGrid = document.getElementById("movie-grid");
        sortRadios = document.getElementById("sort-radios");
        searchInput = document.getElementById("search-input");
        resetSearchButton = document.getElementById("reset-search");
        searchModal = document.getElementById("search-modal");
        const modalElements = [
            { modal: document.getElementById("sort-modal"), buttons: [document.getElementById("sort-button"), document.getElementById("sort-button-mobile")] },
            { modal: document.getElementById("search-modal"), buttons: [document.getElementById("search-button"), document.getElementById("search-button-mobile")] },
            { modal: document.getElementById("add-modal"), buttons: [document.getElementById("add-button"), document.getElementById("add-button-mobile")] },
        ];
        if (movieGrid && movieGrid.dataset.movies) {
            try {
                moviesRef.value = JSON.parse(movieGrid.dataset.movies);
            } catch {
                moviesRef.value = [];
            }
        }
        displayGrid();
        addOpeners(modalElements);
        addClosers(modalElements);
        if (sortRadios) addSortActions({ sortRadios, sortChoices, moviesRef, displayGrid });
        if (searchInput && resetSearchButton && searchModal) addSearchAction({ searchInput, resetSearchButton, searchModal, moviesRef, displayGrid });
    }

    document.addEventListener("DOMContentLoaded", init);
    return { init, displayGrid, moviesRef };
}
