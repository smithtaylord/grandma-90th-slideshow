<template>
  <div class="slideshow" @mousemove="showControls" @touchstart="showControls" @touchend="onSwipe">
    <div v-if="ended" class="end-card">
      <h1 class="end-title">Happy 90th Birthday,</h1>
      <h1 class="end-title end-name">Grandma Liz!</h1>
    </div>

    <div v-else-if="!started" class="start-screen" @click="startSlideshow">
      <div class="start-content">
        <h1 class="start-title">{{ config.songTitle || 'Ninety Years of Liz' }}</h1>
        <div class="start-divider"><span class="divider-ornament">&#10047;</span></div>
        <p class="start-subtitle">A celebration of 90 amazing years</p>
        <p class="start-date">June 25, 2026</p>
        <div v-if="mode === 'slideshow'" class="mode-badge">Photo Slideshow Mode</div>
        <p class="tap-hint">Tap or click to begin</p>
      </div>
    </div>

    <div v-else class="slide-container">
      <transition name="fade">
        <img
          :key="currentPhoto?.file"
          :src="`/photos/${currentPhoto?.file}`"
          :class="['slide-img', kenBurnsClass]"
          @error="onImgError"
        />
      </transition>

      <div class="lyrics-gradient" v-if="mode === 'full'"></div>

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

    <div :class="['controls', { 'controls-hidden': !controlsVisible }]" v-if="!ended">
      <template v-if="mode === 'slideshow'">
        <button class="btn" @click="prevPhoto" :disabled="currentIndex === 0">&larr;</button>
        <button class="btn btn-play" @click="togglePlay">{{ isPlaying ? '❚❚' : '▶' }}</button>
        <button class="btn" @click="nextPhoto" :disabled="currentIndex === config.photos.length - 1">&rarr;</button>
        <div class="speed-pills">
          <button
            v-for="speed in [3, 5, 8, 10]"
            :key="speed"
            :class="['speed-pill', { 'speed-pill-active': slideDuration === speed }]"
            @click="slideDuration = speed"
          >{{ speed }}s</button>
        </div>
      </template>
      <template v-else>
        <button class="btn" @click="prevPhoto">&larr;</button>
        <button class="btn btn-play" @click="togglePlay">{{ isPlaying ? '❚❚' : '▶' }}</button>
        <button class="btn" @click="nextPhoto">&rarr;</button>
        <span class="time-display" v-if="duration > 0">{{ formatTime(currentTime) }} / {{ formatTime(duration) }}</span>
      </template>
      <div class="mode-switch">
        <router-link v-if="mode === 'full'" to="/?mode=slideshow" class="mode-btn">Photos Only</router-link>
        <router-link v-else to="/" class="mode-btn">Full Slideshow</router-link>
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
const ended = ref(false)
const currentIndex = ref(0)
const currentTime = ref(0)
const duration = ref(0)
const isPlaying = ref(false)
const controlsVisible = ref(true)
const slideDuration = ref(5)
let controlsTimer = null
let timerInterval = null
let touchStartX = 0
let kenBurnsToggle = false

const currentPhoto = computed(() => config.value.photos[currentIndex.value])

const kenBurnsClass = computed(() => {
  kenBurnsToggle = !kenBurnsToggle
  return kenBurnsToggle ? 'ken-burns-a' : 'ken-burns-b'
})

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
  ended.value = false
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
  ended.value = true
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
  if (ended.value) {
    if (e.code === 'Space' || e.code === 'Enter') {
      e.preventDefault()
      ended.value = false
      started.value = false
    }
    return
  }
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
  user-select: none;
  font-family: 'Inter', sans-serif;
}

.slideshow:hover {
  cursor: default;
}

/* --- Start Screen --- */

.start-screen {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100vh;
  color: #fff;
  text-align: center;
  cursor: pointer;
  background: radial-gradient(ellipse at center, #0d1b2a 0%, #0a0a0a 70%, #000 100%);
}

.start-content {
  animation: fadeInUp 1.2s ease-out;
}

.start-title {
  font-family: 'Playfair Display', serif;
  font-weight: 700;
  font-size: 3.5rem;
  letter-spacing: 0.01em;
  margin-bottom: 0.5rem;
  line-height: 1.2;
}

.start-divider {
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 1.25rem 0;
  gap: 1rem;
}

.start-divider::before,
.start-divider::after {
  content: '';
  width: 80px;
  height: 1px;
  background: linear-gradient(to var(--dir, right), transparent, rgba(255, 255, 255, 0.3), transparent);
}

.start-divider::before {
  --dir: right;
}

.start-divider::after {
  --dir: left;
}

.divider-ornament {
  color: rgba(255, 255, 255, 0.35);
  font-size: 1.2rem;
}

.start-subtitle {
  font-size: 1.2rem;
  font-weight: 300;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 0.5rem;
  letter-spacing: 0.03em;
}

.start-date {
  font-size: 0.95rem;
  font-weight: 300;
  color: rgba(255, 255, 255, 0.4);
  letter-spacing: 0.1em;
  text-transform: uppercase;
  margin-bottom: 2rem;
}

.mode-badge {
  display: inline-block;
  background: rgba(140, 180, 216, 0.15);
  border: 1px solid rgba(140, 180, 216, 0.35);
  color: rgba(140, 180, 216, 0.8);
  padding: 0.3rem 1.2rem;
  border-radius: 20px;
  font-size: 0.85rem;
  letter-spacing: 0.05em;
  margin-bottom: 1.5rem;
}

.tap-hint {
  font-size: 0.95rem;
  color: rgba(255, 255, 255, 0.3);
  letter-spacing: 0.05em;
  animation: pulse 2.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 0.8; }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* --- End Card --- */

.end-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  text-align: center;
  background: radial-gradient(ellipse at center, #0d1b2a 0%, #0a0a0a 70%, #000 100%);
  animation: fadeInUp 1.5s ease-out;
}

.end-title {
  font-family: 'Playfair Display', serif;
  font-weight: 700;
  font-size: 3.2rem;
  color: #fff;
  letter-spacing: 0.01em;
  line-height: 1.3;
  animation: fadeInUp 1.8s ease-out;
}

.end-name {
  color: #e8c88a;
  font-size: 3.8rem;
  margin-top: 0.25rem;
  animation-delay: 0.3s;
}

/* --- Slide Container --- */

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

.ken-burns-a {
  animation: kenBurnsA 8s ease-in-out forwards;
}

.ken-burns-b {
  animation: kenBurnsB 8s ease-in-out forwards;
}

@keyframes kenBurnsA {
  from { transform: scale(1); }
  to { transform: scale(1.06) translateX(-1%); }
}

@keyframes kenBurnsB {
  from { transform: scale(1); }
  to { transform: scale(1.06) translateX(1%); }
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s ease-in-out;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.fade-enter-to {
  opacity: 1;
}

/* --- Lyrics --- */

.lyrics-gradient {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 35%;
  background: linear-gradient(to bottom, transparent 0%, rgba(0, 0, 0, 0.1) 30%, rgba(0, 0, 0, 0.7) 70%, rgba(0, 0, 0, 0.85) 100%);
  pointer-events: none;
  z-index: 5;
}

.lyrics-overlay {
  position: absolute;
  bottom: 12%;
  left: 50%;
  transform: translateX(-50%);
  text-align: center;
  width: 90%;
  max-width: 950px;
  pointer-events: none;
  z-index: 10;
}

.lyric-line {
  font-family: 'Playfair Display', serif;
  font-weight: 700;
  font-size: 2.4rem;
  color: #fff;
  text-shadow: 0 2px 12px rgba(0, 0, 0, 0.9), 0 0 30px rgba(0, 0, 0, 0.5);
  line-height: 1.35;
  letter-spacing: 0.02em;
}

.lyric-fade-enter-active {
  transition: opacity 0.6s ease-in, transform 0.6s ease-in;
}

.lyric-fade-leave-active {
  transition: opacity 0.25s ease-out;
}

.lyric-fade-enter-from {
  opacity: 0;
  transform: translateX(-50%) translateY(8px) scale(0.97);
}

.lyric-fade-leave-to {
  opacity: 0;
  transform: translateX(-50%);
}

.caption {
  position: absolute;
  bottom: 3%;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.6);
  color: #fff;
  padding: 0.5rem 1.5rem;
  border-radius: 6px;
  font-size: 1.1rem;
  max-width: 80%;
  text-align: center;
  z-index: 20;
}

.photo-counter {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.8rem;
  font-family: monospace;
  padding: 0.25rem 0.6rem;
  border-radius: 12px;
  z-index: 20;
}

/* --- Navigation Arrows (Slideshow mode) --- */

.nav-arrows {
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  transform: translateY(-50%);
  display: flex;
  justify-content: space-between;
  pointer-events: none;
  padding: 0 0.75rem;
  z-index: 25;
}

.nav-btn {
  pointer-events: auto;
  background: rgba(0, 0, 0, 0.35);
  color: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.15);
  font-size: 2.5rem;
  line-height: 1;
  padding: 0.75rem 1rem;
  cursor: pointer;
  border-radius: 12px;
  transition: background 0.2s, border-color 0.2s;
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
}

.nav-btn:hover:not(:disabled) {
  background: rgba(0, 0, 0, 0.6);
  border-color: rgba(255, 255, 255, 0.3);
}

.nav-btn:disabled {
  opacity: 0.15;
  cursor: default;
}

/* --- Controls Bar --- */

.controls {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 1.5rem 1.5rem 1.25rem;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.75) 60%);
  transition: opacity 0.3s;
  z-index: 30;
}

.controls-hidden {
  opacity: 0;
  pointer-events: none;
}

.mode-switch {
  position: absolute;
  right: 1.5rem;
  display: flex;
  align-items: center;
}

.mode-btn {
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.75);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  padding: 0.45rem 1rem;
  font-size: 0.85rem;
  text-decoration: none;
  letter-spacing: 0.02em;
  transition: background 0.2s, color 0.2s;
}

.mode-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
}

.time-display {
  color: rgba(255, 255, 255, 0.6);
  font-family: monospace;
  font-size: 0.85rem;
  font-variant-numeric: tabular-nums;
}

/* --- Speed Pills --- */

.speed-pills {
  display: flex;
  gap: 0.25rem;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  padding: 0.15rem;
}

.speed-pill {
  background: transparent;
  color: rgba(255, 255, 255, 0.5);
  border: none;
  border-radius: 12px;
  padding: 0.3rem 0.6rem;
  font-size: 0.8rem;
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
  letter-spacing: 0.02em;
}

.speed-pill:hover {
  color: rgba(255, 255, 255, 0.8);
}

.speed-pill-active {
  background: rgba(140, 180, 216, 0.35);
  color: #fff;
}

/* --- Buttons --- */

.btn {
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 8px;
  padding: 0.5rem 1rem;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background 0.2s, border-color 0.2s;
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
}

.btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.3);
}

.btn:disabled {
  opacity: 0.3;
  cursor: default;
}

.btn-play {
  background: rgba(140, 180, 216, 0.25);
  border-color: rgba(140, 180, 216, 0.4);
  border-radius: 24px;
  padding: 0.5rem 1.4rem;
  min-width: 70px;
  text-align: center;
  font-size: 0.95rem;
}

.btn-play:hover {
  background: rgba(140, 180, 216, 0.4) !important;
  border-color: rgba(140, 180, 216, 0.6) !important;
}

/* --- Mobile / iPad --- */

@media (max-width: 768px) {
  .start-title {
    font-size: 2.2rem;
  }
  .start-divider::before,
  .start-divider::after {
    width: 50px;
  }
  .end-title {
    font-size: 2rem;
  }
  .end-name {
    font-size: 2.4rem;
  }
  .lyric-line {
    font-size: 1.3rem;
  }
  .lyrics-overlay {
    bottom: 8%;
  }
  .nav-btn {
    font-size: 1.8rem;
    padding: 0.6rem 0.8rem;
  }
  .controls {
    padding: 1rem 0.75rem 0.75rem;
    gap: 0.5rem;
  }
  .btn-play {
    padding: 0.45rem 1.1rem;
    min-width: 60px;
  }
}

@media (min-width: 769px) and (max-width: 1024px) {
  .lyric-line {
    font-size: 1.8rem;
  }
  .start-title {
    font-size: 2.8rem;
  }
}
</style>