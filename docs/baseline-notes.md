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
