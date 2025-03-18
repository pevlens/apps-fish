function showTab(tabId) {
    // Скрываем все вкладки
    var tabs = document.querySelectorAll('.tab-content');
    tabs.forEach(function(tab) {
        tab.classList.remove('active');
    });

    // Убираем активный класс у всех кнопок
    var buttons = document.querySelectorAll('.tab-button');
    buttons.forEach(function(button) {
        button.classList.remove('active');
    });

    // Показываем выбранную вкладку
    document.getElementById(tabId).classList.add('active');

    // Делаем кнопку активной
    document.querySelector(`[onclick="showTab('${tabId}')"]`).classList.add('active');
}

const banner = document.getElementById('banner');
const images = [
    'https://minio-api.psncorp.store/django-static/images/fishers.jpg',
    'https://minio-api.psncorp.store/django-static/images/fishers1.jpg',
    'https://minio-api.psncorp.store/django-static/images/fishers2.jpg',
    'https://minio-api.psncorp.store/django-static/images/fishers4.jpg',
];


// Проверяем, что массив изображений не пуст
if (images.length === 0) {
    console.error('Массив изображений пуст! Добавьте изображения.');
} else {
    // Предзагрузка изображений, чтобы избежать мигания
    function preloadImages(imageArray) {
        imageArray.forEach((src) => {
            const img = new Image();
            img.src = src;
            img.onerror = () => {
                console.error(`Ошибка загрузки изображения: ${src}`);
            };
        });
    }

    preloadImages(images); // Предзагружаем изображения

    let currentIndex = 0;

    function changeBackground() {
        // Проверяем, что текущий индекс в пределах массива
        if (currentIndex >= images.length) {
            currentIndex = 0; // Начинаем цикл заново
        }

        // Меняем фоновое изображение
        banner.style.backgroundImage = `url(${images[currentIndex]})`;

        // Увеличиваем индекс для следующего изображения
        currentIndex++;
    }

    // Меняем фон каждую секунду
    setInterval(changeBackground, 20000);

    // Устанавливаем первое изображение сразу
    changeBackground();
}

