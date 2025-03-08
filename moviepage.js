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
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const movie = await response.json();
  
        // Update header title and year
        document.querySelector(".header h1").textContent = movie.Title;
        const releaseYear = movie["Release Date"]
          ? new Date(movie["Release Date"]).getFullYear()
          : "Unknown Year";
        const yearElement = document.querySelector(".header h2");
        yearElement.textContent = releaseYear;
  
        // If releaseYear is valid, make the year clickable to filter by decade
        if (releaseYear !== "Unknown Year") {
          const decade = Math.floor(releaseYear / 10) * 10;
          yearElement.style.cursor = "pointer";
          yearElement.style.textDecoration = "underline";
          yearElement.addEventListener("click", () => {
            window.location.href = `homepage.html?decade=${decade}`;
          });
        }
  
        // Update backdrop
        const backdropPath = `http://localhost:8000/images/backdrops/${movie.image_id}`;
        document.querySelector(".header").style.setProperty("--backdrop-url", `url(${backdropPath})`);
  
        // Update poster image
        const posterPath = `http://localhost:8000/images/posters/${movie.image_id}`;
        const posterImg = document.querySelector("#movie-poster");
        posterImg.src = posterPath;
        posterImg.onerror = function () {
          this.src = "path/to/placeholder_poster.jpg";
        };
  
        // Update description
        document.querySelector(".left p").textContent = movie.Overview;
  
        // Update genres with click listeners
        const genresContainer = document.querySelector(".tags");
        genresContainer.innerHTML = movie.genres
          .map(genre => `<span class="genre" data-genre="${genre}">${genre}</span>`)
          .join("");
        document.querySelectorAll(".genre").forEach(genreElement => {
          genreElement.addEventListener("click", () => {
            const genre = genreElement.getAttribute("data-genre");
            window.location.href = `homepage.html?genre=${encodeURIComponent(genre)}`;
          });
        });
  
        // Update director, cast, and rating
        document.querySelector(".right ul:nth-of-type(1)").innerHTML = `<li>${movie.Director}</li>`;
        document.querySelector(".right ul:nth-of-type(2)").innerHTML = movie.Cast
          .split(",")
          .map(star => `<li>${star.trim()}</li>`)
          .join("");
        document.querySelector(".right ul:nth-of-type(3)").innerHTML = `<li>${movie.rating}/10</li>`;
  
        // Fetch and display similar movies in the carousel
        await fetchSimilarMovies(movieId);
      } catch (error) {
        console.error("Error fetching movie details:", error);
      }
    }
  
    async function fetchSimilarMovies(movieId) {
      try {
        const response = await fetch(`http://localhost:8000/similar-movies/${movieId}`);
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const similarMovies = await response.json();
  
        const carouselTrack = document.querySelector(".carousel-track");
        carouselTrack.innerHTML = similarMovies
          .map(movie => `
            <li>
              <div class="similar-movie" onclick="window.location.href='moviepage.html?id=${movie['Movie ID']}'">
                <img src="http://localhost:8000/images/posters/${movie.image_id}" alt="${movie.Title}" class="poster">
                <img src="http://localhost:8000/images/backdrops/${movie.image_id}" alt="${movie.Title}" class="backdrop">
                <h4>${movie.Title}</h4>
                <div class="movie-details">
                  <h3>${movie.Title}</h3>
                  <p>Rating: ${movie.rating}</p>
                  <p>${movie.Overview || "No overview available."}</p>
                  <button onclick="window.location.href='moviepage.html?id=${movie['Movie ID']}'; event.stopPropagation();">More Info</button>
                </div>
              </div>
            </li>
          `)
          .join("");
  
        initializeCarousel();
      } catch (error) {
        console.error("Error fetching similar movies:", error);
      }
    }
  
    function initializeCarousel() {
      const carouselTrack = document.querySelector(".carousel-track");
      const prevButton = document.querySelector(".carousel-button.prev");
      const nextButton = document.querySelector(".carousel-button.next");
  
      let currentIndex = 0;
      const itemsToShow = 5;
      const totalItems = carouselTrack.children.length;
  
      // Ensure each item takes up equal width based on the number of items to show
      Array.from(carouselTrack.children).forEach(item => {
        item.style.minWidth = `${100 / itemsToShow}%`;
      });
  
      prevButton.addEventListener("click", () => {
        if (currentIndex > 0) {
          currentIndex--;
          carouselTrack.style.transform = `translateX(-${currentIndex * (100 / itemsToShow)}%)`;
        }
      });
  
      nextButton.addEventListener("click", () => {
        if (currentIndex < totalItems - itemsToShow) {
          currentIndex++;
          carouselTrack.style.transform = `translateX(-${currentIndex * (100 / itemsToShow)}%)`;
        }
      });
    }
  
    await fetchMovieDetails();
  });
  