document.addEventListener('DOMContentLoaded', () => {
    const slides = document.querySelectorAll('.slide');
    const nextBtn = document.getElementById('next-btn');
    const prevBtn = document.getElementById('prev-btn');
    const audio = document.getElementById('jukebox-audio');
    const playPauseBtn = document.getElementById('play-pause-btn');
    let currentSlide = 0;

    const songs = [
        './dance-of-the-sugar-plum-fairies.mp3',
        './jingle-bells.mp3',
        './we-wish-you-a-merry-christmas.mp3',
        './deck-the-halls.mp3',
        './silent-night.mp3',
        './o-holy-night.mp3'
    ];

    function showSlide(index) {
        // Hide all slides
        slides.forEach(slide => {
            slide.classList.remove('active');
        });

        // Show the correct slide
        slides[index].classList.add('active');

        // Update button visibility
        if (currentSlide === 0) {
            prevBtn.style.display = 'none';
        } else {
            prevBtn.style.display = 'inline-block';
        }

        if (currentSlide === slides.length - 1) {
            nextBtn.textContent = 'Finish';
        } else {
            nextBtn.textContent = 'Next';
        }

        // Update audio source
        if (songs[index]) {
            audio.src = songs[index];
            audio.play();
        }
    }

    playPauseBtn.addEventListener('click', () => {
        if (audio.paused) {
            audio.play();
        } else {
            audio.pause();
        }
    });

    nextBtn.addEventListener('click', () => {
        if (currentSlide < slides.length - 1) {
            currentSlide++;
            showSlide(currentSlide);
        } else {
            // Optional: Restart or go to a final message
            alert('Merry Christmas!');
            currentSlide = 0;
            showSlide(currentSlide);
        }
    });

    prevBtn.addEventListener('click', () => {
        if (currentSlide > 0) {
            currentSlide--;
            showSlide(currentSlide);
        }
    });

    // Initialize the first slide
    showSlide(0);
});
