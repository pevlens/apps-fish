document.addEventListener('DOMContentLoaded', function() {
    // === Функционал для вкладок сезонов ===
    const seasonTabs = document.querySelectorAll('.season-tabs button');
  
    seasonTabs.forEach(tab => {
      tab.addEventListener('click', function() {
        // Получаем выбранный сезон из data-атрибута
        const season = tab.getAttribute('data-season');
        // Обновляем URL с GET-параметром season
        window.location.href = updateUrlParameter(window.location.href, 'season', season);
      });
    });
  
    /**
     * Функция обновления GET-параметра в URL.
     * Если параметр существует – обновляет его значение, иначе добавляет.
     */
    function updateUrlParameter(url, param, paramVal) {
      let newAdditionalURL = "";
      let tempArray = url.split("?");
      const baseURL = tempArray[0];
      const additionalURL = tempArray[1];
      if (additionalURL) {
        const temp = additionalURL.split("&");
        let found = false;
        for (let i = 0; i < temp.length; i++) {
          if (temp[i].split('=')[0] === param) {
            temp[i] = param + "=" + paramVal;
            found = true;
          }
        }
        if (!found) {
          temp.push(param + "=" + paramVal);
        }
        newAdditionalURL = temp.join("&");
      } else {
        newAdditionalURL = param + "=" + paramVal;
      }
      return baseURL + "?" + newAdditionalURL;
    }
  
    // === Функционал для переключения статистики по видам рыб ===
    const fishButtons = document.querySelectorAll('.fish-buttons button');
    const fishStatsContainers = document.querySelectorAll('.fish-stat');
  
    fishButtons.forEach(button => {
      button.addEventListener('click', function() {
        const selectedFish = button.getAttribute('data-fish');
  
        // Снимаем класс active со всех кнопок и скрываем все контейнеры статистики
        fishButtons.forEach(btn => btn.classList.remove('active'));
        fishStatsContainers.forEach(container => {
          container.style.display = 'none';
        });
  
        // Активируем выбранную кнопку и показываем соответствующий контейнер
        button.classList.add('active');
        const container = document.querySelector(`.fish-stat[data-fish="${selectedFish}"]`);
        if (container) {
          container.style.display = 'block';
        }
      });
    });
  
    // Если ни одна кнопка не активна, делаем активной первую
    if (fishButtons.length > 0 && !document.querySelector('.fish-buttons button.active')) {
      fishButtons[0].classList.add('active');
      fishStatsContainers.forEach((container, idx) => {
        container.style.display = idx === 0 ? 'block' : 'none';
      });
    }
  });