# Baseline notes

Date: 26 October 2026. All runs use `scripts/run_eval.py`, greedy decoding, max 200 new tokens, and the same passages from `data/eval/passages.json`:

1. English science, written for this test: mitochondria produce energy, make ATP by oxidative phosphorylation, have their own DNA inherited from the mother.
2. Three German example sentences from my Anki deck (`deutsch/anki-alltag.txt`): "Ich melde mich morgen bei dem Kunden.", "Ich habe mich um die Stelle beworben.", "Das hängt vom Budget ab."

Science cards and vocabulary cards are different jobs. A science card asks about a fact in the passage. A vocabulary card pulls out a phrase and translates it: "sich melden bei (+ Dat.) | to get in touch with". The eval scores them separately.

# Qwen2.5 0.5B Instruct, plain

Model: [Qwen/Qwen2.5-0.5B-Instruct](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct), about 500M weights, Apache 2.0. Run: `qwen`.

Science: three good questions covering all three facts, with answers. But the answers add facts not in the passage (electron transport chain, inner membrane, proton gradient), ignore the `question | answer` format, run to paragraphs, and the last one is cut off at the token limit.

German: sentence 1 split word by word with a wrong translation ("I am reminded"). Sentence 2 translated whole instead of extracting "sich bewerben um (+ Akk.)". Sentence 3 missed the separable verb "abhängen von (+ Dat.)". Two answers start by copying the format line back.

Failure types: outside knowledge (true in biology, not in the passage: faithful and true are different checks), format ignored, format line copied, too long, truncated, whole sentence translated, separable verb missed.

# Qwen2.5 0.5B Instruct, few-shot

Run: `qwen-fewshot`. Before each passage the prompt shows worked examples from `data/prompts/examples.json`: one ribosome passage with three cards, two German sentences with their cards. None of the examples come from `data/eval`, so the test does not leak.

Science: three cards in the right format, card-sized, all three facts, nothing from outside the passage. The third card's question ("What is mitochondrial DNA?") does not match its answer.

German: the format is right, the content is worse. Invented German ("machen mich miteinander"), a Chinese word in the output ("被动", passive), and a repetition loop ("hängen + + + ...") until the token limit.

Failure types: invented words, wrong language (Chinese), repetition loop.

# Qwen3 0.6B, plain

Model: [Qwen/Qwen3-0.6B](https://huggingface.co/Qwen/Qwen3-0.6B), about 600M weights, Apache 2.0. Thinking switched off (`enable_thinking: False`), because cards need the answer only. Run: `qwen3`.

Science: two lines, "question | <first sentence of the passage>" and "answer | <second sentence>". The format words are used as questions and the passage is copied. The DNA fact is missed.

German: sentence 1 copied back unchanged. Sentence 2 translated whole. Sentence 3 gives "Budget" as the phrase to learn and explains it instead of translating.

Failure types: format word as question, passage copied, input copied.

# Qwen3 0.6B, few-shot

Run: `qwen3-fewshot`. Same examples as Qwen2.5 few-shot.

Science: the format line "question | answer" copied, then two passage sentences with no cards at all.

German: "melde mich morgen bei (+ Dat.) | to call on the customer" (conjugated, not the infinitive, wrong meaning). "sich beworben um (+ Akk.) | to apply for the position" (participle instead of "bewerben", meaning right). "budget | to depend on" (wrong phrase, right meaning).

Failure types: conjugated or participle form instead of the infinitive.

# What this means

- Examples teach format and behaviour. They cannot add knowledge the model lacks.
- Newer did not mean better at this size. Qwen3 0.6B was no better than Qwen2.5 0.5B at science, and its German got the meaning right more often but never the dictionary form.
- Science may need only good prompting or light fine-tuning. German needs real training data, so the two subjects are worth treating separately.
- My Anki file pairs 105 example sentences with the cards I made from them. That is a ready test set for the vocabulary job.

# 27 October 2026: 99 cards and EuroLLM

The vocabulary test set is now the Anki deck: 99 sentences, each with the card I wrote for it, in four categories (19 verbs with case, 19 verbs, 28 nouns, 33 connectors and phrases). The prompt asks for dictionary form with article and plural. EuroLLM 1.7B Instruct joins the Qwen models, because it was trained on German from the start. Run: `eurollm`, `eurollm-fewshot`.

A card is correct when the word, the meaning and, for a verb, the case are all right. Reading the outputs found five ways the scorer was fooled, each now pinned by a test: a copied clause around the right word, a right meaning on the wrong word, the right verb with the wrong case, a conjugated form, and an invented case note on a noun.

Without examples no model writes a card at all. With two examples: EuroLLM 7 of 99 correct, Qwen3 0.6B 6, Qwen2.5 0.5B 1.

# 28 October 2026: the score split in two

One number hid two failures. Selection: did the model pick the word I made a card for. Knowledge: of those, how many cards were fully right. Both are in `scripts/score.py`, overall and per category.

Selection is the bigger wall. The best model picks my word in 25 of 99 sentences (Qwen3), EuroLLM in 19. Phrases are worst, 3 or 4 of 33 for every model. Nouns are where Qwen3 is ahead, 11 of 28 picked and 4 of those right.

Knowledge, once the word is picked: EuroLLM 7 of 19, Qwen3 6 of 25, Qwen2.5 1 of 20. EuroLLM is the only model that gets a verb with its case right, 3 of 8. Qwen3 gets 0 of 6.

A limit of the split: selection asks for the head word in dictionary form, so a model that picked the right verb and wrote it conjugated counts as not selected. Part of the selection wall is form, not choice. Telling those two apart needs a lemmatiser in the scorer, which is the same piece the dictionary lookup needs.
