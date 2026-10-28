# ADR 0001: Cards come from a text the learner gives

Status: accepted, 2026-10-28

## Context

Kartei could ask the model for cards in two ways. Rejected: from a topic name, "networking",
"Spanish grammar", where the model writes 100 cards from what it knows. Chosen: from a text
the learner pastes or opens, where the model writes cards from what the text says.

The baselines of 26 October showed what a model under 1B parameters does when asked for
knowledge it does not have: it invents. Examples taught it the format but could not add
knowledge. A model that size writing 100 cards on networking from nothing would be wrong
often, with no text to check it against.

## Decision

The model writes cards from a text the learner gives it, plus the kind of card wanted. It
never writes cards from a topic alone. Cards from a topic, if Kartei offers them, are a cloud
feature on a large model and are not Cardsmith's job.

## Consequences

The model always has the text in front of it, so the hard part is reading and card form, not
recall. A card can be checked against the text, which is what the scorer and the later judge
do. The test set is texts with the cards wanted from them; today the texts are one sentence
long and grow to paragraphs later. Reading files and cutting text into pieces is Kartei's work.
