# Hinge: Designed to be deleted

A 20-second spec motion film for Hinge, built with [HyperFrames](https://github.com/heygen-com/hyperframes). Everything is HTML, CSS and GSAP, rendered to MP4.

**Watch:** [`renders/hinge-designed-to-be-deleted.mp4`](renders/hinge-designed-to-be-deleted.mp4) (1920×1080, 30fps, with sound)

> Unofficial concept piece. Not made by or affiliated with Hinge or Match Group. No Hinge logos or assets are used; the wordmark is plain type.

## The film

The idea comes from Hinge's own line: the goal of a dating app is to stop needing it. So the film ends with the app being deleted.

| Time | Scene | What happens |
| --- | --- | --- |
| 0–5s | **01 · The prompt** | A Hinge-style prompt card. *"I'll fall for you if… you ask a second question."* The heart gets tapped, a comment is typed (*"Ask me one."*), "Send like" shimmers and gets pressed, and the profile flies off screen. *"Maya is typing…"* |
| 5–11s | **02 · The part in between** | Kinetic type, one word per beat: *Like. → Match. → First date. → Second date. → Meet the friends. → Us.* A split-flap day counter flips from 001 to 214. |
| 11–16.5s | **03 · The goal** | *"Found your person?"* A phone on a demo stage: press & hold, the icons jiggle, and an exit question asks *"Delete Hinge?"*. The answer is *"We met on Hinge"*, then Delete. "Hinge deleted", the icons shuffle over, and the empty slot dithers open into… |
| 16.5–20s | **End card** | *Designed to be deleted.* / Hinge, in liquid metal |

The type uses two voices. Instrument Serif is the human voice (the prompts and the story). Inter is the interface voice (the UI, matching both component libraries below). The palette is paper `#F3EEE7`, ink `#1D1519` and plum `#6D2E62`, with blush `#E7C3D6` on the dark end card.

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

Small deviations from the sources: the approval card's Delete button uses the library's own `--red` token (the source primary is blue), and the "Hinge deleted" text is darkened from `#199A4D` to `#137A3C` to pass WCAG AA. See [CREDITS.md](CREDITS.md) for licenses.

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
index.html                 host: four scene slots + the audio track
compositions/prompt.html   01 · the prompt (Watermelon card, Beautiful UI composer + shimmer)
compositions/beats.html    02 · kinetic type + Watermelon flip clock
compositions/delete.html   03 · Watermelon device + dock, ApprovalCard, callouts, dither iris
compositions/endcard.html  end card
scripts/make_score.py      synthesizes assets/audio/score.mp3 (numpy, seeded, license-free)
assets/fonts/              Instrument Serif, Inter, Geist Mono (OFL), embedded via @font-face
vendor/gsap.min.js         GSAP 3.14.2, vendored so renders work offline
```

## Run it

Needs Node 22+ and FFmpeg.

```bash
npx hyperframes@0.8.78 preview    # live preview in Studio
npx hyperframes@0.8.78 check      # lint + runtime + layout + contrast
npx hyperframes@0.8.78 render -o renders/hinge-designed-to-be-deleted.mp4 --fps 30 --quality delivery
python3 scripts/make_score.py     # rebuild the score (needs numpy)
```

If Chrome or FFmpeg aren't on your PATH, point HyperFrames at them with `HYPERFRAMES_BROWSER_PATH`, `HYPERFRAMES_FFMPEG_PATH` and `HYPERFRAMES_FFPROBE_PATH`.
