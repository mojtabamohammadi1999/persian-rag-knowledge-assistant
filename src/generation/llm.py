import os

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

DEFAULT_LLM = os.getenv("LLM_MODEL", "Qwen/Qwen2.5-7B-Instruct")


class LocalLLM:
    def __init__(self, model_name=DEFAULT_LLM, model=None, tokenizer=None):
        self.tokenizer = tokenizer if tokenizer is not None else AutoTokenizer.from_pretrained(model_name)
        self.model = model if model is not None else self._load_4bit(model_name)

    @staticmethod
    def _load_4bit(model_name):
        quant_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
        )
        return AutoModelForCausalLM.from_pretrained(
            model_name, quantization_config=quant_config, device_map="auto"
        )

    def generate(self, messages, max_new_tokens=500):
        text = self.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)
        with torch.no_grad():
            output_ids = self.model.generate(
                **inputs, max_new_tokens=max_new_tokens, do_sample=False
            )
        new_tokens = output_ids[0][inputs["input_ids"].shape[1]:]
        return self.tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
