
class CLI:
    def __init__(self, cli: str):
        
        self.cli = cli

    def index(self, max_chunk_size: int):
        pass

    def search(self, query: str, k: int):
        pass

    def search_dataset(self, dataset_path: str, k: int, save_directory: str):
        pass

    def answer(self, cli: str):
        pass

    def answer_dataset(self, cli: str):
        pass

    def evaluate(self, cli: str):
        pass

    def process_cli(self):
        
        if "index" in self.cli:
            self._index_cli(self.cli)
        elif "sreach" in self.cli:
            self._search_cli(self.cli)




