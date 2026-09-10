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
    function resetSearch() {
        if (searchInput.value !== "") {
            searchInput.value = "";
            displayGrid();
        }
    }

    searchInput.addEventListener("input", function () {
        const keyword = searchInput.value.trim().toLowerCase();
        if (keyword === "") {
            displayGrid();
            return;
        }
        const filteredMovies = search(moviesRef.value, keyword);
        displayGrid(filteredMovies);
    });
    resetSearchButton.addEventListener("click", function () {
        searchInput.value = "";
        searchModal.classList.add("hidden");
        displayGrid();
    });

    // Escape inside the research field: clear filter, hide modal, keep grid clickable
    searchInput.addEventListener("keydown", function (event) {
        if (event.key === "Escape") {
            event.preventDefault();
            searchInput.value = "";
            searchModal.classList.add("hidden");
            searchInput.blur();
            displayGrid();
        }
    });

    // Escape anywhere closes search and clears filter; clicking outside keeps filter and modal open
    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape" && !searchModal.classList.contains("hidden")) {
            resetSearch();
            searchModal.classList.add("hidden");
            // ensure focus leaves hidden modal so grid remains clickable
            if (document.activeElement === searchInput) searchInput.blur();
        }
    });

    // Clear search when accessing another page (navigation or opening another modal)
    function clearOnPageChange() {
        if (searchInput.value !== "") {
            searchInput.value = "";
            displayGrid();
        }
    }
    // Navigation links (grid/watchlist/detail)
    document.addEventListener("click", function (e) {
        const link = e.target.closest('a[href]');
        if (link && link.getAttribute('href')) {
            clearOnPageChange();
        }
        // Opening sort/add modals also clears search
        if (e.target.closest('#sort-button, #sort-button-mobile, #add-button, #add-button-mobile')) {
            clearOnPageChange();
        }
    });
    window.addEventListener("beforeunload", clearOnPageChange);
    window.addEventListener("pagehide", clearOnPageChange);
}
