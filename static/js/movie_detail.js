import { addOpeners, addClosers } from "./base.js";

document.addEventListener("DOMContentLoaded", function () {
    const banner = document.getElementById("banner");
    const movie = JSON.parse(banner.dataset.movie);
    const mediaQuery = window.matchMedia("(hover: none)");
    if (mediaQuery.matches) {
        banner.style = `background-image: url('${movie.poster}')`;
    }
    const modalElements = [
        { modal: document.getElementById("update-modal"), buttons: [document.getElementById("update-movie-button"), document.getElementById("update-movie-button-mobile")] },
        { modal: document.getElementById("delete-modal"), buttons: [document.getElementById("delete-movie-button"), document.getElementById("delete-movie-button-mobile")] },
    ];
    addOpeners(modalElements);
    addClosers(modalElements);
});
