document.addEventListener('DOMContentLoaded', () => {
    const slides = document.querySelectorAll('.slide');
    const nextBtn = document.getElementById('next-btn');
    const prevBtn = document.getElementById('prev-btn');
    const music = document.getElementById('background-music');
    let currentSlide = 0;
    let musicStarted = false;

    function showSlide(index) {
        slides.forEach(slide => slide.classList.remove('active'));
        slides[index].classList.add('active');

        prevBtn.style.display = index === 0 ? 'none' : 'inline-block';
        nextBtn.textContent = index === slides.length - 1 ? 'Finish' : 'Next';
    }

    nextBtn.addEventListener('click', () => {
        if (currentSlide < slides.length - 1) {
            currentSlide++;
            showSlide(currentSlide);

            // Play music for the first time when we move to the 2nd slide (index 1)
            if (currentSlide === 1 && !musicStarted) {
                music.play().catch(e => console.error("Audio playback failed:", e));
                musicStarted = true;
            }
        } else {
            alert('Merry Christmas!');
            currentSlide = 0;
            showSlide(currentSlide);
            if (musicStarted) {
                music.pause();
                music.currentTime = 0;
            }
            musicStarted = false;
        }
    });

    prevBtn.addEventListener('click', () => {
        if (currentSlide > 0) {
            currentSlide--;
            showSlide(currentSlide);
        }
    });

    showSlide(0);
});
