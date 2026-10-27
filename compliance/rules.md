# Compliance rules

Numbered so a review can cite them. Not legal advice.

1. Intended purpose is self-study. Nothing here grades students for a school or employer, or decides admission (EU AI Act, high-risk education uses).
2. No personal data in data/ or any training set. My own Anki deck is fine. Other people's notes, names, emails or chat logs are not (GDPR).
3. Every data file is named in docs/data-sources.md with source URL, licence, date and what was taken.
4. A dataset keeps its sources' licence terms. CC BY-SA sources make it CC BY-SA, and non-commercial sources stay out of data meant for release.
5. No text from commercial textbooks in the repo.
6. Anything the model writes is labelled as generated, never presented as written by a person (EU AI Act, transparency).
7. MODEL_CARD.md changes in the same pull request as the model, its training data or its eval. It covers intended use, out-of-scope uses, languages, eval results and known failures.
8. Every eval result names the model version and data version it came from.
9. Code meant to run on the phone makes no network calls.
10. Synthetic training data from another model records which model wrote it, and that model's terms must allow training other models on its output.
11. No API keys, tokens or secrets committed.
