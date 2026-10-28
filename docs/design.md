# Cardsmith

## Goal

A small model running offline on the phone, inside Kartei, takes a plain text the learner
gives it and a request such as "vocabulary", "grammar" or "formulas", and writes the flash
cards of that kind worth learning from the text. Vocabulary cards carry the word in dictionary
form with case, article and plural. Grammar, fact and formula cards say only what the text says.
Reading files, cutting text into pieces and everything about the learner stay in Kartei.

## Constraints

- Offline. No server, no account, no network permission.
- Works on phones without the vendors' on-device AI. The test phone is a Pixel 8a with 8 GB RAM.
- The model is a separate download, not part of the app: under 500 MB wanted, 1 GB at most.
- Every model, dataset and teacher output must allow training and publishing. Repo, dataset
  and model will be public.
- The model sees plain text only, a few paragraphs at a time.
- A piece of text becomes cards within the time a learner will wait: under 10 seconds per
  piece on the Pixel 8a, inside the memory the phone leaves an app. Provisional until the
  first run on a phone; every result records seconds per passage and peak memory.
- German vocabulary first, then English facts from a passage. Other card kinds come one at a
  time, each with its own test set.

Decisions are in adr/, one file each, dated and numbered. The rules the code must keep are in
rules.md. What was measured and when is in baseline-notes.md.
