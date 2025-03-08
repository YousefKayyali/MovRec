document.addEventListener("DOMContentLoaded", async () => {
    const movieContainer = document.querySelector(".movie-container");
    const genreDropdown = document.getElementById("genre-dropdown");
    const decadeDropdown = document.getElementById("decade-dropdown");
    const searchInput = document.getElementById("search-input");
    const autocompleteResults = document.getElementById("autocomplete-results");
    const logo = document.getElementById("logo");

    let currentPage = 1;
    let isLoading = false;
    let allMovies = [];
    let selectedGenres = new Set();
    let selectedDecades = new Set();

    // Check for genre or decade query parameters in the URL
    const urlParams = new URLSearchParams(window.location.search);
    const genreFromURL = urlParams.get("genre");
    const decadeFromURL = urlParams.get("decade");

    if (genreFromURL) {
        selectedGenres.add(genreFromURL);
    }
    if (decadeFromURL) {
        selectedDecades.add(decadeFromURL);
    }

    // Redirect to homepage without query parameters when logo is clicked
    logo.addEventListener("click", () => {
        window.location.href = "homepage.html";
    });

    // Fetch movies sorted by average rating
    async function fetchMovies(page = 1) {
        try {
            isLoading = true;
            let url = `http://localhost:8000/movies?page=${page}&sort_by=rating&per_page=100`;
            if (selectedGenres.size > 0) {
                selectedGenres.forEach(genre => {
                    url += `&genre=${genre}`;
                });
            }
            if (selectedDecades.size > 0) {
                selectedDecades.forEach(decade => {
                    url += `&decade=${decade}`;
                });
            }
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            return data.movies;
        } catch (error) {
            console.error("Error fetching movies:", error);
            return [];
        } finally {
            isLoading = false;
        }
    }

    // Render movies in a grid
    function renderMovies(movies) {
        movies.forEach(movie => {
            if (allMovies.some(m => m["Movie ID"] === movie["Movie ID"])) {
                return;
            }

            const movieElement = document.createElement("div");
            movieElement.classList.add("movie");

            let posterPath = movie.image_id ? `http://localhost:8000/images/posters/${movie.image_id}` : "http://localhost:8000/images/posters/default.jpg";
            let backdropPath = movie.image_id ? `http://localhost:8000/images/backdrops/${movie.image_id}` : "http://localhost:8000/images/backdrops/default.jpg";

            movieElement.innerHTML = `
                <img src="${posterPath}" alt="${movie.Title}" class="poster" onerror="this.src='http://localhost:8000/images/posters/default.jpg';">
                <img src="${backdropPath}" alt="${movie.Title}" class="backdrop" onerror="this.src='http://localhost:8000/images/backdrops/default.jpg';">
                <h3>${movie.Title}</h3>
                <p>Rating: ${movie.rating}</p>
                <div class="movie-details">
                    <h3>${movie.Title}</h3>
                    <p>Rating: ${movie.rating}</p>
                    <p>${movie.Overview || "No overview available."}</p>
                    <button onclick="window.location.href='moviepage.html?id=${movie["Movie ID"]}';">More Info</button>
                </div>
            `;

            movieElement.addEventListener("click", () => {
                window.location.href = `moviepage.html?id=${movie["Movie ID"]}`;
            });

            movieContainer.appendChild(movieElement);
            allMovies.push(movie);
        });
    }

    // Load initial movies
    async function loadInitialMovies() {
        const movies = await fetchMovies(currentPage);
        renderMovies(movies);
    }

    // Load more movies when the user scrolls down
    async function loadMoreMovies() {
        if (isLoading) return;
        currentPage++;
        const movies = await fetchMovies(currentPage);
        renderMovies(movies);
    }

    // Infinite scroll logic
    window.addEventListener("scroll", () => {
        const { scrollTop, scrollHeight, clientHeight } = document.documentElement;
        if (scrollTop + clientHeight >= scrollHeight - 100) {
            loadMoreMovies();
        }
    });

    // Fetch genres from the backend
    async function fetchGenres() {
        try {
            const response = await fetch("http://localhost:8000/genres");
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            return data;
        } catch (error) {
            console.error("Error fetching genres:", error);
            return [];
        }
    }

    // Fetch decades from the backend
    async function fetchDecades() {
        try {
            const response = await fetch("http://localhost:8000/decades");
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            return data;
        } catch (error) {
            console.error("Error fetching decades:", error);
            return [];
        }
    }

    // Populate the dropdown with genres
    async function populateGenres() {
        const genres = await fetchGenres();
        if (genres.length > 0) {
            genres.forEach(genre => {
                const genreItem = document.createElement("div");
                genreItem.classList.add("dropdown-item");
                genreItem.textContent = genre;
                if (selectedGenres.has(genre)) {
                    genreItem.classList.add("selected");
                }
                genreItem.addEventListener("click", () => {
                    if (selectedGenres.has(genre)) {
                        selectedGenres.delete(genre);
                        genreItem.classList.remove("selected");
                    } else {
                        selectedGenres.add(genre);
                        genreItem.classList.add("selected");
                    }
                    allMovies = [];
                    movieContainer.innerHTML = "";
                    currentPage = 1;
                    loadInitialMovies();
                });
                genreDropdown.appendChild(genreItem);
            });
        } else {
            const noGenres = document.createElement("div");
            noGenres.classList.add("dropdown-item");
            noGenres.textContent = "No genres available";
            genreDropdown.appendChild(noGenres);
        }
    }

    // Populate the dropdown with decades
    async function populateDecades() {
        const decades = await fetchDecades();
        if (decades.length > 0) {
            decades.forEach(decade => {
                const decadeItem = document.createElement("div");
                decadeItem.classList.add("dropdown-item");
                decadeItem.textContent = decade;
                if (selectedDecades.has(decade)) {
                    decadeItem.classList.add("selected");
                }
                decadeItem.addEventListener("click", () => {
                    if (selectedDecades.has(decade)) {
                        selectedDecades.delete(decade);
                        decadeItem.classList.remove("selected");
                    } else {
                        selectedDecades.add(decade);
                        decadeItem.classList.add("selected");
                    }
                    allMovies = [];
                    movieContainer.innerHTML = "";
                    currentPage = 1;
                    loadInitialMovies();
                });
                decadeDropdown.appendChild(decadeItem);
            });
        } else {
            const noDecades = document.createElement("div");
            noDecades.classList.add("dropdown-item");
            noDecades.textContent = "No decades available";
            decadeDropdown.appendChild(noDecades);
        }
    }

    // Fetch and render initial movies
    loadInitialMovies();

    // Populate genres and decades when the page loads
    populateGenres();
    populateDecades();

    // Search functionality
    searchInput.addEventListener("input", async (e) => {
        const query = e.target.value;
        if (query.length > 2) {
            const response = await fetch(`http://localhost:8000/search?query=${query}`);
            const data = await response.json();
            showAutocompleteResults(data);
        } else {
            autocompleteResults.innerHTML = "";
        }
    });

    function showAutocompleteResults(results) {
        autocompleteResults.innerHTML = "";

        const uniqueResults = Array.from(new Set(results.map(movie => movie["Movie ID"])))
            .map(id => results.find(movie => movie["Movie ID"] === id));

        uniqueResults.forEach(movie => {
            const resultItem = document.createElement("div");
            resultItem.innerHTML = `
                <img src="http://localhost:8000/images/posters/${movie.image_id}" alt="${movie.Title}" onerror="this.src='http://localhost:8000/images/posters/default.jpg';">
                <span>${movie.Title}</span>
            `;
            resultItem.addEventListener("click", () => {
                window.location.href = `moviepage.html?id=${movie["Movie ID"]}`;
            });
            autocompleteResults.appendChild(resultItem);
        });
    }

    function performSearch() {
        const query = searchInput.value;
        if (query) {
            window.location.href = `search.html?query=${query}`;
        }
    }
});