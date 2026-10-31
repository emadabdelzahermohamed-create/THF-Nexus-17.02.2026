'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const pulseDir = path.resolve(__dirname, '../../android/app/src/main/assets/pulse');
const helperPath = path.join(pulseDir, 'workout-local-calendar.js');
const helperSource = fs.readFileSync(helperPath, 'utf8');
const context = {window: {}};
vm.runInNewContext(helperSource, context, {filename: helperPath});
const calendar = context.window.THFWorkoutLocalCalendar;
const localMillis = (year, month, day, hour = 12, minute = 0) => new Date(year, month - 1, day, hour, minute).getTime();

test('local date keys use device-local calendar fields, not UTC day slicing', () => {
  assert.equal(calendar.localDateKey(localMillis(2026, 10, 31, 23, 50)), '2026-10-31');
});

test('a persisted localDate takes precedence over a UTC timestamp after timezone travel', () => {
  const nextLocalDay = new Date(localMillis(2026, 11, 1, 0, 15)).toISOString();
  assert.equal(calendar.historyDateKey({localDate: '2026-10-31', date: nextLocalDay}), '2026-10-31');
});

test('legacy history without localDate falls back to the timestamp in the current local timezone', () => {
  const timestamp = new Date(localMillis(2026, 10, 31, 23, 45)).toISOString();
  assert.equal(calendar.historyDateKey({date: timestamp}), '2026-10-31');
});

test('today summary includes new and legacy sessions on the same local day only', () => {
  const today = localMillis(2026, 10, 31, 23, 30);
  const entries = [
    {localDate: '2026-10-31', date: new Date(today).toISOString()},
    {date: new Date(localMillis(2026, 10, 31, 9)).toISOString()},
    {localDate: '2026-10-30', date: new Date(localMillis(2026, 10, 30, 20)).toISOString()},
    {date: 'not-a-date'}
  ];
  assert.equal(calendar.sessionsForLocalDay(entries, today).length, 2);
});

test('current streak counts today and consecutive prior local dates', () => {
  const entries = ['2026-10-31', '2026-10-30', '2026-10-29'].map(localDate => ({localDate}));
  assert.equal(calendar.currentStreak(entries, localMillis(2026, 10, 31, 14)), 3);
});

test('current streak remains alive through today when the last session was yesterday', () => {
  const entries = [{localDate: '2026-10-30'}, {localDate: '2026-10-29'}];
  assert.equal(calendar.currentStreak(entries, localMillis(2026, 10, 31, 10)), 2);
});

test('a missed full local day breaks the current streak', () => {
  const entries = [{localDate: '2026-10-31'}, {localDate: '2026-10-29'}];
  assert.equal(calendar.currentStreak(entries, localMillis(2026, 10, 31, 18)), 1);
});

test('invalid dates and empty history fail closed', () => {
  assert.equal(calendar.historyDateKey({localDate: '2026-02-30', date: 'bad'}), '');
  assert.equal(calendar.currentStreak([{date: 'bad'}], localMillis(2026, 10, 31)), 0);
  assert.equal(calendar.currentStreak([], localMillis(2026, 10, 31)), 0);
});

test('app persists local calendar keys locally but keeps the native summary payload unchanged', () => {
  const app = fs.readFileSync(path.join(pulseDir, 'app.js'), 'utf8');
  assert.ok(app.includes('const workoutCalendar = window.THFWorkoutLocalCalendar;'));
  assert.ok(app.includes('localDate:workoutCalendar.localDateKey(now)'));
  assert.ok(app.includes('sessionsForLocalDay(entries,Date.now())'));
  assert.ok(app.includes('currentStreak(entries,Date.now())'));
  assert.ok(app.includes('N?.saveSummary?.(JSON.stringify(summary))'));
});

test('the local calendar module loads before app.js in the offline asset page', () => {
  const html = fs.readFileSync(path.join(pulseDir, 'index.html'), 'utf8');
  const helper = html.indexOf('<script src="./workout-local-calendar.js"></script>');
  const app = html.indexOf('<script src="./app.js"></script>');
  assert.ok(helper >= 0 && app > helper);
});
