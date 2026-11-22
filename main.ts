// news-image-20261121 — the entry program (Node 22, standard library only).
//
// The front page itself is the file entry.png sitting beside this program;
// all this program does is place a copy of it where the grader looks.
// The picture's location is worked out from this file's own URL, so it
// does not matter which directory the program is started from.
//
// Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const folder = dirname(fileURLToPath(import.meta.url));
const picture = join(folder, "entry.png");
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
mkdirSync(outDir, { recursive: true });
copyFileSync(picture, join(outDir, "entry.png"));
console.log("wrote " + join(outDir, "entry.png"));
