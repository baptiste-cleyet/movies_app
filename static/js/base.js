lucide.createIcons();

const root = document.documentElement;
/**
 * This function is used to toggle the dark mode of the website.
 */
(function () {
    theme =
        document.cookie
            .split("; ")
            .find((row) => row.startsWith("theme="))
            ?.split("=")[1] || "light";
    root.setAttribute("data-theme", theme);

    document.addEventListener("DOMContentLoaded", function () {

        id_themes = {
            "light": ["light-mode-li", "light-mode-mobile-li"],
            "dark": ["dark-mode-li", "dark-mode-mobile-li"]
        }

        events_id = ["light-mode", "light-mode-mobile", "dark-mode", "dark-mode-mobile"];

        events_id.forEach(id => {
            document.getElementById(id).addEventListener("click", toggleDarkMode);
        })

        id_themes[theme].forEach(id => {
            document.getElementById(id).classList.add("hidden");
        })
        id_themes[theme === "dark" ? "light" : "dark"].forEach(id => {
            document.getElementById(id).classList.remove("hidden");
        })
    });

})();

/**
 * Toggle the dark mode of the website and save the preference in a cookie.
 */
function toggleDarkMode() {
    const currentTheme = root.getAttribute("data-theme");
    const newTheme = currentTheme === "dark" ? "light" : "dark";
    root.setAttribute("data-theme", newTheme);
    document.cookie = `theme=${newTheme};path=/;max-age=31536000`; // 1 year

    id_themes[newTheme].forEach(id => {
        document.getElementById(id).classList.add("hidden");
    })
    id_themes[currentTheme].forEach(id => {
        document.getElementById(id).classList.remove("hidden");
    })
}


/**
 * When the DOM is loaded, update the color of the score elements and add an event listener to hide the mobile menu when clicking outside of it.
 */
document.addEventListener("DOMContentLoaded", function () {
    updateScoreColors();

    const container = document.getElementById('mobile-menu');
    const menu = document.getElementById('mobile-ul');
    window.addEventListener('click', (e) => {
        if (!container.contains(e.target)) {
            menu.classList.add('hidden');
        }
    });
});


/** 
* Return a color based on the score. The color is a gradient from red to green
* @param {int} score - the score to get the color from
* @return {string} A string containing the rgb value of the color
*/
function getColor(score) {
    const r = score < 80 ? 255 : Math.floor(255 - (score - 80) * 8);
    const g = score > 80 ? 255 : Math.floor(score * 3);
    return `rgb(${r},${g},0)`; // rouge → jaune → vert
}


/** 
* Get all the score elements and update their color based on their value. The color come from the getColor function.
*/
function updateScoreColors() {
    let noteElements = document.querySelectorAll(".score");

    noteElements.forEach((noteTxt) => {
        const scoreText = noteTxt.textContent.trim();
        const score = parseFloat(scoreText.replace("%", ""));
        noteTxt.style.color = getColor(score);
    });
}

/**
 * Toggle the visibility by toggling the "hidden" class on the given element.
 * @param {*} element 
 */
function toggleHidden(element) {
    element.classList.toggle("hidden");
}
