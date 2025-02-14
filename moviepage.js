document.addEventListener("DOMContentLoaded", async () => {
    const urlParams = new URLSearchParams(window.location.search);
    const movieId = urlParams.get("id");

    if (!movieId) {
        console.error("No movie ID found in URL");
        return;
    }

    async function fetchMovieDetails() {
        try {
            const response = await fetch(`http://localhost:8000/movie/${movieId}`);
            const movie = await response.json();

            // Debugging: Log the movie object
            console.log("Movie Data:", movie);

            // Update the header
            document.querySelector(".header h1").textContent = movie.Title;
            document.querySelector(".header h2").textContent = movie["Release Date"];

            // Update backdrop as background
            const backdropPath = `http://localhost:8000/images/backdrops/${movie.image_id}`;
            const header = document.querySelector(".header");
            header.style.setProperty("--backdrop-url", `url(${backdropPath})`);

            // Update poster image
            const posterPath = `http://localhost:8000/images/posters/${movie.image_id}`;
            const posterImg = document.querySelector("#movie-poster");
            posterImg.src = posterPath;
            posterImg.onerror = function () {
                this.src = "path/to/placeholder_poster.jpg"; // Fallback image
            };

            // Update description
            document.querySelector(".left p").textContent = movie.Overview;

            // Update genres
            const genresContainer = document.querySelector(".tags");
            genresContainer.innerHTML = movie.genres.map(genre => `<span class="genre">${genre}</span>`).join("");

            // Add event listeners to genre elements
            const genreElements = document.querySelectorAll(".genre");
            genreElements.forEach(genreElement => {
                genreElement.addEventListener("click", () => {
                    const genre = genreElement.textContent;
                    window.location.href = `homepage.html?genre=${encodeURIComponent(genre)}`;
                });
            });

            // Update director
            document.querySelector(".right ul:nth-of-type(1)").innerHTML = `<li>${movie.Director}</li>`;

            // Update stars
            document.querySelector(".right ul:nth-of-type(2)").innerHTML = movie.Cast.split(',').map(star => `<li>${star.trim()}</li>`).join("");

            // Update rating
            document.querySelector(".right ul:nth-of-type(3)").innerHTML = `<li>${movie.rating}/10</li>`;
        } catch (error) {
            console.error("Error fetching movie details:", error);
        }
    }

    fetchMovieDetails();
});