# Hinge: Designed to be deleted

A 24-second spec motion film for Hinge, built with [HyperFrames](https://github.com/heygen-com/hyperframes). Everything is HTML, CSS and GSAP, rendered to MP4.

**Watch:** [`renders/v3/hinge-designed-to-be-deleted-1080p60-audio.mp4`](renders/v3/hinge-designed-to-be-deleted-1080p60-audio.mp4) (1920×1080, 60fps with motion blur, with sound). Also in `renders/v3/`: a muted MP4, a WebM and a poster. Earlier cuts are in `renders/v2/` and the git history.

> Unofficial concept piece. Not made by or affiliated with Hinge or Match Group. No Hinge logos or assets are used; the wordmark is plain type.

## The film

The idea comes from Hinge's own line: the goal of a dating app is to stop needing it. So the film ends with the app being deleted.

| Bars | Time | Scene | What happens |
| --- | --- | --- | --- |
| 1–3 | 0–6s | **The prompt** | A Hinge-style prompt card. *"I'll fall for you if… you ask a second question."* The heart is tapped on the beat, a comment is typed (*"Ask me one."*), "Send like" shimmers and is pressed, and the profile flies off. The liked heart stays behind and glides into *"Maya is typing"*. |
| 4–6 | 6–12s | **The part in between** | The heart crosses the cut into its slot beside *Like.* Then punchlines land word by word on the beat: *Match. → First date. → Second date. → Meet the friends. → Us.* A split-flap counter ticks from Day 001 to 214, off-beats included. |
| 7 | 12–14s | **Found your person?** | One punchline, then *"Then you know what to do."* streams in. |
| 8–10 | 14–20s | **Delete** | Only the UI: a phone on a demo stage. Press & hold, the icons jiggle, an exit question asks *"Delete Hinge?"*, the answer is *"We met on Hinge"*, then Delete. The icons shuffle over, and the empty slot dithers open on the downbeat of bar 11 into… |
| 11–12 | 20–24s | **End card** | *Designed to be deleted.* word by word, then the Hinge wordmark in liquid metal. |

The full cue list is [BEATSHEET.md](BEATSHEET.md), generated from [`cues.js`](cues.js).

The type uses two voices. Instrument Serif is the human voice (the prompts and the story). Inter is the interface voice (the UI, matching both component libraries below). The palette is paper `#F3EEE7`, ink `#1D1519` and plum `#6D2E62`, with blush `#E7C3D6` on the dark end card.

## Craft: the product-film skill

This cut applies [product-film-skill](https://github.com/Rieranthony/product-film-skill) (a Claude Code skill for showreel-grade product films) to a HyperFrames build. The skill targets Remotion; its craft rules carried over like this:

- **A beat grid, not seconds.** 120 BPM, 12 bars. `cues.js` holds every moment as `b(bar, beat, fraction)`, and scenes read cue names, never literal times. Scene boundaries sit on bars. `node scripts/beatsheet.mjs` regenerates the beat sheet and fails if `index.html`'s slots drift from the cues.
- **Something happens on every beat.** Idle beats got life: the day counter ticks on the off-beats, and the end card's rule draws on beat 4.
- **Punchlines.** At most a few words, and each word lands in 0.3s with a 16px blur and a 36px rise (`cubic-bezier(.22,1,.36,1)`). Every word keeps its slot from the start, so lines never re-center. A card exits with a quick blur just before the next one.
- **Scenes show, punchlines tell.** No captions or chapter labels over the UI. The phone scene is UI only, preceded by its own punchline card.
- **A magic move.** One element carries across scenes: the liked heart leaves the prompt card, becomes the icon of "Maya is typing", then crosses the cut into its slot beside *Like.* It travels on the kit's closed-form spring (stiffness 150, damping 20).
- **Measure, never guess.** Endpoints were measured with a debug probe printed into the frame, and from decoded pixels. The score's grid was checked with the skill's `beats.py`: 120.015 BPM, 1.5ms spread.
- **Quality floor.** No glows, particles, click rings or bouncy easing: touches fade instead of ringing, and pops became springs. Touches rest beside text, never on it. The dither texture thins behind words.
- **Sound on the hit.** Every sound effect is placed from its cue, minus the sound's own peak time, so the transient lands on the frame.
- **Final render.** A 240fps master, blurred 4 subframes to 1 down to 60fps, delivered as muted and with-music H.264, a VP9 WebM and a poster, then checked with the skill's `verify.py` (`scripts/deliver.sh`).

## UI kit

The on-screen UI is built from these sites. Watermelon UI and Beautiful UI have public MIT source, so their components are ported property by property (sizes, colors, shadows, easings, keyframe timings) from source and computed styles, then re-expressed as seekable GSAP. The other tools are closed web apps, so their looks are recreated by hand.

| Site | Used for | How |
| --- | --- | --- |
| [Watermelon UI](https://ui.watermelon.sh) | Prompt card + heart tile, **Send like** shimmer button, split-flap **flip clock**, **iPhone frame**, **dock**, the long-press pop | Ported from [`watermellon-registry`](https://github.com/WatermelonCorp/watermellon-registry): card-swipe card/icon tile, `shimmer-button` (700ms sheen), `flip-clock` (300ms ease-in top flap, 300ms ease-out bottom flap), `device.tsx` SVG (verbatim paths), `dock`, and the dock's k550/c15 click spring solved analytically. Icons are Hugeicons, its icon set. |
| [Beautiful UI](https://beautifului.dev) | Comment **composer**, "Maya is typing" **shimmer**, the **"Delete Hinge?"** exit question, the "Hinge deleted" pill, the streamed line in scene 03 | Ported from [`beautiful-ui`](https://github.com/slev12397/beautiful-ui): `ChatComposer`, `ThinkingState` (1.4s gradient sweep), `ApprovalCard` (fade-up 8px/380ms, radio, resolved pill), `StreamingText` (one word per 55ms). |
| [Ditther](https://ditther.com) | The **dithered iris** out of the deleted app's slot, and the end card's dithered glow | Hand-built Bayer 8×8 ordered dither on a canvas, repainted per frame from time alone. |
| [MetalForge](https://metalforge.xyz) | The **liquid-metal** Hinge app icon and the chrome wordmark | Hand-built with CSS: a chrome gradient ramp plus a traveling specular band. |
| [Tokokino](https://tokokino.com) | Product-demo staging in scene 03: gradient **stage card**, **"Press & hold" / "Tap Delete" callouts**, focus ring, zoom-to-region | Hand-built in the style of a demo editor. |
| [21st.dev](https://21st.dev) | Not used | Its components are served only from its own registry, which wasn't reachable from the build machine, and no public repo mirrors them. |

Small deviations from the sources, all to pass WCAG AA:
- The approval card's Delete button uses the library's own `--red`, darkened from `#E3474C` to `#CF3A40`. The source primary is blue.
- The "Hinge deleted" text is darkened from `#199A4D` to `#137A3C`.
- The card's grey placeholder and counter are darkened from `#9A9DA3` to `#6F7278`. See [CREDITS.md](CREDITS.md) for licenses.

## Inspiration (from [whatships.com](https://whatships.com))

What Ships is an archive of startup launch films posted on X. These are the ones this film borrows from:

| Film | What was borrowed |
| --- | --- |
| [Linear launch film](https://whatships.com/videos/linear-launch-film/) | A 26-second film built on a sequence of single words (*idea, plan, align, focus, ship*). That became the *Like → Match → … → Us.* relay in scene 02. |
| [10s launch video](https://whatships.com/videos/launch-video-10s/) | "Your launch video should probably be 10 seconds or less." So each scene makes exactly one point and the whole thing stays at 20s. |
| [Grok Bot icon in code](https://whatships.com/videos/grok-bot-icon-in-code/) | An app icon animated entirely in code, moving between states. That's the approach for the home screen: jiggle, badge, delete and reflow, all DOM. |
| [Marmarapp Mobile](https://whatships.com/videos/marmarapp-mobile/) | Clean sans type with an italic serif accent word (*"Managing your* allergies"). That became the *person?*, *Second* and *deleted.* treatment. |
| [Apple motion film](https://whatships.com/videos/apple-wonderful-tools/) | Restrained, precise motion on a light field that closes on one line. That's the end card. |
| [HeyGen Hyperframes](https://whatships.com/videos/heygen-hyperframes-6818/) | HyperFrames' own launch is about rhythm. The score is 120 BPM and every word in scene 02 lands on a downbeat. |
| [Candle: Love Letters](https://whatships.com/videos/candle-launches-love-letters-word-game/) · [KnownDating](https://whatships.com/videos/knowndating/) | The dating and couples launches in the archive tell their story through the product's own mechanics. Here that's prompt, like-with-comment, and delete. |

## Project layout

```
cues.js                     the beat sheet as data (bars and beats); the only source of timing
BEATSHEET.md                generated from cues.js
index.html                  host: scene slots on bars, the audio track, the traveler
compositions/prompt.html    bars 1–3 · Watermelon card, Beautiful UI composer + shimmer, the heart's first move
compositions/traveler.html  the heart's move across the cut
compositions/beats.html     bars 4–6 · punchlines + Watermelon flip clock
compositions/found.html     bar 7 · punchline card + StreamingText
compositions/delete.html    bars 8–10 · Watermelon device + dock, ApprovalCard, callouts, dither iris
compositions/endcard.html   bars 11–12 · tagline, metal wordmark, dithered texture
assets/icons.js             Hugeicons glyphs for the home screen and dock
scripts/make_score.py       synthesizes assets/audio/score.mp3 on the cues (numpy, seeded, license-free)
scripts/beatsheet.mjs       prints BEATSHEET.md and checks the slots against the cues
scripts/deliver.sh          240fps master → motion blur → deliverables
scripts/product-film/       beats.py and verify.py from the product-film skill (MIT)
assets/fonts/               Instrument Serif, Inter, Geist Mono (OFL), embedded via @font-face
vendor/gsap.min.js          GSAP 3.14.2, vendored so renders work offline
```

## Run it

Needs Node 22+ and FFmpeg.

```bash
npx hyperframes@0.8.78 preview        # live preview in Studio
npx hyperframes@0.8.78 check          # lint + runtime + layout + contrast
node scripts/beatsheet.mjs > BEATSHEET.md
python3 scripts/make_score.py         # rebuild the score on the cues (needs numpy, node, ffmpeg)
scripts/deliver.sh renders/v3         # 240fps master → 60fps motion blur → deliverables (needs a full ffmpeg)
python3 scripts/product-film/verify.py renders/v3 --duration 24 --bg 243,238,231
```

If Chrome or FFmpeg aren't on your PATH, point HyperFrames at them with `HYPERFRAMES_BROWSER_PATH`, `HYPERFRAMES_FFMPEG_PATH` and `HYPERFRAMES_FFPROBE_PATH`.
