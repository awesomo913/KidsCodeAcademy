// Deterministic smoke tests for the vendored offline chess rules engine.
import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";
import { fileURLToPath } from "node:url";
import path from "node:path";

const here = path.dirname(fileURLToPath(import.meta.url));
const source = fs.readFileSync(path.join(here, "..", "vendor", "chess-rules.min.js"), "utf8");
const context = {};
vm.runInNewContext(source, context);
const { Chess } = context.ChessRules;

const illegal = new Chess();
assert.throws(
  () => illegal.move({ from: "e2", to: "e5" }),
  /Invalid move/,
  "illegal pawn jump must fail",
);

const mate = new Chess();
for (const move of ["f3", "e5", "g4", "Qh4#"]) assert.ok(mate.move(move));
assert.equal(mate.isCheckmate(), true, "Fool's mate must be checkmate");

const stale = new Chess("7k/5Q2/6K1/8/8/8/8/8 b - - 0 1");
assert.equal(stale.isStalemate(), true, "known stalemate must be detected");

const castle = new Chess("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1");
assert.ok(castle.move({ from: "e1", to: "g1" }), "legal castling must succeed");
assert.equal(castle.get("f1")?.type, "r", "rook must move during castling");

const enPassant = new Chess();
for (const move of ["e4", "a6", "e5", "d5"]) assert.ok(enPassant.move(move));
assert.ok(enPassant.move({ from: "e5", to: "d6" }), "en passant must succeed");
assert.equal(enPassant.get("d5"), undefined, "captured pawn must be removed");

const promote = new Chess("8/P7/8/8/8/8/7p/4K2k w - - 0 1");
assert.ok(promote.move({ from: "a7", to: "a8", promotion: "q" }), "promotion must succeed");
assert.equal(promote.get("a8")?.type, "q", "pawn must promote to a queen");

// Play many legal random games to exercise state transitions without relying
// on UI timing. A fixed generator makes failures reproducible.
let seed = 913;
const random = () => ((seed = (seed * 1664525 + 1013904223) >>> 0) / 2 ** 32);
for (let gameNo = 0; gameNo < 100; gameNo += 1) {
  const game = new Chess();
  for (let ply = 0; ply < 250 && !game.isGameOver(); ply += 1) {
    const moves = game.moves({ verbose: true });
    assert.ok(moves.length > 0);
    assert.ok(game.move(moves[Math.floor(random() * moves.length)]));
  }
}

console.log("chess rules: all deterministic tests passed (100 random games)");
