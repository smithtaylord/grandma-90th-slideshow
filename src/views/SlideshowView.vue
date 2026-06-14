<template>
  <div class="slideshow" @mousemove="showControls" @touchstart="showControls" @touchend="onSwipe">
    <div v-if="!started" class="start-screen" @click="startSlideshow">
      <h1>{{ config.songTitle || 'Ninety Years of Liz' }}</h1>
      <p>A celebration of 90 amazing years</p>
      <div v-if="mode === 'slideshow'" class="mode-badge">Photo Slideshow Mode</div>
      <p class="tap-hint">Tap or click to begin</p>
    </div>

    <div v-else class="slide-container">
      <transition name="fade" mode="out-in">
        <img
          :key="currentPhoto?.file"
          :src="`/photos/${currentPhoto?.file}`"
          class="slide-img"
          @error="onImgError"
        />
      </transition>

      <transition name="lyric-fade">
        <div :key="currentLyric?.text" class="lyrics-overlay" v-if="currentLyric && mode === 'full'">
          <p class="lyric-line">{{ currentLyric.text }}</p>
        </div>
      </transition>

      <div class="caption" v-if="currentPhoto?.caption">
        {{ currentPhoto.caption }}
      </div>

      <div class="photo-counter">{{ currentIndex + 1 }} / {{ config.photos.length }}</div>

      <div v-if="mode === 'slideshow'" class="nav-arrows">
        <button class="nav-btn nav-prev" @click="prevPhoto" :disabled="currentIndex === 0">&#8249;</button>
        <button class="nav-btn nav-next" @click="nextPhoto" :disabled="currentIndex === config.photos.length - 1">&#8250;</button>
      </div>
    </div>

    <div :class="['controls', { 'controls-hidden': !controlsVisible }]">
      <template v-if="mode === 'slideshow'">
        <button class="btn" @click="prevPhoto" :disabled="currentIndex === 0">&larr;</button>
        <button class="btn primary" @click="togglePlay">{{ isPlaying ? 'Pause' : 'Play' }}</button>
        <button class="btn" @click="nextPhoto" :disabled="currentIndex === config.photos.length - 1">&rarr;</button>
        <select class="speed-select" v-model.number="slideDuration">
          <option :value="3">3s</option>
          <option :value="5">5s</option>
          <option :value="8">8s</option>
          <option :value="10">10s</option>
        </select>
      </template>
      <template v-else>
        <button class="btn" @click="prevPhoto">&larr;</button>
        <button class="btn primary" @click="togglePlay">{{ isPlaying ? 'Pause' : 'Play' }}</button>
        <button class="btn" @click="nextPhoto">&rarr;</button>
        <span class="time-display" v-if="duration > 0">{{ formatTime(currentTime) }} / {{ formatTime(duration) }}</span>
      </template>
      <div class="mode-switch">
        <router-link v-if="mode === 'full'" to="/?mode=slideshow" class="sync-link">Photos Only</router-link>
        <router-link v-else to="/" class="sync-link">Full Slideshow</router-link>
        <router-link to="/sync" class="sync-link sync-link-secondary">Sync Tool</router-link>
      </div>
    </div>

    <audio
      ref="audioEl"
      :src="mode === 'full' ? '/audio/song.mp3' : undefined"
      @timeupdate="onTimeUpdate"
      @loadedmetadata="onAudioLoaded"
      @ended="onAudioEnded"
    ></audio>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const mode = computed(() => route.query.mode || 'full')

const config = ref({ photos: [], defaultDuration: 5, transitionDuration: 1 })
const lyrics = ref([])
const audioEl = ref(null)
const started = ref(false)
const currentIndex = ref(0)
const currentTime = ref(0)
const duration = ref(0)
const isPlaying = ref(false)
const controlsVisible = ref(true)
const slideDuration = ref(5)
let controlsTimer = null
let timerInterval = null
let touchStartX = 0

const currentPhoto = computed(() => config.value.photos[currentIndex.value])

const currentLyric = computed(() => {
  if (lyrics.value.length === 0) return null
  const t = currentTime.value
  let current = null
  for (let i = lyrics.value.length - 1; i >= 0; i--) {
    if (t >= lyrics.value[i].time) {
      current = lyrics.value[i]
      break
    }
  }
  return current
})

async function loadConfig() {
  try {
    const res = await fetch('/config.json')
    config.value = await res.json()
  } catch (e) {
    console.error('Failed to load config.json', e)
  }
}

async function loadLyrics() {
  if (mode.value !== 'full') return
  try {
    const res = await fetch('/lyrics.json')
    lyrics.value = await res.json()
  } catch (e) {
    console.error('Failed to load lyrics.json', e)
  }
}

function startSlideshow() {
  started.value = true
  if (mode.value === 'full' && audioEl.value) {
    audioEl.value.play().catch(() => {})
    isPlaying.value = true
  } else {
    startTimer()
    isPlaying.value = true
  }
  showControls()
}

function startTimer() {
  stopTimer()
  timerInterval = setInterval(() => {
    nextPhoto()
  }, slideDuration.value * 1000)
}

function stopTimer() {
  if (timerInterval) {
    clearInterval(timerInterval)
    timerInterval = null
  }
}

watch(slideDuration, () => {
  if (mode.value === 'slideshow' && isPlaying.value) {
    startTimer()
  }
})

function togglePlay() {
  if (mode.value === 'full' && audioEl.value) {
    if (isPlaying.value) {
      audioEl.value.pause()
    } else {
      audioEl.value.play()
    }
  } else {
    if (isPlaying.value) {
      stopTimer()
    } else {
      startTimer()
    }
  }
  isPlaying.value = !isPlaying.value
}

function nextPhoto() {
  if (currentIndex.value < config.value.photos.length - 1) {
    currentIndex.value++
  } else if (mode.value === 'slideshow') {
    currentIndex.value = 0
  }
}

function prevPhoto() {
  if (currentIndex.value > 0) {
    currentIndex.value--
  }
}

function onSwipe(e) {
  if (!started.value) return
  const touch = e.changedTouches?.[0]
  if (!touch) return
  const dx = touch.clientX - touchStartX
  if (Math.abs(dx) > 50) {
    if (dx > 0) prevPhoto()
    else nextPhoto()
  }
}

function onTimeUpdate() {
  if (!audioEl.value) return
  currentTime.value = audioEl.value.currentTime
  const totalPhotos = config.value.photos.length
  if (totalPhotos === 0 || !duration.value) return
  const photoDuration = duration.value / totalPhotos
  const newIndex = Math.min(
    Math.floor(audioEl.value.currentTime / photoDuration),
    totalPhotos - 1
  )
  if (newIndex !== currentIndex.value) {
    currentIndex.value = newIndex
  }
}

function onAudioLoaded() {
  if (audioEl.value) {
    duration.value = audioEl.value.duration
  }
}

function onAudioEnded() {
  isPlaying.value = false
}

function onImgError(e) {
  e.target.style.display = 'none'
}

function showControls() {
  controlsVisible.value = true
  clearTimeout(controlsTimer)
  controlsTimer = setTimeout(() => {
    if (isPlaying.value) controlsVisible.value = false
  }, 3000)
}

function formatTime(seconds) {
  if (!seconds || isNaN(seconds)) return '0:00'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

function onKeyDown(e) {
  if (!started.value) return
  if (e.code === 'Space') {
    e.preventDefault()
    togglePlay()
  }
  if (e.code === 'ArrowRight') {
    e.preventDefault()
    nextPhoto()
  }
  if (e.code === 'ArrowLeft') {
    e.preventDefault()
    prevPhoto()
  }
}

function onTouchStart(e) {
  touchStartX = e.touches?.[0]?.clientX || 0
}

onMounted(() => {
  loadConfig()
  loadLyrics()
  window.addEventListener('keydown', onKeyDown)
  window.addEventListener('touchstart', onTouchStart, { passive: true })
})

onUnmounted(() => {
  stopTimer()
  window.removeEventListener('keydown', onKeyDown)
  window.removeEventListener('touchstart', onTouchStart)
  if (controlsTimer) clearTimeout(controlsTimer)
})
</script>

<style scoped>
.slideshow {
  width: 100%;
  height: 100vh;
  background: #000;
  position: relative;
  overflow: hidden;
  cursor: none;
  user-select: none;
}

.slideshow:hover {
  cursor: default;
}

.start-screen {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  color: #fff;
  text-align: center;
  cursor: pointer;
}

.start-screen h1 {
  font-family: 'Playfair Display', serif;
  font-size: 3rem;
  margin-bottom: 0.5rem;
}

.start-screen p {
  font-size: 1.2rem;
  color: #aaa;
  margin-bottom: 2rem;
}

.start-screen .mode-badge {
  background: rgba(140, 180, 216, 0.3);
  border: 1px solid rgba(140, 180, 216, 0.5);
  color: #8cb4d8;
  padding: 0.3rem 1rem;
  border-radius: 20px;
  font-size: 0.85rem;
  margin-bottom: 1.5rem;
}

.start-screen .tap-hint {
  font-size: 1rem;
  color: #666;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}

.slide-container {
  width: 100%;
  height: 100%;
  position: relative;
}

.slide-img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 1s ease-in-out;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.lyrics-overlay {
  position: absolute;
  bottom: 10%;
  left: 50%;
  transform: translateX(-50%);
  text-align: center;
  width: 90%;
  max-width: 900px;
  background: rgba(0, 0, 0, 0.85);
  border-radius: 8px;
  padding: 0.75rem 2rem;
  pointer-events: none;
  z-index: 10;
}

.lyric-line {
  font-family: 'Playfair Display', serif;
  font-size: 2.2rem;
  color: #fff;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.8), 0 0 20px rgba(0, 0, 0, 0.5);
  line-height: 1.3;
}

.lyric-fade-enter-active {
  transition: opacity 0.5s ease-in, transform 0.5s ease-in;
}

.lyric-fade-leave-active {
  transition: opacity 0.3s ease-out, transform 0.3s ease-out;
}

.lyric-fade-enter-from {
  opacity: 0;
  transform: translateX(-50%) translateY(10px);
}

.lyric-fade-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(-10px);
}

.caption {
  position: absolute;
  bottom: 3%;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.6);
  color: #fff;
  padding: 0.5rem 1.5rem;
  border-radius: 4px;
  font-size: 1.1rem;
  max-width: 80%;
  text-align: center;
  z-index: 20;
}

.photo-counter {
  position: absolute;
  top: 1rem;
  right: 1rem;
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.85rem;
  font-family: monospace;
  z-index: 20;
}

.nav-arrows {
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  transform: translateY(-50%);
  display: flex;
  justify-content: space-between;
  pointer-events: none;
  padding: 0 0.5rem;
  z-index: 25;
}

.nav-btn {
  pointer-events: auto;
  background: rgba(0, 0, 0, 0.4);
  color: #fff;
  border: none;
  font-size: 3rem;
  line-height: 1;
  padding: 0.5rem 0.8rem;
  cursor: pointer;
  border-radius: 8px;
  transition: background 0.2s;
}

.nav-btn:hover:not(:disabled) {
  background: rgba(0, 0, 0, 0.7);
}

.nav-btn:disabled {
  opacity: 0.2;
  cursor: default;
}

.controls {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 1rem;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.7));
  transition: opacity 0.3s;
  z-index: 30;
}

.controls-hidden {
  opacity: 0;
  pointer-events: none;
}

.mode-switch {
  position: absolute;
  right: 1rem;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.25rem;
}

.time-display {
  color: #ccc;
  font-family: monospace;
  font-size: 0.9rem;
}

.sync-link {
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.8rem;
  text-decoration: none;
}

.sync-link:hover {
  color: rgba(255, 255, 255, 0.8);
}

.sync-link-secondary {
  font-size: 0.7rem;
}

.speed-select {
  background: rgba(255, 255, 255, 0.15);
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  padding: 0.3rem 0.5rem;
  font-size: 0.85rem;
  cursor: pointer;
}

.speed-select option {
  background: #333;
  color: #fff;
}

.btn {
  background: rgba(255, 255, 255, 0.15);
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  padding: 0.4rem 1rem;
  cursor: pointer;
  font-size: 0.9rem;
}

.btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.25);
}

.btn:disabled {
  opacity: 0.4;
  cursor: default;
}

.btn.primary {
  background: rgba(140, 180, 216, 0.3);
  border-color: rgba(140, 180, 216, 0.5);
}

@media (max-width: 768px) {
  .lyric-line {
    font-size: 1.4rem;
  }
  .lyrics-overlay {
    bottom: 6%;
  }
  .start-screen h1 {
    font-size: 2rem;
  }
  .nav-btn {
    font-size: 2rem;
    padding: 0.4rem 0.6rem;
  }
}
</style>