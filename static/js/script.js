document.querySelectorAll('.img_question_container').forEach(img => {
    img.addEventListener('click', () => {
        img.classList.toggle('active');
    });
});