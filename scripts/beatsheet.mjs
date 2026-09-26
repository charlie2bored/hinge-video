// Prints the beat sheet from cues.js as Markdown and checks that index.html's
// scene slots sit on the same bars. Usage: node scripts/beatsheet.mjs > BEATSHEET.md
import { readFileSync } from "node:fs";

await import("../cues.js"); // sets globalThis.CUES (the package is ESM, so no module.exports)
const CUES = globalThis.CUES;

const barBeat = (t) => {
  const beats = t / CUES.beat;
  const bar = Math.floor(beats / 4) + 1;
  const beat = beats - (bar - 1) * 4 + 1;
  const whole = Math.floor(beat + 1e-9), rest = beat - whole;
  return rest < 1e-9 ? `${bar}.${whole}` : `${bar}.${whole} +${rest.toFixed(2)}`;
};

// index.html must mount each scene exactly on its bars.
const html = readFileSync(new URL("../index.html", import.meta.url), "utf8");
for (const [id, scene] of Object.entries(CUES.scenes)) {
  const slot = html.match(new RegExp(`data-composition-id="${id}"[^>]*?data-start="([\\d.]+)"[^>]*?data-duration="([\\d.]+)"`, "s"));
  if (!slot) throw new Error(`no slot for ${id} in index.html`);
  const [start, duration] = [Number(slot[1]), Number(slot[2])];
  if (start !== scene.start || duration !== scene.end - scene.start) {
    throw new Error(`${id}: index.html says ${start}+${duration}, cues say ${scene.start}+${scene.end - scene.start}`);
  }
}

const lines = [
  "# Beat sheet",
  "",
  `${CUES.bpm} BPM, 4/4, a beat is ${CUES.beat}s and a bar ${CUES.beat * 4}s. ${CUES.bars} bars, ${CUES.duration}s.`,
  "Generated from `cues.js` by `node scripts/beatsheet.mjs > BEATSHEET.md`.",
  "",
];
for (const [id, scene] of Object.entries(CUES.scenes)) {
  lines.push(`## ${id} · bars ${barBeat(scene.start).split(".")[0]}–${Number(barBeat(scene.end).split(".")[0]) - 1} · ${scene.start}–${scene.end}s`, "", scene.what, "");
  lines.push("| cue | bar.beat | seconds |", "| --- | --- | --- |");
  for (const [name, t] of Object.entries(CUES[id])) lines.push(`| ${name} | ${barBeat(t)} | ${t} |`);
  lines.push("");
}
console.log(lines.join("\n"));
