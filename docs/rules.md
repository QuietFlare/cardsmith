# Rules

The non-negotiables of the design that the diagram cannot show. A pull request that breaks one
is reported, never quietly accepted. The compliance rules in compliance/rules.md are separate
and are cited by number.

- Every result line names the model revision and the data version it came from. A score over
  results from another data version is refused, not warned about.
- Every model, baseline or trained, sits behind one interface: passage in, prompt and raw output
  out. Nothing after that point knows which model answered.
- The scorer is plain rules with no model in it. Whether a card says only what the passage says
  is a judgement about meaning and belongs to a separate judge, never folded into the scorer.
- Few-shot examples never come from the eval passages. A row used as an example is left out of
  the eval when the deck is rebuilt.
- Science cards and vocabulary cards are different jobs and are scored separately.
- Everything under data/ is own work or is listed in docs/data-sources.md with source, licence
  and date.
- A rerun of a model overwrites only its own results file. Results of other models stay as they
  were.
- Code meant to run on the phone makes no network calls.
