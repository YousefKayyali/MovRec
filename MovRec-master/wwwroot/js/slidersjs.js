// Carousel configuration
const config = {
    itemsPerView: {
        default: 5,
        tablet: 3,
        mobile: 2
    },
    transitionDuration: 300,
    touchThreshold: 50
};

// State management
const state = {
    currentIndices: [],
    carousels: [],
    touchStartX: 0,
    isDragging: false
};

// Initialize carousels
function initCarousels() {
    state.carousels = document.querySelectorAll('.carousel');
    state.currentIndices = new Array(state.carousels.length).fill(0);

    // Add event listeners to each carousel
    state.carousels.forEach((carousel, index) => {
        // Touch events
        carousel.addEventListener('touchstart', (e) => handleTouchStart(e, index));
        carousel.addEventListener('touchmove', (e) => handleTouchMove(e, index));
        carousel.addEventListener('touchend', () => handleTouchEnd(index));

        // Mouse events
        carousel.addEventListener('mousedown', (e) => handleMouseDown(e, index));
        carousel.addEventListener('mousemove', (e) => handleMouseMove(e, index));
        carousel.addEventListener('mouseup', () => handleMouseUp(index));
        carousel.addEventListener('mouseleave', () => handleMouseUp(index));

        // Keyboard navigation
        carousel.addEventListener('keydown', (e) => handleKeyDown(e, index));

        // Set initial state
        updateCarousel(index);
    });

    // Handle window resize
    window.addEventListener('resize', handleResize);
}

// Get items per view based on screen size
function getItemsPerView() {
    const width = window.innerWidth;
    if (width <= 768) return config.itemsPerView.mobile;
    if (width <= 1024) return config.itemsPerView.tablet;
    return config.itemsPerView.default;
}

// Update carousel position
function updateCarousel(carouselIndex) {
    const carousel = state.carousels[carouselIndex];
    if (!carousel) return;

    const itemsPerView = getItemsPerView();
    const posters = carousel.querySelectorAll('.poster-container');
    const itemWidth = posters[0]?.offsetWidth + 20 || 0; // Width + margin
    const totalItems = posters.length;
    const totalSlides = Math.ceil(totalItems / itemsPerView);

    // Ensure current index is within bounds
    state.currentIndices[carouselIndex] = Math.max(0, Math.min(state.currentIndices[carouselIndex], totalSlides - 1));

    const offset = state.currentIndices[carouselIndex] * itemWidth * itemsPerView;

    carousel.style.transition = `transform ${config.transitionDuration}ms ease`;
    carousel.style.transform = `translateX(-${offset}px)`;
}

// Navigation functions
function nextSlide(carouselIndex) {
    const itemsPerView = getItemsPerView();
    const posters = state.carousels[carouselIndex]?.querySelectorAll('.poster-container');
    if (!posters) return;

    const totalItems = posters.length;
    const totalSlides = Math.ceil(totalItems / itemsPerView);

    state.currentIndices[carouselIndex]++;
    if (state.currentIndices[carouselIndex] >= totalSlides) {
        state.currentIndices[carouselIndex] = 0;
    }
    updateCarousel(carouselIndex);
}

function prevSlide(carouselIndex) {
    const itemsPerView = getItemsPerView();
    const posters = state.carousels[carouselIndex]?.querySelectorAll('.poster-container');
    if (!posters) return;

    const totalItems = posters.length;
    const totalSlides = Math.ceil(totalItems / itemsPerView);

    state.currentIndices[carouselIndex]--;
    if (state.currentIndices[carouselIndex] < 0) {
        state.currentIndices[carouselIndex] = totalSlides - 1;
    }
    updateCarousel(carouselIndex);
}

// Touch event handlers
function handleTouchStart(e, carouselIndex) {
    state.touchStartX = e.touches[0].clientX;
    state.isDragging = true;
    state.carousels[carouselIndex].style.transition = 'none';
}

function handleTouchMove(e, carouselIndex) {
    if (!state.isDragging) return;

    const touchCurrentX = e.touches[0].clientX;
    const touchDiff = state.touchStartX - touchCurrentX;

    const posters = state.carousels[carouselIndex].querySelectorAll('.poster-container');
    const itemWidth = posters[0].offsetWidth + 20;
    const offset = state.currentIndices[carouselIndex] * itemWidth * getItemsPerView();

    state.carousels[carouselIndex].style.transform = `translateX(-${offset - touchDiff}px)`;
}

function handleTouchEnd(carouselIndex) {
    if (!state.isDragging) return;

    const touchEndX = event.changedTouches[0].clientX;
    const touchDiff = state.touchStartX - touchEndX;

    if (Math.abs(touchDiff) > config.touchThreshold) {
        if (touchDiff > 0) {
            nextSlide(carouselIndex);
        } else {
            prevSlide(carouselIndex);
        }
    } else {
        updateCarousel(carouselIndex);
    }

    state.isDragging = false;
}

// Mouse event handlers
function handleMouseDown(e, carouselIndex) {
    state.touchStartX = e.clientX;
    state.isDragging = true;
    state.carousels[carouselIndex].style.transition = 'none';
}

function handleMouseMove(e, carouselIndex) {
    if (!state.isDragging) return;

    const mouseCurrentX = e.clientX;
    const mouseDiff = state.touchStartX - mouseCurrentX;

    const posters = state.carousels[carouselIndex].querySelectorAll('.poster-container');
    const itemWidth = posters[0].offsetWidth + 20;
    const offset = state.currentIndices[carouselIndex] * itemWidth * getItemsPerView();

    state.carousels[carouselIndex].style.transform = `translateX(-${offset - mouseDiff}px)`;
}

function handleMouseUp(carouselIndex) {
    if (!state.isDragging) return;

    const mouseEndX = event.clientX;
    const mouseDiff = state.touchStartX - mouseEndX;

    if (Math.abs(mouseDiff) > config.touchThreshold) {
        if (mouseDiff > 0) {
            nextSlide(carouselIndex);
        } else {
            prevSlide(carouselIndex);
        }
    } else {
        updateCarousel(carouselIndex);
    }

    state.isDragging = false;
}

// Keyboard navigation
function handleKeyDown(e, carouselIndex) {
    if (e.key === 'ArrowLeft') {
        prevSlide(carouselIndex);
    } else if (e.key === 'ArrowRight') {
        nextSlide(carouselIndex);
    }
}

// Handle window resize
function handleResize() {
    state.carousels.forEach((_, index) => {
        updateCarousel(index);
    });
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initCarousels);

// Cleanup function
function cleanup() {
    window.removeEventListener('resize', handleResize);
    state.carousels.forEach(carousel => {
        carousel.removeEventListener('touchstart', handleTouchStart);
        carousel.removeEventListener('touchmove', handleTouchMove);
        carousel.removeEventListener('touchend', handleTouchEnd);
        carousel.removeEventListener('mousedown', handleMouseDown);
        carousel.removeEventListener('mousemove', handleMouseMove);
        carousel.removeEventListener('mouseup', handleMouseUp);
        carousel.removeEventListener('mouseleave', handleMouseUp);
        carousel.removeEventListener('keydown', handleKeyDown);
    });
}

// Export functions for use in HTML
window.nextSlide = nextSlide;
window.prevSlide = prevSlide;


