# ADR 0002: The model picks the word

Status: accepted, 2026-10-28

## Context

The design of 28 October asked, as its first step, whether the prompt names the word the
learner tapped in the sentence. With the word named, the model only has to write the card
form and the test measures card quality alone. Without it, part of every miss is the model
choosing a different word than the one the test expected, since many sentences hold two
learnable words.

ADR 0001 settled that the input is a text, pasted or opened, not a sentence with a tap.

## Decision

The prompt carries the text and the card kind. It does not name a word. The model chooses
what in the text is worth a card.

## Consequences

Choosing the word is part of the job and is measured as its own score, selection, apart from
whether the card is right for the word chosen, knowledge. The current baselines already run
this way, so their numbers stand. The test set needs no tapped-word field.
