<template>
  <div class="reorder">
    <div class="header">
      <h1>Arrange Photos</h1>
      <p class="hint">
        Drag photos to reorder. Drag into the "Excluded" bin to leave them out of
        the music slideshow (they'll still play in Photos-Only mode).
      </p>
      <div class="actions">
        <router-link to="/" class="btn">&larr; Back to Slideshow</router-link>
        <router-link to="/?mode=slideshow" class="btn">Photos Only</router-link>
        <button class="btn primary" @click="downloadConfig">Download config.json</button>
        <button class="btn" @click="resetOrder">Reset Order</button>
      </div>
    </div>

    <div v-if="loaded" class="lists">
      <details class="lyrics-panel" v-if="lyrics.length">
        <summary>
          Lyrics timeline &amp; photo pairing
          <span class="panel-sub">{{ lyrics.length }} lines</span>
        </summary>
        <p class="panel-hint" v-if="audioLoading">Loading song duration…</p>
        <p class="panel-hint" v-else>
          Each lyric maps to the photo on screen at that moment
          ({{ musicPhotos.length }} photos across {{ formatTime(songDuration) }}).
          Reorder to change pairings.
        </p>
        <ol class="lyrics-timeline">
          <li v-for="(line, i) in lyricPhotoMap" :key="i">
            <span class="lyric-time">{{ formatTime(line.time) }}</span>
            <span class="lyric-text">{{ line.text }}</span>
            <span class="lyric-photo">&rarr; photo {{ line.photoIndex + 1 }}</span>
          </li>
        </ol>
      </details>

      <!-- Music slideshow list -->
      <section class="list-section">
        <div class="list-header">
          <h2>In Music Slideshow</h2>
          <span :class="['count-badge', countBadgeClass]">
            {{ musicPhotos.length }} photos
            <span class="count-target" v-if="!inTargetRange">
              (target 55–60)
            </span>
          </span>
        </div>
        <div
          class="photo-grid drop-zone"
          :class="{ 'drop-zone-active': dragSource && dragSource !== 'music' }"
          @dragover.prevent
          @drop.prevent="onDropOnList('music')"
        >
          <div
            v-for="(photo, index) in musicPhotos"
            :key="photo.file"
            :class="['photo-card', { 'drag-over': dragOverKey === `music-${index}` }]"
            draggable="true"
            @dragstart="onDragStart('music', index, $event)"
            @dragenter.prevent="onDragEnter('music', index)"
            @drop.prevent="onDrop"
            @dragend="onDragEnd"
          >
            <div class="photo-number">{{ index + 1 }}</div>
            <button class="card-toggle" @click="toggleOne('music', index)" title="Exclude from music slideshow">
              &#8595; exclude
            </button>
            <div class="img-wrapper">
              <img :src="`/photos/${photo.file}`" :alt="`Photo ${index + 1}`" loading="lazy" draggable="false" />
            </div>
            <div class="card-lyric" :title="photoLyricMap[index] || ''">
              {{ photoLyricMap[index] || (audioLoading ? '…' : 'no lyric') }}
            </div>
            <div class="photo-label">{{ photo.file }}</div>
          </div>
          <div v-if="musicPhotos.length === 0" class="empty-hint">
            Drag photos here to include them in the music slideshow
          </div>
        </div>
      </section>

      <!-- Excluded bin -->
      <section class="list-section excluded-section">
        <div class="list-header">
          <h2>Excluded from Music <span class="bin-icon">&#128465;</span></h2>
          <span class="count-badge muted">{{ excludedPhotos.length }} photos</span>
        </div>
        <p class="bin-subhint">These play in Photos-Only mode, after the music set.</p>
        <div
          class="photo-grid drop-zone"
          :class="{ 'drop-zone-active': dragSource && dragSource !== 'excluded' }"
          @dragover.prevent
          @drop.prevent="onDropOnList('excluded')"
        >
          <div
            v-for="(photo, index) in excludedPhotos"
            :key="photo.file"
            :class="['photo-card', { 'drag-over': dragOverKey === `excluded-${index}` }]"
            draggable="true"
            @dragstart="onDragStart('excluded', index, $event)"
            @dragenter.prevent="onDragEnter('excluded', index)"
            @drop.prevent="onDrop"
            @dragend="onDragEnd"
          >
            <div class="photo-number">{{ index + 1 }}</div>
            <button class="card-toggle include" @click="toggleOne('excluded', index)" title="Include in music slideshow">
              &#8593; include
            </button>
            <div class="img-wrapper">
              <img :src="`/photos/${photo.file}`" :alt="`Photo ${index + 1}`" loading="lazy" draggable="false" />
            </div>
            <div class="photo-label">{{ photo.file }}</div>
          </div>
          <div v-if="excludedPhotos.length === 0" class="empty-hint">
            Drag photos here to exclude them from the music slideshow
          </div>
        </div>
      </section>
    </div>

    <div v-else class="loading">
      <p>Loading photos...</p>
    </div>

    <div class="footer" v-if="loaded">
      <p class="footer-hint">
        Download config.json, then place it in <code>public/config.json</code> and
        redeploy to persist your changes.
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const musicPhotos = ref([])
const excludedPhotos = ref([])
const loaded = ref(false)
const dragSource = ref(null)
const dragIndex = ref(null)
const dragOverKey = ref(null)

const lyrics = ref([])
const songDuration = ref(0)
const audioLoading = ref(true)

const TARGET_MIN = 55
const TARGET_MAX = 60

const inTargetRange = computed(() =>
  musicPhotos.value.length >= TARGET_MIN && musicPhotos.value.length <= TARGET_MAX
)

const countBadgeClass = computed(() => {
  const n = musicPhotos.value.length
  if (n >= TARGET_MIN && n <= TARGET_MAX) return 'good'
  if (n < TARGET_MIN) return 'low'
  return 'high'
})

const photoLyricMap = computed(() => {
  const N = musicPhotos.value.length
  const dur = songDuration.value
  if (!N || !dur || !lyrics.value.length) return []
  const out = new Array(N)
  for (let i = 0; i < N; i++) {
    const mid = ((i + 0.5) / N) * dur
    let text = null
    for (let j = lyrics.value.length - 1; j >= 0; j--) {
      if (lyrics.value[j].time <= mid) { text = lyrics.value[j].text; break }
    }
    out[i] = text
  }
  return out
})

const lyricPhotoMap = computed(() => {
  const N = musicPhotos.value.length
  const dur = songDuration.value
  if (!N || !dur || !lyrics.value.length) return []
  const per = dur / N
  return lyrics.value.map(l => ({
    time: l.time,
    text: l.text,
    photoIndex: Math.min(Math.max(0, Math.floor(l.time / per)), N - 1),
  }))
})

function getListRef(list) {
  return list === 'music' ? musicPhotos : excludedPhotos
}

async function loadConfig() {
  try {
    const res = await fetch('/config.json')
    const config = await res.json()
    const photos = config.photos || []
    musicPhotos.value = photos.filter(p => !p.excludedFromMusic).map(p => ({ ...p }))
    excludedPhotos.value = photos.filter(p => p.excludedFromMusic).map(p => ({ ...p }))
  } catch (e) {
    console.error('Failed to load config', e)
  } finally {
    loaded.value = true
  }
}

async function loadLyrics() {
  try {
    const res = await fetch('/lyrics.json')
    lyrics.value = await res.json()
  } catch (e) {
    console.error('Failed to load lyrics.json', e)
  }
}

function loadSongDuration() {
  const audio = new Audio('/audio/song.mp3')
  audio.preload = 'metadata'
  audio.addEventListener('loadedmetadata', () => {
    if (audio.duration && isFinite(audio.duration)) {
      songDuration.value = audio.duration
      audioLoading.value = false
    }
  })
  audio.addEventListener('error', fallbackDuration)
  setTimeout(() => {
    if (audioLoading.value) fallbackDuration()
  }, 4000)
}

function fallbackDuration() {
  if (!audioLoading.value) return
  songDuration.value = lyrics.value.length
    ? lyrics.value[lyrics.value.length - 1].time + 5
    : 190
  audioLoading.value = false
}

function formatTime(seconds) {
  if (!seconds || isNaN(seconds)) return '0:00'
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  return `${m}:${s.toString().padStart(2, '0')}`
}

function onDragStart(list, index, e) {
  dragSource.value = list
  dragIndex.value = index
  e.dataTransfer.effectAllowed = 'move'
  e.dataTransfer.setData('text/plain', '')
}

function onDragEnter(list, index) {
  if (dragSource.value === null) return
  dragOverKey.value = `${list}-${index}`

  if (dragSource.value === list) {
    if (dragIndex.value === index) return
    const arr = getListRef(list).value
    const item = arr.splice(dragIndex.value, 1)[0]
    arr.splice(index, 0, item)
    dragIndex.value = index
  } else {
    const fromArr = getListRef(dragSource.value).value
    const toArr = getListRef(list).value
    const item = fromArr.splice(dragIndex.value, 1)[0]
    toArr.splice(index, 0, item)
    dragSource.value = list
    dragIndex.value = index
  }
}

function onDropOnList(list) {
  if (dragSource.value === null) {
    dragOverKey.value = null
    return
  }
  if (dragSource.value !== list) {
    const fromArr = getListRef(dragSource.value).value
    const toArr = getListRef(list).value
    const item = fromArr.splice(dragIndex.value, 1)[0]
    toArr.push(item)
  }
  dragSource.value = null
  dragIndex.value = null
  dragOverKey.value = null
}

function onDrop() {
  dragSource.value = null
  dragIndex.value = null
  dragOverKey.value = null
}

function onDragEnd() {
  dragSource.value = null
  dragIndex.value = null
  dragOverKey.value = null
}

function toggleOne(list, index) {
  const fromArr = getListRef(list).value
  const item = fromArr.splice(index, 1)[0]
  if (list === 'music') {
    excludedPhotos.value.push(item)
  } else {
    musicPhotos.value.push(item)
  }
}

function resetOrder() {
  const all = [...musicPhotos.value, ...excludedPhotos.value]
  all.sort((a, b) => a.file.localeCompare(b.file))
  all.forEach(p => { p.excludedFromMusic = false })
  musicPhotos.value = all
  excludedPhotos.value = []
}

function downloadConfig() {
  const photos = [
    ...musicPhotos.value.map(p => ({ ...p, excludedFromMusic: false })),
    ...excludedPhotos.value.map(p => ({ ...p, excludedFromMusic: true })),
  ]
  const config = {
    songTitle: 'Ninety Years of Liz',
    defaultDuration: 5,
    transitionDuration: 1,
    transitionStyle: 'crossfade',
    photos,
  }
  const json = JSON.stringify(config, null, 2)
  const blob = new Blob([json], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'config.json'
  a.click()
  URL.revokeObjectURL(url)
}

onMounted(() => {
  loadConfig()
  loadLyrics()
  loadSongDuration()
})
</script>

<style scoped>
.reorder {
  height: 100vh;
  overflow-y: auto;
  background: #0d1117;
  color: #e0e0e0;
  padding: 1.5rem;
  font-family: 'Inter', sans-serif;
}

.header {
  text-align: center;
  margin-bottom: 1.5rem;
}

.header h1 {
  font-family: 'Playfair Display', serif;
  font-size: 1.8rem;
  color: #fff;
  margin-bottom: 0.25rem;
}

.hint {
  color: #888;
  font-size: 0.85rem;
  margin-bottom: 1rem;
  max-width: 640px;
  margin-left: auto;
  margin-right: auto;
}

.actions {
  display: flex;
  gap: 0.5rem;
  justify-content: center;
  flex-wrap: wrap;
}

.lists {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.list-section {
  background: #11161d;
  border: 1px solid #21262d;
  border-radius: 12px;
  padding: 1rem;
}

.excluded-section {
  background: #141011;
  border-color: #2a2122;
}

.list-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.list-header h2 {
  font-family: 'Playfair Display', serif;
  font-size: 1.15rem;
  color: #fff;
  margin: 0;
}

.bin-icon {
  font-size: 1rem;
  opacity: 0.6;
}

.bin-subhint {
  color: #777;
  font-size: 0.78rem;
  margin: 0 0 0.75rem;
}

.count-badge {
  font-size: 0.8rem;
  padding: 0.2rem 0.7rem;
  border-radius: 12px;
  font-weight: 600;
  border: 1px solid transparent;
}

.count-badge.good {
  background: rgba(63, 185, 113, 0.15);
  color: #3fb971;
  border-color: rgba(63, 185, 113, 0.35);
}

.count-badge.low {
  background: rgba(212, 167, 44, 0.15);
  color: #d4a72c;
  border-color: rgba(212, 167, 44, 0.35);
}

.count-badge.high {
  background: rgba(212, 87, 87, 0.15);
  color: #d45757;
  border-color: rgba(212, 87, 87, 0.35);
}

.count-badge.muted {
  background: rgba(255, 255, 255, 0.05);
  color: #888;
  border-color: #30363d;
}

.count-target {
  font-weight: 400;
  opacity: 0.8;
}

.photo-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 0.75rem;
}

.drop-zone {
  min-height: 120px;
  border-radius: 8px;
  transition: background 0.15s, outline 0.15s;
}

.drop-zone-active {
  outline: 2px dashed #8cb4d8;
  outline-offset: 4px;
  background: rgba(140, 180, 216, 0.04);
}

.photo-card {
  background: #161b22;
  border: 2px solid #30363d;
  border-radius: 8px;
  overflow: hidden;
  cursor: grab;
  transition: transform 0.2s, border-color 0.15s, box-shadow 0.15s;
  position: relative;
}

.photo-card:hover {
  border-color: #58647a;
}

.photo-card:active {
  cursor: grabbing;
}

.photo-card.drag-over {
  border-color: #8cb4d8;
  transform: scale(1.04);
  box-shadow: 0 0 12px rgba(140, 180, 216, 0.3);
}

.photo-number {
  position: absolute;
  top: 0.4rem;
  left: 0.4rem;
  background: rgba(0, 0, 0, 0.75);
  color: #fff;
  font-size: 0.7rem;
  font-weight: 600;
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
  z-index: 2;
  pointer-events: none;
}

.card-toggle {
  position: absolute;
  top: 0.4rem;
  right: 0.4rem;
  background: rgba(0, 0, 0, 0.75);
  color: #ccc;
  border: 1px solid rgba(255, 255, 255, 0.15);
  font-size: 0.65rem;
  padding: 0.15rem 0.4rem;
  border-radius: 4px;
  cursor: pointer;
  z-index: 3;
  transition: background 0.15s;
}

.card-toggle:hover {
  background: rgba(140, 180, 216, 0.4);
  color: #fff;
}

.card-toggle.include:hover {
  background: rgba(63, 185, 113, 0.4);
}

.img-wrapper {
  width: 100%;
  height: 150px;
  overflow: hidden;
}

.img-wrapper img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  pointer-events: none;
}

.photo-label {
  padding: 0.35rem 0.5rem;
  font-size: 0.7rem;
  color: #666;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.empty-hint {
  grid-column: 1 / -1;
  text-align: center;
  padding: 2rem;
  color: #555;
  font-size: 0.85rem;
  border: 1px dashed #30363d;
  border-radius: 8px;
}

.footer {
  text-align: center;
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid #30363d;
}

.footer-hint {
  color: #888;
  font-size: 0.8rem;
}

.footer-hint code {
  background: #21262d;
  padding: 0.1rem 0.3rem;
  border-radius: 3px;
  font-size: 0.8rem;
}

.loading {
  text-align: center;
  padding: 4rem;
  color: #888;
}

.btn {
  background: #21262d;
  color: #ccc;
  border: 1px solid #30363d;
  border-radius: 6px;
  padding: 0.45rem 0.9rem;
  cursor: pointer;
  font-size: 0.85rem;
  text-decoration: none;
  transition: background 0.2s;
}

.btn:hover {
  background: #30363d;
}

.btn.primary {
  background: #2a628f;
  border-color: #3a82b8;
  color: #fff;
}

.btn.primary:hover {
  background: #3a82b8;
}

@media (max-width: 600px) {
  .photo-grid {
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: 0.5rem;
  }
  .img-wrapper {
    height: 120px;
  }
  .header h1 {
    font-size: 1.4rem;
  }
}
</style>
