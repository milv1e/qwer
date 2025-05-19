document.addEventListener('DOMContentLoaded', function() {
    // Проверяем, есть ли форма на странице
    const routeForm = document.getElementById('routeForm');
    if (routeForm) {
        const submitBtn = routeForm.querySelector('.submit-btn');

        routeForm.addEventListener('submit', function(e) {
            e.preventDefault();

            const start = document.getElementById('start')?.value.trim();
            const end = document.getElementById('end')?.value.trim();

            if (!start || !end) {
                alert('Пожалуйста, заполните оба поля адресов');
                return;
            }

            // Показать индикатор загрузки
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Построение маршрута...';

            // Отправить запрос
            fetch('/map', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `start=${encodeURIComponent(start)}&end=${encodeURIComponent(end)}`
            })
            .then(response => {
                if (!response.ok) throw new Error('Ошибка сети');
                return response.text();
            })
            .then(html => {
                document.open();
                document.write(html);
                document.close();
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Ошибка при построении маршрута');
            })
            .finally(() => {
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = '<i class="fas fa-route"></i> ПОСТРОИТЬ МАРШРУТ';
                }
            });
        });
    }

    // Подсветка активной ссылки в навигации
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        if (link.href === window.location.href) {
            link.classList.add('active');
        }
    });
});
// Обработка формы контактов
const contactForm = document.querySelector('.contact-form');
if (contactForm) {
    contactForm.addEventListener('submit', function(e) {
        e.preventDefault();

        const formData = new FormData(contactForm);
        const submitBtn = contactForm.querySelector('.submit-btn');

        // Показать индикатор загрузки
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Отправка...';

        // Здесь можно добавить реальную отправку формы
        setTimeout(() => {
            alert('Сообщение отправлено! Мы свяжемся с вами в ближайшее время.');
            contactForm.reset();
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fas fa-paper-plane"></i> ОТПРАВИТЬ';
        }, 1500);
    });
}