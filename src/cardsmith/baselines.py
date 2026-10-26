"""Baseline models behind one interface: give a passage, get back the prompt and the raw output."""
import json
from pathlib import Path

from huggingface_hub import try_to_load_from_cache
from transformers import AutoModelForCausalLM, AutoTokenizer

# Plain-words instructions for models that follow them, one per kind of card.
PROMPTS = {
    "qa": (
        "Write flash cards from this text. Use only facts that are in the text. "
        "One card per line, as: question | answer\n\nText: "
    ),
    "vocab": (
        "This is a German example sentence. Find the verb phrase a learner should "
        "memorise, with its preposition and case, and translate it to English. "
        "Answer with one line, as: German phrase | English meaning\n\nSentence: "
    ),
}


def revision(model_id):
    """The commit of the model files in the local cache, so a result names its exact model."""
    path = try_to_load_from_cache(model_id, "config.json")
    return Path(path).parent.name if isinstance(path, str) else "unknown"


def load_examples():
    """Worked examples for few-shot prompts. Never taken from data/eval: that would leak the test."""
    path = Path(__file__).resolve().parents[2] / "data" / "prompts" / "examples.json"
    return json.loads(path.read_text(encoding="utf-8"))


class ChatModel:
    """A general instruct model, asked in plain words through its chat template.

    With examples, each one goes in first as an earlier question and answer, so the
    model sees the format done right before it gets the real passage (few-shot).
    """

    def __init__(self, model_id, examples=None, template_options=None):
        self.model_id = model_id
        self.examples = examples or {}
        # Extra switches some chat templates take, e.g. Qwen3's enable_thinking.
        self.template_options = template_options or {}
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.model = AutoModelForCausalLM.from_pretrained(model_id)
        self.revision = revision(model_id)

    def ask(self, passage):
        task = PROMPTS[passage["kind"]]
        messages = []
        for example in self.examples.get(passage["kind"], []):
            messages.append({"role": "user", "content": task + example["text"]})
            messages.append({"role": "assistant", "content": example["cards"]})
        messages.append({"role": "user", "content": task + passage["text"]})
        text = self.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True, **self.template_options
        )
        inputs = self.tokenizer(text, return_tensors="pt")
        output = self.model.generate(**inputs, max_new_tokens=200, do_sample=False)
        new_tokens = output[0][inputs["input_ids"].shape[1]:]
        # The prompt saved is the full text the model saw, chat markers and examples included.
        return text, self.tokenizer.decode(new_tokens, skip_special_tokens=True).strip()


# The names the run script accepts. A new model is one more line here.
MODELS = {
    "qwen": lambda: ChatModel("Qwen/Qwen2.5-0.5B-Instruct"),
    "qwen-fewshot": lambda: ChatModel("Qwen/Qwen2.5-0.5B-Instruct", load_examples()),
    # Qwen3 thinks out loud before answering unless told not to; cards need the answer only.
    "qwen3": lambda: ChatModel("Qwen/Qwen3-0.6B", template_options={"enable_thinking": False}),
    "qwen3-fewshot": lambda: ChatModel(
        "Qwen/Qwen3-0.6B", load_examples(), template_options={"enable_thinking": False}
    ),
}
