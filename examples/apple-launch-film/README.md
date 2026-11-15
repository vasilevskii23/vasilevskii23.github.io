# Aura — example Apple-style launch film

Demo built with the `apple-launch-film` + `apple-design` agent skills.

**Product:** Aura  
**Line:** Clarity for every conversation.

## Preview

Open `index.html` in a browser, or:

```bash
cd examples/apple-launch-film
npm run preview
```

Spacebar pauses/resumes. Call `window.seek(seconds)` from the console to jump to any frame.

## Render MP4

```bash
cd examples/apple-launch-film
npm install
npm run render
```

Writes `aura-launch.mp4` (1920×1080, 30fps, ~17.5s).
