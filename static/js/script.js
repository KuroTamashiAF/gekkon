// document.querySelectorAll('.img_question_container').forEach(img => {
//     img.addEventListener('click', () => {
//         img.classList.toggle('active');
//     });
// });

// document.querySelectorAll('.img_question_container').forEach(img => {

//     img.addEventListener('click', () => {

//         // если уже открыта -> закрыть
//         if (img.classList.contains('zoomed')) {
//             img.classList.remove('zoomed');

//             document
//                 .querySelector('.image-overlay')
//                 ?.remove();

//             return;
//         }

//         // затемнение фона
//         const overlay = document.createElement('div');
//         overlay.classList.add('image-overlay');

//         document.body.appendChild(overlay);

//         // увеличение картинки
//         img.classList.add('zoomed');

//         // закрытие по клику на фон
//         overlay.addEventListener('click', () => {
//             img.classList.remove('zoomed');
//             overlay.remove();
//         });

//     });

// });
document.querySelectorAll('.img_question_container').forEach(img => {

    img.addEventListener('click', () => {

        // ЗАКРЫТИЕ
        if (img.classList.contains('zoomed')) {

            img.classList.remove('zoomed');

            document
                .querySelector('.image-overlay')
                ?.remove();

            return;
        }

        // СОЗДАЁМ OVERLAY
        const overlay = document.createElement('div');
        overlay.classList.add('image-overlay');

        document.body.appendChild(overlay);

        // небольшой delay для transition
        setTimeout(() => {
            overlay.classList.add('active');
        }, 10);

        // УВЕЛИЧЕНИЕ
        img.classList.add('zoomed');

        // ЗАКРЫТИЕ ПО ФОНУ
        overlay.addEventListener('click', () => {

            img.classList.remove('zoomed');

            overlay.classList.remove('active');

            setTimeout(() => {
                overlay.remove();
            }, 300);

        });

    });

});