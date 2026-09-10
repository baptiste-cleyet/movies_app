/**
 * Sort the movies based on the given criterion and order.
 * @param {string} criterion - The criterion to sort by.
 * @param {boolean} increasing - Whether to sort in increasing order.
 * @returns {list(dict)} The sorted list of movies.
 */
function sortMovies(criterion = 'date-sort', increasing = false) {
    const sortFunctions = {
        'rating-sort': (a, b) => a.rating - b.rating,
        'title-sort': (a, b) => a.title.localeCompare(b.title),
        'date-sort': (a, b) => new Date(a.date) - new Date(b.date),
        'year-sort': (a, b) => a.year - b.year,
    };

    if (!sortFunctions[criterion]) {
        console.warn(
            `Critère de tri inconnu : ${criterion}, tri par date par défaut.`,
        );
        return movies;
    }

    return movies.sort((a, b) => {
        const result = sortFunctions[criterion](a, b);
        return increasing ? result : -result;
    });
}

/**
 * Search for movies that include the given title in their title.
 * @param {string} title
 * @returns {list(dict)} The list of movies that match the search criteria.
 */
function search(title) {
    const correpondingMovies = [];

    movies.forEach((movie) => {
        if (movie.title.toLowerCase().includes(title.toLowerCase())) {
            correpondingMovies.push(movie);
        }
    });

    return correpondingMovies;
}

/**
 * Add event listeners to open the modals when the corresponding buttons are clicked.
 */
function addOpeners() {
    for (const element of modalElements) {
        for (const but of element['buttons']) {
            but.addEventListener('click', () => {
                element['modal'].classList.remove('hidden');
            });
        }
    }
}

/**
 * Add event listeners to close the modals when the escape key is pressed or when a click is detected outside the modal content.
 */
function addClosers() {
    document.addEventListener('keydown', function (event) {
        if (event.key === 'Escape') {
            for (const element of modalElements) {
                element['modal'].classList.add('hidden');
            }
        }
    });

    for (const element of modalElements) {
        document.addEventListener('mousedown', function (event) {
            if (event.target === element['modal']) {
                element['modal'].classList.add('hidden');
            }
        });
    }
}

/**
 * Add event listeners to sort the movies when the sorting options are changed.
 */
function addSortActions() {
    sortRadios.addEventListener('change', () => {
        movies = sortMovies(
            document.querySelector(`input[name="${sortChoices[1]}"]:checked`)
                ?.value,
            document.querySelector(`input[name="${sortChoices[0]}"]:checked`)
                ?.value === 'increasing',
        );
        displayGrid();
    });
}

/**
 * Add event listeners to filter the movies when the search input is changed or when the reset search button is clicked.
 */
function addSearchAction() {
    searchInput.addEventListener('input', function () {
        const keyword = searchInput.value.trim().toLowerCase();
        const filteredMovies = search(keyword);
        displayGrid(filteredMovies);
    });
    resetSearchButton.addEventListener('click', function () {
        searchInput.value = '';
        searchModal.classList.add('hidden');
        displayGrid();
    });
}

/**
 * Add the posters of the movies with radio buttons to the given container.
 */
function addSearchPosters(title, posterContainer) {
    posterContainer.innerHTML = '';

    fetch('/search_movie', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
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
            addChoices = data.results;
            if (!data.results || data.results.length === 0) {
                posterContainer.innerHTML = 'Aucun film trouvé';
                return;
            }
            for (let i = 0; i < data.results.length; i++) {
                let inputChild = document.createElement('input');
                inputChild.type = 'radio';
                inputChild.name = 'movie_add';
                inputChild.id = i;
                inputChild.value = data.results[i].id;
                if (i === 0) inputChild.checked = true;

                let imgChild = document.createElement('img');
                imgChild.src =
                    'https://image.tmdb.org/t/p/w500' +
                    data.results[i].poster_path;
                imgChild.alt = 'inaccessible';
                imgChild.style =
                    'width:100px; height:140px; margin-right: 8px;';

                posterContainer.appendChild(inputChild);
                posterContainer.appendChild(imgChild);
            }
        })
        .catch((err) => console.error('Erreur :', err));
}
