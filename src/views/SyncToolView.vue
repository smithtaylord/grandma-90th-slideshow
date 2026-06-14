<template>
  <div class="sync-tool" @keydown="onKeyDown" tabindex="0" ref="rootEl">
    <div class="header">
      <router-link to="/" class="back-link">&larr; Slideshow</router-link>
      <router-link to="/?mode=slideshow" class="back-link">Slideshow Only (no audio)</router-link>
      <h1>Lyric Sync Tool</h1>
      <p class="hint">Press <kbd>Space</kbd> to stamp the current time onto the next unsynced line. Click a line to re-sync it.</p>
    </div>

    <div class="main">
      <div class="lyrics-panel">
        <div v-if="!lyricsLoaded" class="lyrics-input">
          <h2>Paste Lyrics</h2>
          <p>One lyric line per row. Section headers like "Verse 1" or "Chorus" will be preserved as markers (not timed).</p>
          <textarea
            v-model="lyricsText"
            placeholder="Well, Liz has got a garden where the rhubarb grows tall,&#10;She's been making things bloom since we can all recall.&#10;..."
            rows="20"
          ></textarea>
          <div class="actions">
            <button class="btn primary" @click="parseLyrics" :disabled="!lyricsText.trim()">Parse Lyrics</button>
            <button class="btn" @click="triggerLoadJson">Load lyrics.json</button>
            <input type="file" ref="fileInput" accept=".json" @change="onFileLoaded" hidden />
          </div>
        </div>

        <div v-else class="lyrics-lines">
          <div class="lyrics-header-bar">
            <span class="line-count">{{ syncedCount }} / {{ timedLines.length }} synced</span>
            <div class="header-actions">
              <button class="btn small" @click="resetTimestamps">Reset Timestamps</button>
              <button class="btn small" @click="editLyrics">Edit Lyrics Text</button>
              <button class="btn small" @click="triggerLoadJson">Load lyrics.json</button>
            </div>
          </div>
          <div class="lines-scroll" ref="linesContainer">
            <div
              v-for="(line, index) in lines"
              :key="index"
              :class="['line-row', { 'line-marker': line.isMarker, 'line-active': index === activeLineIndex, 'line-synced': line.time !== null && !line.isMarker, 'line-clicked': line.clicked }]"
              @click="onLineClick(index)"
            >
              <span class="line-time" v-if="!line.isMarker">{{ line.time !== null ? formatTime(line.time) : '--:--' }}</span>
              <span class="line-text" v-if="line.isMarker">{{ line.text }}</span>
              <span class="line-text" v-else>{{ line.text }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="audio-panel">
        <h2>Audio</h2>
        <audio
          ref="audioEl"
          src="/audio/song.mp3"
          @timeupdate="onTimeUpdate"
          @loadedmetadata="onAudioLoaded"
          @ended="onAudioEnded"
          @pause="isPlaying = false"
          @play="isPlaying = true"
        ></audio>
        <div class="audio-controls">
          <button class="btn primary" @click="togglePlay">
            {{ isPlaying ? '&#9646;&#9646; Pause' : '&#9654; Play' }}
          </button>
          <span class="time-display">{{ formatTime(currentTime) }} / {{ formatTime(duration) }}</span>
        </div>
        <input
          type="range"
          class="seek-bar"
          min="0"
          :max="duration"
          step="0.1"
          :value="currentTime"
          @input="onSeek"
        />
        <p v-if="!audioReady" class="audio-hint">Audio file must be at <code>public/audio/song.mp3</code></p>
      </div>
    </div>

    <div class="footer" v-if="lyricsLoaded">
      <button class="btn primary large" @click="exportJson">Export lyrics.json</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onMounted, onUnmounted } from 'vue'

const rootEl = ref(null)
const audioEl = ref(null)
const linesContainer = ref(null)
const fileInput = ref(null)

const lyricsText = ref(`"Ninety Years of Liz"

Verse 1
Well, Liz has got a garden where the rhubarb grows tall,
She's been making things bloom since we can all recall.
Got dirt on her boots and sunshine on her face,
She's been spreading love and laughter all over the place.

She spent her working years with scissors in her hand,
Making folks look better all across the land.
And if there's fun to be found, she's always in the mix,
Nobody knows how to live it up quite like Liz.

Chorus
Here's to ninety years and a whole lot more,
Still finding reasons to walk through every door.
From the garden rows to the casino lights,
She's still chasing good days and Saturday nights.
Raise a glass and sing because the truth is this:
The world got lucky the day it got Liz.

Verse 2
Now she's counting down the days to June twenty-five,
Ninety years young and still feeling alive.
Minnesota's got a gift that's finally hers to claim,
A free fishing license with her name on the frame.

So cast that line out on a summer afternoon,
Watch the bobber dance beneath the June moon.
She's got stories to tell and memories to give,
And she's showing us all the right way to live.

Chorus
Here's to ninety years and a whole lot more,
Still finding reasons to walk through every door.
From the garden rows to the casino lights,
She's still chasing good days and Saturday nights.
Raise a glass and sing because the truth is this:
The world got lucky the day it got Liz.

Tag
Yeah, the world got lucky the day it got Liz.`)

const lines = ref([])
const currentTime = ref(0)
const duration = ref(0)
const isPlaying = ref(false)
const audioReady = ref(false)
const clickedLineIndex = ref(null)

const SECTION_MARKERS = ['verse 1', 'verse 2', 'chorus', 'final chorus', 'bridge', 'tag', 'outro', 'intro', 'pre-chorus', 'refrain']

const lyricsLoaded = computed(() => lines.value.length > 0)
const timedLines = computed(() => lines.value.filter(l => !l.isMarker))
const syncedCount = computed(() => timedLines.value.filter(l => l.time !== null).length)
const activeLineIndex = computed(() => {
  if (clickedLineIndex.value !== null) return clickedLineIndex.value
  return lines.value.findIndex(l => !l.isMarker && l.time === null)
})

function isSectionMarker(text) {
  const trimmed = text.trim().toLowerCase()
  return SECTION_MARKERS.some(m => trimmed === m) || /^[a-z]+\s*\d*$/.test(trimmed) && trimmed.length < 20 && !trimmed.includes(',')
}

function parseLyrics() {
  const raw = lyricsText.value.split('\n')
  const parsed = []
  let id = 0
  for (const line of raw) {
    const trimmed = line.trim()
    if (trimmed === '') continue
    if (trimmed.startsWith('"') && trimmed.endsWith('"') && trimmed.length < 60) {
      parsed.push({ id: id++, text: trimmed, isMarker: true, time: null, clicked: false })
      continue
    }
    if (isSectionMarker(trimmed)) {
      parsed.push({ id: id++, text: trimmed, isMarker: true, time: null, clicked: false })
      continue
    }
    parsed.push({ id: id++, text: trimmed, isMarker: false, time: null, clicked: false })
  }
  lines.value = parsed
}

function editLyrics() {
  lines.value = []
}

function resetTimestamps() {
  lines.value.forEach(l => { l.time = null; l.clicked = false })
  clickedLineIndex.value = null
}

function togglePlay() {
  if (!audioEl.value) return
  if (isPlaying.value) {
    audioEl.value.pause()
  } else {
    audioEl.value.play()
  }
}

function onTimeUpdate() {
  if (!audioEl.value) return
  currentTime.value = audioEl.value.currentTime
}

function onAudioLoaded() {
  audioReady.value = true
  duration.value = audioEl.value.duration
}

function onAudioEnded() {
  isPlaying.value = false
}

function onSeek(e) {
  if (!audioEl.value) return
  audioEl.value.currentTime = parseFloat(e.target.value)
  currentTime.value = audioEl.value.currentTime
}

function onKeyDown(e) {
  if (e.code === 'Space' && lyricsLoaded.value) {
    e.preventDefault()
    stampTime()
  }
  if (e.code === 'ArrowLeft' && audioEl.value) {
    e.preventDefault()
    audioEl.value.currentTime = Math.max(0, audioEl.value.currentTime - 2)
  }
  if (e.code === 'ArrowRight' && audioEl.value) {
    e.preventDefault()
    audioEl.value.currentTime = Math.min(duration.value, audioEl.value.currentTime + 2)
  }
}

function stampTime() {
  if (!audioEl.value) return
  const t = audioEl.value.currentTime
  if (clickedLineIndex.value !== null) {
    lines.value[clickedLineIndex.value].time = t
    lines.value[clickedLineIndex.value].clicked = false
    clickedLineIndex.value = null
    return
  }
  const idx = lines.value.findIndex(l => !l.isMarker && l.time === null)
  if (idx === -1) return
  lines.value[idx].time = t
  scrollToLine(idx)
}

function onLineClick(index) {
  const line = lines.value[index]
  if (line.isMarker) return
  clickedLineIndex.value = index
  line.clicked = true
  setTimeout(() => { line.clicked = false }, 300)
}

function scrollToLine(index) {
  nextTick(() => {
    if (!linesContainer.value) return
    const el = linesContainer.value.children[index]
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' })
  })
}

function formatTime(seconds) {
  if (seconds === null || seconds === undefined) return '--:--'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  const ms = Math.floor((seconds % 1) * 10)
  return `${mins}:${secs.toString().padStart(2, '0')}.${ms}`
}

function exportJson() {
  const data = lines.value
    .filter(l => !l.isMarker && l.time !== null)
    .map(l => ({ time: Math.round(l.time * 100) / 100, text: l.text }))
  const json = JSON.stringify(data, null, 2)
  const blob = new Blob([json], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'lyrics.json'
  a.click()
  URL.revokeObjectURL(url)
}

function triggerLoadJson() {
  fileInput.value.click()
}

function onFileLoaded(e) {
  const file = e.target.files[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = (event) => {
    try {
      const data = JSON.parse(event.target.result)
      if (Array.isArray(data) && data.length > 0 && typeof data[0].time === 'number') {
        const parsed = []
        let id = 0
        for (const item of data) {
          parsed.push({ id: id++, text: item.text, isMarker: false, time: item.time, clicked: false })
        }
        lines.value = parsed
      }
    } catch (err) {
      alert('Invalid lyrics.json file')
    }
  }
  reader.readAsText(file)
  e.target.value = ''
}

onMounted(() => {
  if (rootEl.value) rootEl.value.focus()
})

onUnmounted(() => {
  if (audioEl.value) audioEl.value.pause()
})
</script>

<style scoped>
.sync-tool {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #1a1a2e;
  color: #e0e0e0;
  padding: 1rem;
  outline: none;
}

.header {
  text-align: center;
  margin-bottom: 1rem;
  flex-shrink: 0;
}

.header h1 {
  font-family: 'Playfair Display', serif;
  font-size: 1.5rem;
  color: #fff;
  margin-bottom: 0.25rem;
}

.header .hint {
  font-size: 0.85rem;
  color: #888;
}

.header kbd {
  background: #333;
  border: 1px solid #555;
  border-radius: 3px;
  padding: 1px 6px;
  font-size: 0.8rem;
  color: #ccc;
}

.back-link {
  display: inline-block;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
}

.main {
  display: flex;
  gap: 1rem;
  flex: 1;
  min-height: 0;
}

.lyrics-panel {
  flex: 2;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.lyrics-input {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.lyrics-input h2 {
  font-size: 1.1rem;
  color: #fff;
}

.lyrics-input textarea {
  width: 100%;
  min-height: 300px;
  background: #16213e;
  color: #e0e0e0;
  border: 1px solid #333;
  border-radius: 4px;
  padding: 0.75rem;
  font-family: 'Inter', sans-serif;
  font-size: 0.95rem;
  line-height: 1.6;
  resize: vertical;
}

.lyrics-input textarea:focus {
  outline: none;
  border-color: #8cb4d8;
}

.lyrics-lines {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
}

.lyrics-header-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
  flex-shrink: 0;
}

.line-count {
  font-size: 0.85rem;
  color: #888;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
}

.lines-scroll {
  flex: 1;
  overflow-y: auto;
  border: 1px solid #333;
  border-radius: 4px;
  background: #16213e;
  padding: 0.5rem;
}

.line-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.4rem 0.75rem;
  border-radius: 3px;
  cursor: pointer;
  transition: background 0.15s;
}

.line-row:hover {
  background: rgba(140, 180, 216, 0.1);
}

.line-row.line-active {
  background: rgba(140, 180, 216, 0.15);
  border-left: 3px solid #8cb4d8;
}

.line-row.line-synced {
  color: #a0d8a0;
}

.line-row.line-clicked {
  background: rgba(255, 200, 50, 0.2);
}

.line-row.line-marker {
  color: #8cb4d8;
  font-style: italic;
  font-weight: 600;
  padding-top: 0.75rem;
  cursor: default;
}

.line-time {
  font-family: monospace;
  font-size: 0.85rem;
  min-width: 5rem;
  color: #888;
  flex-shrink: 0;
}

.line-row.line-synced .line-time {
  color: #a0d8a0;
}

.line-text {
  font-size: 0.95rem;
  line-height: 1.4;
}

.audio-panel {
  flex: 1;
  background: #16213e;
  border-radius: 4px;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.audio-panel h2 {
  font-size: 1.1rem;
  color: #fff;
}

.audio-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.time-display {
  font-family: monospace;
  font-size: 1.1rem;
  color: #ccc;
}

.seek-bar {
  width: 100%;
  accent-color: #8cb4d8;
}

.audio-hint {
  font-size: 0.8rem;
  color: #666;
}

.audio-hint code {
  background: #222;
  padding: 1px 4px;
  border-radius: 2px;
}

.footer {
  text-align: center;
  padding: 1rem 0 0;
  flex-shrink: 0;
}

.btn {
  background: #333;
  color: #ddd;
  border: 1px solid #555;
  border-radius: 4px;
  padding: 0.4rem 1rem;
  cursor: pointer;
  font-size: 0.85rem;
  transition: background 0.15s;
}

.btn:hover:not(:disabled) {
  background: #444;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn.primary {
  background: #2a628f;
  border-color: #3a82b8;
  color: #fff;
}

.btn.primary:hover:not(:disabled) {
  background: #3a82b8;
}

.btn.small {
  padding: 0.25rem 0.6rem;
  font-size: 0.8rem;
}

.btn.large {
  padding: 0.6rem 2rem;
  font-size: 1rem;
}

.actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.5rem;
}
</style>