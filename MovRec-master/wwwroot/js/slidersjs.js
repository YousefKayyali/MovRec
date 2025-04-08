/*
let index = 0;
const carousel = document.querySelectorAll('.carousel');
const items = document.querySelectorAll('.carousel .poster-container');
const itemsPerView = 5;
const totalItems = 35;
const totalSlides = Math.ceil(totalItems / itemsPerView);

function updateCarousel(i) {
    const itemWidth = items[0].clientWidth + 20;
    const offset = index * itemWidth * itemsPerView;
    carousel[i].style.transform = `translateX(-${offset}px)`;
}

function nextSlide(i) {
    index = (index + 1) % totalSlides;
    updateCarousel(i);
}

function prevSlide(i) {
    index = (index - 1) % totalSlides;
    if (index < 0) {
        index = totalSlides - 1;
    }
    updateCarousel(i);
}
    */// Track current slide index for each carousel
const currentIndices = [0, 0, 0, 0];
const carousels = document.querySelectorAll('.carousel');
const posters = document.querySelectorAll('.poster-container');
const itemsPerView = 5; // Number of items visible at once

// Calculate total items and slides for each carousel
const totalItems = posters.length / carousels.length;
const totalSlides = Math.ceil(totalItems / itemsPerView);

function updateCarousel(carouselIndex) {
    const carousel = carousels[carouselIndex];
    const itemWidth = posters[0].offsetWidth + 20; // Width + margin
    const offset = currentIndices[carouselIndex] * itemWidth * itemsPerView;

    carousel.style.transform = `translateX(-${offset}px)`;
}

function nextSlide(carouselIndex) {
    currentIndices[carouselIndex]++;
    if (currentIndices[carouselIndex] >= totalSlides) {
        currentIndices[carouselIndex] = 0;
    }
    updateCarousel(carouselIndex);
}

function prevSlide(carouselIndex) {
    currentIndices[carouselIndex]--;
    if (currentIndices[carouselIndex] < 0) {
        currentIndices[carouselIndex] = totalSlides - 1;
    }
    updateCarousel(carouselIndex);
}


