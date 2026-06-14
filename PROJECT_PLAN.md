# Grandma's 90th Birthday Slideshow - Project Plan

## Project Overview

A Vue 3 + Vite web app with two modes:
1. **Live Slideshow** - Plays in the browser with synced audio, photos, and lyrics
2. **Tap-to-Sync Tool** - Built-in tool to time lyrics to the song

Plus a Python script to render the final slideshow as a `.mp4` video file.

### Key Details

- **Song:** "Ninety Years of Liz" (free fishing license reference!)
- **Audio file:** `public/audio/song.mp3` (copied from `C:\Users\smith\Downloads\rhubarb-in-october.mp3`, ~4.6 MB)
- **Photos:** 55 images (mix of JPG + HEIC), batch-converted to `public/photos/photo01.jpg` - `photo55.jpg`
- **Conversion script:** `scripts/convert_photos.py` - re-runnable, converts HEIC and copies JPGs with sequential naming
- **Target playback:** iPad (Safari), potentially AirPlay/cast to venue screen

---

## Assets

### Photos (55 files - converted and ready)

Source: `C:\Users\smith\OneDrive\Desktop\Grandmas 90th`
Output: `public/photos/photo01.jpg` through `photo55.jpg`

Converted using `scripts/convert_photos.py` (re-run anytime to pick up new photos from the source folder). The script:
- Scans the source directory for all JPG, JPEG, HEIC, and HEIF files
- Converts HEIC/HEIF to JPG (quality 95) using `pillow-heif`
- Copies JPGs with quality re-encode (ensures compatibility)
- Outputs sequentially named files: photo01.jpg, photo02.jpg, etc.
- Sorts alphabetically by original filename

Original filenames (in case you need to identify photos later):
AAA247FC-...HEIC, DSC00039.JPG, DSC00491.JPG, DSC00499.JPG, DSC01135.JPG, DSC01148.JPG, DSC01153.JPG, DSCI0112.JPG, DSCI0264.JPG, DSCI0284.JPG, IMG_0038.JPG, IMG_0663.JPG, IMG_0671.JPG, IMG_0673.JPG, IMG_0683.JPG, IMG_0991.JPG, IMG_1452.HEIC, IMG_1583.HEIC, IMG_1584.heic, IMG_1586.HEIC, IMG_2943.JPG, IMG_3315.JPG, IMG_3374.JPG, IMG_3547.JPG, IMG_3739.HEIC, IMG_4046.JPG, IMG_4273.heic, IMG_5659.JPG, IMG_5845.JPG, IMG_5857.heic, IMG_5917.HEIC, IMG_6296.heic, IMG_6424.HEIC, IMG_6653.HEIC, IMG_6684.heic, IMG_7935.HEIC, IMG_7945.HEIC, IMG_8141.HEIC, IMG_8252.HEIC, IMG_8468.HEIC, IMG_8471.HEIC, IMG_8494.HEIC, IMG_8496.HEIC, IMG_8498.HEIC, IMG_8499.HEIC, IMG_8500.HEIC, IMG_8505.heic, IMG_8508.HEIC, IMG_8509.HEIC, IMG_8512.HEIC, IMG_8513.HEIC, IMG_8514.HEIC, PXL_20220404_195708268.jpg, Resized_20251025_094504.jpeg, relay078.jpg

### Audio

- File: `public/audio/song.mp3`
- Size: ~4.6 MB
- Original: `C:\Users\smith\Downloads\rhubarb-in-october.mp3`

### Lyrics

Full lyrics for "Ninety Years of Liz" (provided by creator, may not match Suno output exactly - use the Sync Tool to verify):

```
"Ninety Years of Liz"

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

Final Chorus
Here's to ninety years and a whole lot more,
Still finding reasons to walk through every door.
From the garden rows to the casino lights,
She's still chasing good days and Saturday nights.
Raise a glass and sing because the truth is this:
The world got lucky the day it got Liz.

Tag
Yeah, the world got lucky the day it got Liz.
```

---

## Phase 0: Project Scaffolding & Asset Prep

**Goal:** Vue + Vite project running, photos and audio in place.

- [x] **Convert HEIC photos to JPG** - Done! 55 images converted via `scripts/convert_photos.py`
  - Script uses `pillow-heif` package: `pip install pillow-heif Pillow`
  - Re-run anytime: `python scripts/convert_photos.py` - picks up new files and auto-updates `config.json`
  - **Supports up to 999 photos** (photo001.jpg - photo999.jpg)
  - **Preserves captions**: if you add captions to `config.json`, re-running the script won't overwrite them
- [x] **Copy audio file** - Done! `public/audio/song.mp3` in place
- [x] Scaffold Vue 3 + Vite project
- [x] Install dependencies: `vue-router`, `@vitejs/plugin-vue`
- [x] Create folder structure:
  ```
  grandma-90th-slideshow/
  ├── public/
  │   ├── photos/          # Converted JPGs (photo001.jpg - photo055.jpg, expandable)
  │   └── audio/
  │       └── song.mp3      # "Ninety Years of Liz"
  ├── scripts/
  │   └── convert_photos.py  # HEIC->JPG batch converter + config.json generator
  ├── src/
  │   ├── components/
  │   ├── views/
  │   │   ├── SlideshowView.vue   # Full slideshow with audio/lyrics + slideshow-only mode
  │   │   └── SyncToolView.vue    # Lyrics tap-to-sync tool
  │   ├── router/
  │   │   └── index.js
  │   ├── App.vue
  │   ├── main.js
  │   └── style.css
  ├── config.json          # Auto-generated by convert_photos.py
  ├── lyrics.json          # Created by Sync Tool export
  └── PROJECT_PLAN.md
  ```
- [x] Set up Vue Router with routes: `/` (slideshow), `/sync` (tap-to-sync tool), `/?mode=slideshow` (photos only)
- [x] Create initial `config.json` listing all 55 photos (auto-generated by script)

**Verify:** Run `npm run dev` - `/` shows start screen, `/sync` shows sync tool, photos load from config.json.

### Adding More Photos Later

When people send you more photos:
1. Drop them into `C:\Users\smith\OneDrive\Desktop\Grandmas 90th`
2. Re-run `python scripts/convert_photos.py`
3. The script will: convert all new files, re-number sequentially, update `config.json` (preserving any captions you've added), clean up old numbered files
4. The slideshow automatically reads from `config.json`, so it picks up new photos with no code changes

**Verify:** `npm run dev` loads the app, routes work, photos and audio are accessible in `public/`.

---

## Phase 1: Tap-to-Sync Tool

**Goal:** A working web tool where you can tap along with the song to create timestamped lyrics.

### 1a: Lyrics Input UI
- [x] Create `SyncToolView.vue` with a textarea where you paste lyrics (one line per row)
- [x] Parse lyrics into an array of line objects: `{ id, text, time: null }`
- [x] Skip blank lines and section headers (e.g., "Verse 1", "Chorus", etc.) or mark them as section markers
- [x] Display lyrics as a scrollable list on screen
- [x] Pre-filled with "Ninety Years of Liz" lyrics

**Verify:** Page loads, you can paste the full lyrics of "Ninety Years of Liz", they appear as a list.

### 1b: Audio Playback
- [x] Add an `<audio>` element that loads the song from `public/audio/song.mp3`
- [x] Play/pause controls, current time display, seek bar
- [x] The song "Ninety Years of Liz" should load and play

**Verify:** Audio plays, you can seek and see the current timestamp.

### 1c: Tap-to-Sync Mechanism
- [x] Listen for spacebar keypress during playback
- [x] On each spacebar press, stamp the current audio time onto the **next un-timed** lyric line
- [x] Highlight the current line being synced and dim lines already synced
- [x] Display the recorded timestamp next to each synced line (formatted as mm:ss.ms)
- [x] Allow clicking a line to re-sync it (overwrite its timestamp)
- [x] Allow resetting all timestamps and starting over
- [x] Auto-scroll the lyrics list so the current line stays visible
- [x] Arrow keys seek +/-2 seconds for fine-tuning

**Verify:** Play the song, tap spacebar on each lyric line, see timestamps appear. Re-sync a line by clicking it. This is how you'll verify the Suno output matches the lyrics you gave it.

### 1d: Export/Import lyrics.json
- [x] "Export" button that downloads the synced lyrics as `lyrics.json`
- [x] "Load lyrics.json" button to import an existing one (for re-editing)
- [x] Format: `[ { "time": 3.2, "text": "Well, Liz has got a garden..." }, ... ]`
- [x] Save the exported file into the project root so the slideshow can load it

**Verify:** Sync some lyrics, click Export, verify JSON contents. Reload the file and verify it re-populates the tool.

---

## Phase 2: Slideshow View (Photos Only)

**Goal:** A browser slideshow that displays photos with crossfade transitions, auto-advancing on a timer.

### 2a: Photo Configuration
- [x] Create `config.json` (auto-generated by `scripts/convert_photos.py`)
- [x] Load `config.json` at app startup via fetch
- [x] Blank captions for now - you can fill these in later with descriptions for each photo

**Verify:** Config loads, photos array is accessible in the component.

### 2b: Photo Display & Transitions
- [x] Create `SlideshowView.vue` with a full-screen photo display area
- [x] Show photos from `public/photos/` in order
- [x] CSS crossfade transition between photos (opacity transition)
- [x] Auto-advance by distributing photos evenly across song duration (full mode) or timer (slideshow-only mode)
- [x] Display optional caption at bottom of screen
- [x] Start screen with tap-to-begin (required for browser autoplay policy)

**Verify:** Photos advance with smooth crossfade. Blank captions appear (ready for you to fill in).

### 2c: Playback Controls (Basic)
- [x] Play/Pause button
- [x] Next/Previous buttons
- [x] Keyboard shortcuts: Space (play/pause), Left/Right arrow (prev/next)
- [x] Photo counter (e.g., "5 / 55")
- [x] Auto-hide controls after 3 seconds

**Verify:** You can pause, resume, skip forward/back with buttons and keyboard.

---

## Phase 3: Slideshow View (Full Mode - Photos + Audio + Lyrics)

**Goal:** Integrate audio playback and lyrics display into the slideshow.

### 3a: Audio Integration
- [x] Load the "Ninety Years of Liz" audio from `public/audio/song.mp3`
- [x] When slideshow starts, play audio (after user tap to satisfy autoplay policy)
- [x] Photo transitions driven by **audio time** (photos evenly distributed across the song)
- [x] Play/Pause controls audio AND slideshow together
- [x] When audio ends, slideshow stops

**Verify:** Audio plays, photos transition in sync with the song. Pausing pauses both. The slideshow ends when the song ends.

### 3b: Lyrics Display
- [x] Load `lyrics.json` from `public/lyrics.json` (29 lines, ~3 min)
- [x] Display current lyric line on screen (large Playfair Display font, bottom 10%)
- [x] Highlight/advance lyrics based on audio current time matching timestamps
- [x] Fade-in/fade-out transition for each lyric line (Vue `<transition>`)
- [x] Show next line for context (dimmed, smaller font)

**Verify:** Lyrics appear in time with the audio. They fade in/out smoothly. You can read along.

### 3c: Slideshow-Only Mode
- [x] Query param `?mode=slideshow` plays photos with NO audio and NO lyrics
- [x] Uses simple timer-based auto-advance (from `defaultDuration` in config)
- [x] Good for background display at the party or a continuous photo loop
- [x] Link from Sync Tool page to slideshow-only mode

**Verify:** Navigate to `/?mode=slideshow`, photos advance without audio/lyrics.

---

## Phase 4: Polish & QA

**Goal:** Make it party-ready and iPad-optimized.

### 4a: Styling & Layout
- [ ] Full-screen layout, no scrollbars, black background
- [ ] Photos scale properly with `object-fit: cover` or `contain`
- [ ] Lyrics text: large (~3rem), white, readable from a distance, with text shadow for contrast
- [ ] Song title "Ninety Years of Liz" displayed at the start or as an overlay
- [ ] Responsive - test at various aspect ratios (projector 16:9, iPad 4:3, TV)
- [ ] Auto-hide controls after 3 seconds of inactivity, show on tap/hover

**Verify:** Slideshow looks polished and presentation-ready on iPad and desktop browsers.

### 4b: Touch Controls (iPad)
- [ ] Tap screen to show/hide controls
- [ ] Swipe left/right for next/prev photo
- [ ] Add a "Start" splash screen requiring a tap to begin (satisfies Safari autoplay policy)
- [ ] Test: does the full slideshow play through without interruptions?

**Verify:** Works smoothly on iPad Safari with touch gestures.

### 4c: Hosting
- [ ] Deploy to GitHub Pages, Netlify, or Vercel (free tier)
- [ ] Test on iPad via the public URL
- [ ] The URL will be temporary - take it down after the party if desired
- [ ] Alternatively, serve locally via `npx serve dist` or Python's `http.server`

**Verify:** Slideshow loads and plays correctly from the hosted URL on iPad.

---

## Phase 5: Python Video Renderer (Optional - for offline .mp4)

**Goal:** Render the slideshow as a `.mp4` file for offline playback, AirPlay, or casting.

### 5a: Setup & Dependencies
- [ ] Create `requirements.txt`: `moviepy`, `Pillow`
- [ ] Install FFmpeg: download from https://ffmpeg.org/download.html, add to PATH
- [ ] Verify: `python -c "from moviepy.editor import *; print('OK')"`

**Verify:** moviepy imports successfully, FFmpeg is accessible.

### 5b: Render Photos with Transitions
- [ ] Read `config.json` and `lyrics.json`
- [ ] For each photo: create a clip with the specified duration
- [ ] Add crossfade transitions between clips
- [ ] Concatenate all clips into one video

**Verify:** Run script, get a video of photos with crossfade transitions (no audio, no lyrics yet).

### 5c: Add Background Audio
- [ ] Load `rhubarb-in-october.mp3`
- [ ] Set audio on the video clip, matching duration

**Verify:** Rendered video plays with "Ninety Years of Liz" audio.

### 5d: Add Lyrics Overlay
- [ ] For each lyric line, create a TextClip at the matching timestamp from `lyrics.json`
- [ ] Position text at bottom center, large white font with shadow
- [ ] Apply fade-in/fade-out to each text clip
- [ ] Composite all text clips onto the video

**Verify:** Rendered video shows lyrics timed to the audio, matching the web version.

### 5e: Final Output
- [ ] Render to `.mp4` at 1080p, H.264
- [ ] Output filename: `ninety-years-of-liz.mp4`
- [ ] Test on iPad (via Files app or AirDrop)
- [ ] Test AirPlay to a TV
- [ ] Test from a USB drive on venue equipment

**Verify:** Final `.mp4` plays correctly on iPad and can be AirPlayed/cast at the venue.

---

## Recommended Work Order

1. **Phase 0** - Project scaffolding + copy/convert assets
2. **Phase 1** - Build the Sync Tool (use it to time lyrics as soon as audio is in place)
3. **Phase 2** - Get photos displaying in a slideshow
4. **Phase 3** - Add audio + lyrics integration
5. **Phase 4** - Polish for the party
6. **Phase 5** - Render final video (only if you want an offline .mp4 backup)

Each phase produces something you can see and test immediately. Placeholder data works early on - swap in real assets whenever ready.

---

## Notes

- **HEIC Conversion:** Done! All 55 images (including 23 HEIC files) have been batch-converted to JPG using `scripts/convert_photos.py`. The script is re-runnable if you add more photos to the source folder.
- **Suno Lyrics:** The lyrics above are what you gave to Suno. The actual output may differ slightly. Use the Sync Tool (Phase 1) to verify what was actually generated and note any differences.
- **Photo Order:** Think about the narrative arc - chronological works well for a life story slideshow. You can edit `config.json` to reorder photos and add captions later.
- **Party Date:** June 25th is mentioned in the song ("June twenty-five") - make sure everything is ready before then!