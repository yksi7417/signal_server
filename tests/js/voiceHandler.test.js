import test from 'node:test';
import assert from 'node:assert/strict';
import { parseTile } from '../../static/game/js/voiceParser.js';

test('parse numeric tile', () => {
  assert.equal(parseTile('five bamboo'), '\u{1F014}');
});

test('parse dragon tile', () => {
  assert.equal(parseTile('red dragon'), '\u{1F004}');
});

test('parse wind tile', () => {
  assert.equal(parseTile('north wind'), '\u{1F003}');
});

test('return null on unknown', () => {
  assert.equal(parseTile('not a tile'), null);
});
