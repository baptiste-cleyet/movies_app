import { sortMovies, search } from "./base.js";

export function addSortActions({ sortRadios, sortChoices, moviesRef, displayGrid }) {
    sortRadios.addEventListener("change", () => {
        const criterion = document.querySelector(`input[name="${sortChoices[1]}"]:checked`)?.value;
        const increasing = document.querySelector(`input[name="${sortChoices[0]}"]:checked`)?.value === "increasing";
        moviesRef.value = sortMovies(moviesRef.value, criterion, increasing);
        displayGrid();
    });
}

export function addSearchAction({ searchInput, resetSearchButton, searchModal, moviesRef, displayGrid }) {
    searchInput.addEventListener("input", function () {
        const keyword = searchInput.value.trim().toLowerCase();
        const filteredMovies = search(moviesRef.value, keyword);
        displayGrid(filteredMovies);
    });
    resetSearchButton.addEventListener("click", function () {
        searchInput.value = "";
        searchModal.classList.add("hidden");
        displayGrid();
    });
}
