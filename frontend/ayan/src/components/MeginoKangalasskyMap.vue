<template>
  <div class="map-wrapper">
    <!-- Панель фильтрации и управления -->
    <div class="toolbar">
      <!-- Поиск по местам -->
      <div class="search-row" @focusout="onSearchFocusOut">
        <input
          v-model="searchQuery"
          class="search-input"
          type="text"
          placeholder="Поиск места…"
          @focus="searchOpen = true"
        >
        <div v-if="searchOpen && searchQuery.trim()" class="search-results">
          <button
            v-for="place in searchResults"
            :key="place.id"
            class="search-item"
            @click="selectPlace(place)"
          >
            <b>{{ place.name }}</b>
            <span>{{ place.description }}</span>
          </button>
          <p v-if="!searchResults.length" class="search-empty">Ничего не найдено</p>
        </div>
      </div>

      <span class="toolbar-label">Категория:</span>
      <button
        v-for="cat in categories"
        :key="cat.value"
        :class="['filter-btn', { active: selectedCategory === cat.value }]"
        @click="applyFilter(cat.value)"
      >
        {{ cat.label }}
      </button>

      <div class="toolbar-actions">
        <span class="start-info">Старт: <b>{{ startPointName }}</b></span>
        <button v-if="hasRoute" class="reset-btn" @click="clearRoute">
          Сбросить маршрут
        </button>
      </div>
    </div>

    <!-- Контейнер карты -->
    <div ref="mapContainer" class="map-container"></div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';

const props = defineProps({
  apiKey: {
    type: String,
    default: 'fd5498a7-5f45-4c46-a7b2-4d6d18f39519'
  }
});

const mapContainer = ref(null);
const selectedCategory = ref('all');
const startPoint = ref([61.9585, 129.9100]);
const startPointName = ref('пгт Нижний Бестях');
const hasRoute = ref(false);
const searchQuery = ref('');
const searchOpen = ref(false);

let myMap = null;
let objectManager = null;
let currentRoute = null;

// Категории для панели фильтров
const categories = [
  { value: 'all', label: 'Все объекты' },
  { value: 'transport', label: 'Транспорт и узлы' },
  { value: 'center', label: 'Крупные сёла' },
  { value: 'culture', label: 'Культура и отдых' }
];

// Границы Мегино-Кангаласского улуса: [[юго-запад], [северо-восток]]
const ULUS_BOUNDS = [
  [60.8500, 129.6000],
  [62.5500, 131.6500]
];

// Точки улуса загружаются из базы (GET /places)
const places = ref([]);

// Загрузчик скрипта Яндекс Карт JS API 2.1
function loadYandexMaps(apiKey) {
  return new Promise((resolve, reject) => {
    if (window.ymaps && window.ymaps.Map) {
      window.ymaps.ready(resolve);
      return;
    }

    const script = document.createElement('script');
    script.src = `https://api-maps.yandex.ru/2.1/?apikey=${apiKey}&lang=ru_RU`;
    script.async = true;
    script.onload = () => window.ymaps.ready(resolve);
    script.onerror = (err) => {
      console.error('Ошибка загрузки Яндекс Карт:', err);
      reject(err);
    };
    document.head.appendChild(script);
  });
}


function initMap() {
  const ymaps = window.ymaps;

  myMap = new ymaps.Map(
    mapContainer.value,
    {
      center: [61.8200, 130.2500],
      zoom: 9,
      controls: ['zoomControl', 'typeSelector', 'fullscreenControl']
    },
    {
      restrictMapArea: ULUS_BOUNDS, // Жёсткое ограничение области улуса
      minZoom: 8,
      maxZoom: 18
    }
  );

  objectManager = new ymaps.ObjectManager({
    clusterize: true,
    gridSize: 32
  });

  // Формируем GeoJSON из точек, загруженных из базы
  const featureCollection = {
    type: 'FeatureCollection',
    features: places.value.map((place) => ({
      type: 'Feature',
      id: place.id,
      geometry: {
        type: 'Point',
        coordinates: place.coords
      },
      properties: {
        category: place.category,
        placeName: place.name,
        coords: place.coords,
        balloonContentHeader: place.name,
        balloonContentBody: `
          <p style="margin: 6px 0 10px;">${place.description}</p>
          <div style="display: flex; gap: 6px;">
            <button data-action="set-start" data-id="${place.id}" style="padding: 5px 8px; cursor: pointer;">
              Отсюда
            </button>
            <button data-action="build-route" data-id="${place.id}" style="padding: 5px 8px; cursor: pointer; background: #ffcc00; border: 1px solid #d4aa00;">
              Маршрут сюда
            </button>
          </div>
        `
      },
      options: {
        preset: place.preset
      }
    }))
  };

  objectManager.add(featureCollection);
  myMap.geoObjects.add(objectManager);
}

// Обработчик кликов по кнопкам внутри балуна (делегирование событий во Vue)
function handleBalloonClick(event) {
  const button = event.target.closest('button[data-action]');
  if (!button) return;

  const action = button.dataset.action;
  const placeId = Number(button.dataset.id);
  const place = places.value.find((p) => p.id === placeId);
  if (!place) return;

  if (action === 'set-start') {
    startPoint.value = place.coords;
    startPointName.value = place.name;
    myMap?.balloon.close();
  } else if (action === 'build-route') {
    buildRouteTo(place.coords);
  }
}

// Поиск по местам
const searchResults = computed(() => {
  const q = searchQuery.value.trim().toLowerCase();
  if (!q) return [];
  return places.value.filter((p) =>
    p.name.toLowerCase().includes(q) || p.description.toLowerCase().includes(q)
  );
});

function selectPlace(place) {
  searchQuery.value = place.name;
  searchOpen.value = false;
  if (!myMap || !objectManager) return;

  // если место скрыто фильтром категорий — сбрасываем фильтр
  if (selectedCategory.value !== 'all' && place.category !== selectedCategory.value) {
    applyFilter('all');
  }

  myMap.setCenter(place.coords, 14, { duration: 300 });
  objectManager.objects.balloon.open(place.id);
}

function onSearchFocusOut(e) {
  // закрываем список, только если фокус ушёл за пределы блока поиска
  if (!e.currentTarget.contains(e.relatedTarget)) {
    searchOpen.value = false;
  }
}

// Фильтрация объектов
function applyFilter(category) {  selectedCategory.value = category;
  if (!objectManager) return;

  if (category === 'all') {
    objectManager.setFilter(() => true);
  } else {
    objectManager.setFilter((obj) => obj.properties.category === category);
  }
}

// Построение маршрута
function buildRouteTo(destCoords) {
  if (!myMap || !window.ymaps) return;
  clearRoute();

  currentRoute = new window.ymaps.multiRouter.MultiRoute(
    {
      referencePoints: [startPoint.value, destCoords],
      params: {
        routingMode: 'auto'
      }
    },
    {
      boundsAutoApply: true
    }
  );

  myMap.geoObjects.add(currentRoute);
  hasRoute.value = true;
  myMap.balloon.close();
}

// Сброс маршрута
function clearRoute() {
  if (myMap && currentRoute) {
    myMap.geoObjects.remove(currentRoute);
    currentRoute = null;
  }
  hasRoute.value = false;
}

onMounted(async () => {
  try {
    const res = await fetch('http://127.0.0.1:8000/places');
    places.value = await res.json();
  } catch (err) {
    console.error('Не удалось загрузить места:', err);
  }
  await loadYandexMaps(props.apiKey);
  initMap();
  mapContainer.value?.addEventListener('click', handleBalloonClick);
});

onUnmounted(() => {
  mapContainer.value?.removeEventListener('click', handleBalloonClick);
  if (myMap) {
    myMap.destroy();
    myMap = null;
  }
});
</script>

<style scoped>
.map-wrapper {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: calc(100dvh - 68px);
}

.toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background-color: #2c2d2c;
  border-bottom: 1px solid #454645;
}

.search-row {
  position: relative;
  width: 100%;
}

.search-input {
  width: 100%;
  box-sizing: border-box;
  padding: 9px 12px;
  border: 1px solid #555;
  border-radius: 6px;
  font-size: 14px;
  background: #383938;
  color: #eee;
}

.search-input::placeholder {
  color: #999;
}

.search-input:focus {
  outline: none;
  border-color: #cafb87;
}

.search-results {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  right: 0;
  z-index: 10;
  background: #2c2d2c;
  border: 1px solid #555;
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
  overflow: hidden;
}

.search-item {
  display: block;
  width: 100%;
  padding: 9px 12px;
  border: none;
  border-bottom: 1px solid #454645;
  background: #2c2d2c;
  color: #eee;
  text-align: left;
  cursor: pointer;
}

.search-item:hover {
  background: #383938;
}

.search-item b {
  display: block;
  font-size: 14px;
}

.search-item span {
  font-size: 12px;
  color: #aaa;
}

.search-empty {
  margin: 0;
  padding: 10px 12px;
  font-size: 13px;
  color: #999;
}

.toolbar-label {
  font-size: 14px;
  color: #bbb;
  margin-right: 4px;
}

.filter-btn {
  padding: 7px 14px;
  border: 1px solid #555;
  background-color: #383938;
  color: #eee;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.15s;
}

.filter-btn:hover {
  background-color: #454645;
}

.filter-btn.active {
  background-color: #cafb87;
  border-color: #cafb87;
  color: #383938;
  font-weight: 600;
}

.toolbar-actions {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 12px;
}

.start-info {
  font-size: 13px;
  color: #ddd;
}

.reset-btn {
  padding: 7px 12px;
  border: 1px solid #a71d2a;
  background-color: #3d2126;
  color: #ff8a94;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
}

.map-container {
  flex: 1;
  width: 100%;
}
</style>
