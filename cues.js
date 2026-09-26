// The beat sheet as data (product-film skill: "cues.ts"). Every moment in the film
// is a bar/beat on the 120 BPM grid; scene code reads names from here, never
// literal seconds. Loaded by index.html (window.CUES) and by Node (globalThis.CUES)
// for the score and the beat sheet (scripts/make_score.py, scripts/beatsheet.mjs).
(function (root) {
  const BPM = 120;
  const BEAT = 60 / BPM; // 0.5 s
  const BEATS_PER_BAR = 4; // a bar is 2 s
  // b(bar, beat, fraction): seconds at a bar and beat. fraction .5 is the "and".
  const b = (bar, beat = 1, fraction = 0) => ((bar - 1) * BEATS_PER_BAR + (beat - 1) + fraction) * BEAT;

  const CUES = {
    bpm: BPM,
    beat: BEAT,
    bars: 12,
    duration: b(13),

    scenes: {
      prompt: { start: b(1), end: b(4), what: "A prompt gets a like" },
      beats: { start: b(4), end: b(7), what: "The relationship, word by word" },
      found: { start: b(7), end: b(8), what: "Found your person? (punchline card)" },
      delete: { start: b(8), end: b(11), what: "Delete the app" },
      endcard: { start: b(11), end: b(13), what: "Designed to be deleted." },
    },

    prompt: {
      profileIn: b(1, 1), // name + card rise
      question: b(1, 2), // "I'll fall for you if"
      heartTile: b(1, 3), // heart tile arrives
      typeAnswer: b(1, 3), // answer types to b(2, 2)
      answerDone: b(2, 2),
      heartTap: b(2, 3), // tap lands on the beat
      composerIn: b(2, 4), // composer + Send like fade up
      typeComment: b(3, 1), // "Ask me one." to b(3, 1, .8)
      sendPress: b(3, 2), // press Send like
      flyAway: b(3, 2, 0.2), // profile leaves; the heart detaches and travels
      statusIn: b(3, 3), // "Maya is typing"
      handoff: b(3, 4, 0.5), // heart leaves for the next scene
    },

    beats: {
      like: b(4, 1), // ♥ Like.          Day 001
      likeMark: b(4, 2), // the traveling heart lands in its slot
      match: b(4, 3), // Match.          Day 002
      tick1: b(4, 4), // the counter keeps going: Day 005
      first: b(5, 1), // First | date.  Day 009
      second: b(5, 3), // Second | date. Day 016
      tick2: b(5, 4), // Day 030
      friends: b(6, 1), // Meet | the | friends.  Day 058, lights out
      us: b(6, 3), // Us.              Day 214
      usHeart: b(6, 4), // heart lands beside "Us."
    },

    found: {
      found: b(7, 1), // Found | your | person?
      stream: b(7, 3), // "Then you know what to do." streams
      cardOut: b(8, 1, -0.2),
    },

    delete: {
      phoneIn: b(8, 1), // stage + phone rise
      sheen: b(8, 2), // metal sheen crosses the icon
      press: b(8, 3), // touch lands, press & hold callout
      editMode: b(8, 4), // jiggle, badges, the pop
      badgeTap: b(9, 1, 0.5), // tap the minus badge; zoom in
      cardIn: b(9, 2), // "Delete Hinge?" fades up
      pick: b(9, 3), // "We met on Hinge"
      toDelete: b(9, 4), // touch moves to Delete, callout
      deleteTap: b(10, 1), // Delete; resolved pill
      vanish: b(10, 2), // the icon goes
      reflow: b(10, 3), // icons slide over
      iris: b(10, 3, 0.5), // dithered iris to b(11, 1)
    },

    endcard: {
      designed: b(11, 1),
      to: b(11, 2),
      be: b(11, 2, 0.5),
      deleted: b(11, 3),
      rule: b(11, 4), // the rule draws
      mark: b(12, 1), // wordmark
      sheen: b(12, 1, 0.25),
    },
  };

  CUES.b = b;
  root.CUES = CUES;
})(typeof window !== "undefined" ? window : globalThis);
