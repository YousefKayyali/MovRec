// Fetch genres from the Flask backend
async function fetchGenres() {
    try {
        const response = await fetch('http://localhost:8000/genres'); // Fetch from Flask backend
        if (!response.ok) {
            throw new Error(`Network response was not ok. Status: ${response.status}`);
        }
        const genres = await response.json();
        console.log('Fetched genres:', genres); // Log fetched genres for debugging
        return genres;
    } catch (error) {
        console.error('Error fetching genres:', error);
        return []; // Return an empty array if there's an error
    }
}

// Function to dynamically generate checkboxes
function generateCheckboxes(genres) {
    const categoriesDiv = document.getElementById('categories');
    if (!categoriesDiv) {
        console.error('Error: Could not find the categories div.');
        return;
    }

    // Clear any existing content in the categories div
    categoriesDiv.innerHTML = '';

    // Generate a checkbox for each genre
    genres.forEach(genre => {
        const label = document.createElement('label');
        label.className = 'category';
        label.innerHTML = `
            <input type="checkbox" value="${genre}"> <span>${genre}</span>
        `;
        categoriesDiv.appendChild(label);
    });

    console.log('Checkboxes generated successfully.'); // Log success
}

// On page load, fetch genres and generate checkboxes
document.addEventListener('DOMContentLoaded', async () => {
    console.log('Page loaded. Fetching genres...');
    const genres = await fetchGenres();

    if (genres.length > 0) {
        console.log('Generating checkboxes...');
        generateCheckboxes(genres);
    } else {
        console.error('No genres found or failed to fetch genres.');
        alert('Failed to load genres. Please try again later.');
    }
});

// Handle form submission
document.getElementById('submitButton').addEventListener('click', function(event) {
    event.preventDefault(); // Prevent the default button action

    const selectedCategories = Array.from(
        document.querySelectorAll('.category input[type="checkbox"]:checked')
    ).map(input => input.value);

    if (selectedCategories.length > 0) {
        console.log('Selected categories:', selectedCategories); // Log selected categories
        alert(`You selected: ${selectedCategories.join(', ')}`);
        window.location.href = 'homepage.html'; // Redirect to home.html
    } else {
        alert('Please select at least one category.');
    }
});