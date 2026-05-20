// script.js - чистый JavaScript файл

// Инициализация карты
function initMap() {
    const mapElement = document.getElementById('map');
    if (!mapElement) return;
    
    // Координаты Казани
    const kazanCoords = [55.796127, 49.106405];
    
    const map = L.map('map').setView(kazanCoords, 13);
    
    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> &copy; CartoDB',
        subdomains: 'abcd',
        maxZoom: 19
    }).addTo(map);
    
    // Маркеры самокатов
    const scooterLocations = [
        { lat: 55.796127, lng: 49.106405, name: "ул. Баумана, 25" },
        { lat: 55.795300, lng: 49.108500, name: "Площадь Тукая" },
        { lat: 55.798900, lng: 49.104200, name: "Кремлёвская набережная" },
        { lat: 55.792000, lng: 49.112000, name: "Стадион Ак Барс" },
        { lat: 55.788500, lng: 49.122000, name: "Парк Горького" }
    ];
    
    scooterLocations.forEach(loc => {
        L.marker([loc.lat, loc.lng])
            .bindPopup(`<b>📍 ${loc.name}</b><br>Самокат доступен`)
            .addTo(map);
    });
    
    // Добавим несколько случайных самокатов
    for (let i = 0; i < 15; i++) {
        const lat = 55.78 + (Math.random() * 0.04);
        const lng = 49.09 + (Math.random() * 0.06);
        L.marker([lat, lng], {
            icon: L.divIcon({
                className: 'custom-scooter-marker',
                html: '🛴',
                iconSize: [30, 30],
                popupAnchor: [0, -15]
            })
        }).bindPopup('🛴 Электросамокат #' + (100 + i)).addTo(map);
    }
}

// Запуск карты при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    initMap();
    
    // Автоматическое скрытие flash-сообщений
    const flashMessages = document.querySelectorAll('.flash-message');
    if (flashMessages.length > 0) {
        setTimeout(() => {
            flashMessages.forEach(msg => {
                msg.style.transition = 'opacity 0.3s';
                msg.style.opacity = '0';
                setTimeout(() => msg.remove(), 300);
            });
        }, 4000);
    }
    
    // Плавная прокрутка для якорных ссылок
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href === '#') return;
            
            const target = document.querySelector(href);
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
});

// Анимация счетчиков на главной странице
function animateNumbers() {
    const statNumbers = document.querySelectorAll('.stat-number');
    statNumbers.forEach(stat => {
        const finalValue = stat.innerText;
        if (finalValue && !isNaN(parseInt(finalValue))) {
            let current = 0;
            const increment = Math.ceil(parseInt(finalValue) / 50);
            const timer = setInterval(() => {
                current += increment;
                if (current >= parseInt(finalValue)) {
                    stat.innerText = finalValue;
                    clearInterval(timer);
                } else {
                    stat.innerText = current;
                }
            }, 30);
        }
    });
}

// Запускаем анимацию чисел, если они есть на странице
if (document.querySelector('.stat-number')) {
    setTimeout(animateNumbers, 500);
}