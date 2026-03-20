from agents import UnifiedAgent
from memory_examples import ExampleMemory

class AgentOrchestrator:

    def __init__(self):
        self.memory = ExampleMemory("data.jsonl")
        self.agent = UnifiedAgent(self.memory)

    def run(self, text, caption, tujuan):

        destination = self.detect_destination(text)

        return self.agent.run(text, caption, tujuan)

    def detect_destination(self, text):
        text_lower = text.lower()

        if "toba" in text_lower:
            return "Danau Toba"
        elif "borobudur" in text_lower:
            return "Candi Borobudur"
        else:
            return "Destinasi Wisata"
