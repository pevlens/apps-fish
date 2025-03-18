document.addEventListener('DOMContentLoaded', function() {
    const seasonTabs = document.querySelectorAll('.season-tabs button');
    const fishTabs = document.querySelectorAll('.fish-tabs button');
    const tableRows = document.querySelectorAll('.trophies-table tbody tr');

    // Обработчики для вкладок сезонов:
    seasonTabs.forEach(button => {
        button.addEventListener('click', () => {
            // Получаем выбранный сезон из data-атрибута
            const season = button.dataset.season;
            // Перенаправляем страницу, добавляя GET-параметр season
            window.location.search = `?season=${season}`;
        });
    });

    // Обработчики для вкладок видов рыбы (клиентская фильтрация):
    fishTabs.forEach(button => {
        button.addEventListener('click', () => {
            fishTabs.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            filterTable();
        });
    });

    // Функция фильтрации строк таблицы (по виду рыбы)
    function filterTable() {
        const selectedFish = document.querySelector('.fish-tabs button.active')?.dataset.fish || 'all';
        tableRows.forEach(row => {
            const fish = row.getAttribute('data-fish');

            row.style.display = (selectedFish === 'all' || fish === selectedFish) ? '' : 'none';

            // При фильтрации удаляем дополнительные (accordion) ряды, если они существуют
            const nextRow = row.nextElementSibling;
            if (nextRow && nextRow.classList.contains('details-row')) {
                nextRow.remove();
            }
        });
    }

    // При клике на строку показываем дополнительный ряд с фотографией под ней
    tableRows.forEach(row => {
        row.addEventListener('click', () => {
            // Действуем только если строка видима (не скрыта фильтром)
            if (row.style.display !== 'none') {
                const nextRow = row.nextElementSibling;
                if (nextRow && nextRow.classList.contains('details-row')) {
                    // Если дополнительный ряд уже существует – удаляем его (закрываем)
                    nextRow.remove();
                } else {
                    // Если дополнительного ряда нет – создаем его
                    const detailsRow = document.createElement('tr');
                    detailsRow.classList.add('details-row');

                    // Определяем число столбцов по количеству ячеек заголовка
                    const columnCount = document.querySelector('.trophies-table thead tr').children.length;
                    const detailsCell = document.createElement('td');
                    detailsCell.setAttribute('colspan', columnCount);

                    // Вариант: копируем содержимое ячейки с фото из строки, если она есть
                    const trophyCell = row.querySelector('.trophy-photo-cell');
                    if (trophyCell) {
                        detailsCell.innerHTML = trophyCell.innerHTML;
                    } else {
                        detailsCell.textContent = "Фото трофея отсутствует";
                    }

                    detailsRow.appendChild(detailsCell);
                    // Вставляем созданный ряд сразу после нажатой строки
                    row.parentNode.insertBefore(detailsRow, row.nextSibling);
                }
            }
        });
    });

    // Функция установки первой активной вкладки, если ни одна не активна
    function setDefaultActive(tabs) {
        const activeTab = Array.from(tabs).find(tab => tab.classList.contains('active'));
        if (!activeTab && tabs.length > 0) {
            tabs[0].classList.add('active');
        }
    }

    // Инициализация активных вкладок и первичная фильтрация
    setDefaultActive(fishTabs);
    filterTable();
});