
class MemoryAPI:
    def __init__(self):
        self.memory = {}

    def _load_scenario(self, initial_config: dict, long_context: bool = False):
        self.memory = initial_config
