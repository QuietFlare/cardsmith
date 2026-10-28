# ADR 0003: The model is a separate download

Status: accepted, 2026-10-28

## Context

A 0.6B model at 4-bit is about 400 MB, a 1.7B model about 1 GB. Inside the app bundle that
makes Kartei a 1 GB install for every learner, including those who never use offline cards,
and freezes the model to the app's release cycle.

## Decision

The model ships as a file the learner downloads on demand, once, from inside Kartei. It is
not part of the app bundle. Target under 500 MB, hard limit 1 GB. A new model replaces the
file without an app update.

## Consequences

Kartei installs small. Offline cards cost a download only for those who want them, like an
offline language pack, and the file can be deleted. Which model is best is decided in this
repo's harness, and swapping it is one eval run and one file. The download is the one
network call Kartei makes for Cardsmith, and it carries no learner data.
