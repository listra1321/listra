import json
import random

class ExampleMemory:

    def __init__(self, path):
        self.data = []

        with open(path, 'r') as f:
            for line in f:
                if line.strip():  # hindari baris kosong
                    self.data.append(json.loads(line))

    def get_examples(self, k=2):
        return random.sample(self.data, min(k, len(self.data)))

    def format_examples(self, examples):
        formatted = ""
        for ex in examples:
            formatted += f"""
INPUT:
{ex['input']}

OUTPUT:
{ex['target']}
"""
        return formatted