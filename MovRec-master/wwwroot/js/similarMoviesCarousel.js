// Similar Movies Carousel Configuration
const similarMoviesConfig = {
    itemsPerView: {
        default: 5,
        tablet: 3,
        mobile: 2
    },
    transitionDuration: 300,
    touchThreshold: 50
};

// Similar Movies Carousel State
const similarMoviesState = {
    currentIndex: 0,
    carousel: null,
    posters: [],
    touchStartX: 0,
    isDragging: false
};

// Initialize Similar Movies Carousel
function initSimilarMoviesCarousel() {
    similarMoviesState.carousel = document.querySelector('#recommended-movies .carousel');
    if (!similarMoviesState.carousel) return;

    similarMoviesState.posters = similarMoviesState.carousel.querySelectorAll('.poster-container');

    // Add event listeners
    similarMoviesState.carousel.addEventListener('touchstart', handleSimilarTouchStart);
    similarMoviesState.carousel.addEventListener('touchmove', handleSimilarTouchMove);
    similarMoviesState.carousel.addEventListener('touchend', handleSimilarTouchEnd);

    similarMoviesState.carousel.addEventListener('mousedown', handleSimilarMouseDown);
    similarMoviesState.carousel.addEventListener('mousemove', handleSimilarMouseMove);
    similarMoviesState.carousel.addEventListener('mouseup', handleSimilarMouseUp);
    similarMoviesState.carousel.addEventListener('mouseleave', handleSimilarMouseUp);

    similarMoviesState.carousel.addEventListener('keydown', handleSimilarKeyDown);

    // Handle window resize
    window.addEventListener('resize', handleSimilarResize);

    // Set initial state
    updateSimilarCarousel();
}

// Get items per view based on screen size
function getSimilarItemsPerView() {
    const width = window.innerWidth;
    if (width <= 768) return similarMoviesConfig.itemsPerView.mobile;
    if (width <= 1024) return similarMoviesConfig.itemsPerView.tablet;
    return similarMoviesConfig.itemsPerView.default;
}

// Update carousel position
function updateSimilarCarousel() {
    if (!similarMoviesState.carousel) return;

    const itemsPerView = getSimilarItemsPerView();
    const itemWidth = similarMoviesState.posters[0]?.offsetWidth + 20 || 0; // Width + margin
    const totalItems = similarMoviesState.posters.length;
    const totalSlides = Math.ceil(totalItems / itemsPerView);

    // Ensure current index is within bounds
    similarMoviesState.currentIndex = Math.max(0, Math.min(similarMoviesState.currentIndex, totalSlides - 1));

    const offset = similarMoviesState.currentIndex * itemWidth * itemsPerView;

    similarMoviesState.carousel.style.transition = `transform ${similarMoviesConfig.transitionDuration}ms ease`;
    similarMoviesState.carousel.style.transform = `translateX(-${offset}px)`;
}

// Navigation functions
function nextSimilarSlide() {
    const itemsPerView = getSimilarItemsPerView();
    const totalItems = similarMoviesState.posters.length;
    const totalSlides = Math.ceil(totalItems / itemsPerView);

    similarMoviesState.currentIndex++;
    if (similarMoviesState.currentIndex >= totalSlides) {
        similarMoviesState.currentIndex = 0;
    }
    updateSimilarCarousel();
}

function prevSimilarSlide() {
    const itemsPerView = getSimilarItemsPerView();
    const totalItems = similarMoviesState.posters.length;
    const totalSlides = Math.ceil(totalItems / itemsPerView);

    similarMoviesState.currentIndex--;
    if (similarMoviesState.currentIndex < 0) {
        similarMoviesState.currentIndex = totalSlides - 1;
    }
    updateSimilarCarousel();
}

// Touch event handlers
function handleSimilarTouchStart(e) {
    similarMoviesState.touchStartX = e.touches[0].clientX;
    similarMoviesState.isDragging = true;
    similarMoviesState.carousel.style.transition = 'none';
}

function handleSimilarTouchMove(e) {
    if (!similarMoviesState.isDragging) return;

    const touchCurrentX = e.touches[0].clientX;
    const touchDiff = similarMoviesState.touchStartX - touchCurrentX;

    const itemWidth = similarMoviesState.posters[0].offsetWidth + 20;
    const offset = similarMoviesState.currentIndex * itemWidth * getSimilarItemsPerView();

    similarMoviesState.carousel.style.transform = `translateX(-${offset - touchDiff}px)`;
}

function handleSimilarTouchEnd() {
    if (!similarMoviesState.isDragging) return;

    const touchEndX = event.changedTouches[0].clientX;
    const touchDiff = similarMoviesState.touchStartX - touchEndX;

    if (Math.abs(touchDiff) > similarMoviesConfig.touchThreshold) {
        if (touchDiff > 0) {
            nextSimilarSlide();
        } else {
            prevSimilarSlide();
        }
    } else {
        updateSimilarCarousel();
    }

    similarMoviesState.isDragging = false;
}

// Mouse event handlers
function handleSimilarMouseDown(e) {
    similarMoviesState.touchStartX = e.clientX;
    similarMoviesState.isDragging = true;
    similarMoviesState.carousel.style.transition = 'none';
}

function handleSimilarMouseMove(e) {
    if (!similarMoviesState.isDragging) return;

    const mouseCurrentX = e.clientX;
    const mouseDiff = similarMoviesState.touchStartX - mouseCurrentX;

    const itemWidth = similarMoviesState.posters[0].offsetWidth + 20;
    const offset = similarMoviesState.currentIndex * itemWidth * getSimilarItemsPerView();

    similarMoviesState.carousel.style.transform = `translateX(-${offset - mouseDiff}px)`;
}

function handleSimilarMouseUp() {
    if (!similarMoviesState.isDragging) return;

    const mouseEndX = event.clientX;
    const mouseDiff = similarMoviesState.touchStartX - mouseEndX;

    if (Math.abs(mouseDiff) > similarMoviesConfig.touchThreshold) {
        if (mouseDiff > 0) {
            nextSimilarSlide();
        } else {
            prevSimilarSlide();
        }
    } else {
        updateSimilarCarousel();
    }

    similarMoviesState.isDragging = false;
}

// Keyboard navigation
function handleSimilarKeyDown(e) {
    if (e.key === 'ArrowLeft') {
        prevSimilarSlide();
    } else if (e.key === 'ArrowRight') {
        nextSimilarSlide();
    }
}

// Handle window resize
function handleSimilarResize() {
    updateSimilarCarousel();
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initSimilarMoviesCarousel);

// Cleanup function
function cleanupSimilarCarousel() {
    window.removeEventListener('resize', handleSimilarResize);
    if (similarMoviesState.carousel) {
        similarMoviesState.carousel.removeEventListener('touchstart', handleSimilarTouchStart);
        similarMoviesState.carousel.removeEventListener('touchmove', handleSimilarTouchMove);
        similarMoviesState.carousel.removeEventListener('touchend', handleSimilarTouchEnd);
        similarMoviesState.carousel.removeEventListener('mousedown', handleSimilarMouseDown);
        similarMoviesState.carousel.removeEventListener('mousemove', handleSimilarMouseMove);
        similarMoviesState.carousel.removeEventListener('mouseup', handleSimilarMouseUp);
        similarMoviesState.carousel.removeEventListener('mouseleave', handleSimilarMouseUp);
        similarMoviesState.carousel.removeEventListener('keydown', handleSimilarKeyDown);
    }
}

// Export functions for use in HTML
window.nextSimilarSlide = nextSimilarSlide;
window.prevSimilarSlide = prevSimilarSlide; 