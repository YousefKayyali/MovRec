let searchTimeout;
let currentSearchTerm = '';

// Function to handle search
function performSearch() {
    const searchInput = document.getElementById('search-input');
    const searchTerm = searchInput.value.trim();

    if (!searchTerm) {
        return;
    }

    window.location.href = `/Home/Search?query=${encodeURIComponent(searchTerm)}`;
}

// Function to handle autocomplete
async function handleAutocomplete() {
    const searchInput = document.getElementById('search-input');
    const autocompleteResults = document.getElementById('autocomplete-results');
    const term = searchInput.value.trim();

    if (term === currentSearchTerm) return;
    currentSearchTerm = term;

    if (!term) {
        autocompleteResults.innerHTML = '';
        return;
    }

    try {
        const response = await fetch(`/Home/Autocomplete?term=${encodeURIComponent(term)}`);
        const suggestions = await response.json();

        autocompleteResults.innerHTML = '';
        suggestions.forEach(suggestion => {
            const div = document.createElement('div');
            div.className = 'autocomplete-item';
            div.textContent = suggestion;
            div.onclick = () => {
                searchInput.value = suggestion;
                autocompleteResults.innerHTML = '';
                performSearch();
            };
            autocompleteResults.appendChild(div);
        });
    } catch (error) {
        console.error('Autocomplete error:', error);
    }
}

// Function to display search results
function displaySearchResults(movies) {
    const autocompleteResults = document.getElementById('autocomplete-results');
    autocompleteResults.innerHTML = '';

    if (movies.length === 0) {
        showError('No movies found');
        return;
    }

    const resultsContainer = document.createElement('div');
    resultsContainer.className = 'search-results';

    movies.forEach(movie => {
        const movieDiv = document.createElement('div');
        movieDiv.className = 'search-result-item';
        movieDiv.innerHTML = `
            <a href="/Movies/Details/${movie.id}">
                <img src="${movie.poster}" alt="${movie.title}" class="search-result-poster">
                <span class="search-result-title">${movie.title}</span>
            </a>
        `;
        resultsContainer.appendChild(movieDiv);
    });

    autocompleteResults.appendChild(resultsContainer);
}

// Function to show error messages
function showError(message) {
    const autocompleteResults = document.getElementById('autocomplete-results');
    autocompleteResults.innerHTML = `<div class="error-message">${message}</div>`;
}

// Event listeners
document.getElementById('search-input').addEventListener('input', () => {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(handleAutocomplete, 300);
});

document.getElementById('search-input').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        performSearch();
    }
}); 