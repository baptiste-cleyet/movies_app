/**
 * Once the DOM is loaded, we call all necessary functions to set up the page.
 */
document.addEventListener("DOMContentLoaded", function () {

    const banner = document.getElementById("banner");
    const movie = JSON.parse(banner.dataset.movie);

    // Used to set the banner image on mobile, as a horizontal banner is not good on mobile
    const mediaQuery = window.matchMedia("(hover: none)");
    if (mediaQuery.matches) {
        banner.style = `background-image: url('${movie.poster}')`;
    }

    modalElements = [
        {modal: document.getElementById("update-modal"), buttons: [document.getElementById("update-movie-button"), document.getElementById("update-movie-button-mobile")]},
        {modal: document.getElementById("delete-modal"), buttons: [document.getElementById("delete-movie-button"), document.getElementById("delete-movie-button-mobile")]},
    ];

    addOpeners();
    addClosers();
});

/**
 * Toggle the "active" class on the given element.
 * @param {*} element 
 */
function toggleActive(element) {
    element.classList.toggle("active");
}

/**
 * Add event listeners to the buttons that open the modals. When a button is clicked, the corresponding modal is shown.
 */
function addOpeners(){
    for (const element of modalElements) {
        for (const but of element["buttons"]) {
            but.addEventListener("click", () => {
                element["modal"].classList.remove("hidden");
            });
        }
    }
}

/**
 * Add event listeners to close the modals when needed.
 */
function addClosers(){
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