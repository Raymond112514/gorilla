import json
from copy import deepcopy
from pathlib import Path

from bfcl.utils import extract_test_category_from_id

MAX_SHORT_TERM_MEMORY_SIZE = 7
MAX_SHORT_TERM_MEMORY_ENTRY_LENGTH = 300
MAX_LONG_TERM_MEMORY_SIZE = 50
MAX_LONG_TERM_MEMORY_ENTRY_LENGTH = 2000


class MemoryAPI:
    """
    A class that provides APIs to manage short-term and long-term memory data.
    """

    def __init__(self):
        self.short_term_memory = {}
        self.long_term_memory = {}
        self._api_description = "This tool belongs to the memory suite, which provides APIs to manage short-term and long-term memory data."

    def _load_scenario(self, initial_config: dict, long_context: bool = False):
        # We don't care about the long_context parameter here
        # It's there to match the signature of functions in the multi-turn evaluation code
        result_dir: Path = initial_config["result_dir"]
        model_name_dir: str = initial_config["model_name_dir"]
        test_category: str = initial_config["test_category"]
        target_file = (
            result_dir / model_name_dir / "memory_snapshot" / f"{test_category}_final.json"
        )

        if not target_file.exists():
            raise FileNotFoundError(f"Memory snapshot file not found: {target_file}")

        with open(target_file, "r") as f:
            memory_data = json.load(f)
            self.short_term_memory = deepcopy(memory_data["short_term_memory"])
            self.long_term_memory = deepcopy(memory_data["long_term_memory"])

    def _flush_memory_to_local_file(
        self, result_dir: Path, model_name_dir: str, test_entry_id: str
    ):
        """
        Flush (save) current memory (both short-term and long-term)
        to a local JSON file.
        """
        test_category = extract_test_category_from_id(test_entry_id)

        target_dir = result_dir / model_name_dir / "memory_snapshot"
        target_dir.mkdir(parents=True, exist_ok=True)

        with open(target_dir / f"{test_entry_id}.json", "w") as f:
            json.dump(
                {
                    "short_term_memory": self.short_term_memory,
                    "long_term_memory": self.long_term_memory,
                },
                f,
                indent=4,
            )
        with open(target_dir / f"{test_category}_final.json", "w") as f:
            json.dump(
                {
                    "short_term_memory": self.short_term_memory,
                    "long_term_memory": self.long_term_memory,
                },
                f,
                indent=4,
            )

    def send_message_to_user(self, message: str):
        """
        Send a message to the user. This is the only way you can communicate with the user.

        Args:
            message (str): The message to send to the user.
        """
        return None

    def short_term_memory_add(self, key: str, value: str):
        """
        Add a key-value pair to the short-term memory. Make sure to use meaningful keys for easy retrieval later.

        Args:
            key (str): The key under which the value is stored. The key should be unique and case-sensitive.
            value (str): The value to store in the short-term memory.

        Returns:
            status (str): Status of the operation.
        """
        key, value = str(key), str(value)
        if len(self.short_term_memory) >= MAX_SHORT_TERM_MEMORY_SIZE:
            return {"error": "Short term memory is full. Please clear some entries."}
        if len(value) > MAX_SHORT_TERM_MEMORY_ENTRY_LENGTH:
            return {
                "error": f"Entry is too long. Please shorten the entry to less than {MAX_SHORT_TERM_MEMORY_ENTRY_LENGTH} characters."
            }
        if key in self.short_term_memory:
            return {"error": "Key name must be unique."}

        self.short_term_memory[key] = value
        return {"status": "Key added."}

    def short_term_memory_remove(self, key: str):
        """
        Remove a key-value pair from the short-term memory.

        Args:
            key (str): The key to remove from the short-term memory. Case-sensitive.

        Returns:
            status (str): Status of the operation.
        """
        if key in self.short_term_memory:
            del self.short_term_memory[key]
            return {"status": "Key removed."}
        else:
            return {"error": "Key not found."}

    def short_term_memory_replace(self, key: str, value: str):
        """
        Replace a key-value pair in the short-term memory with a new value.

        Args:
            key (str): The key to replace in the short-term memory. Case-sensitive.
            value (str): The new value associated with the key.

        Returns:
            status (str): Status of the operation.
        """
        key, value = str(key), str(value)
        if key not in self.short_term_memory:
            return {"error": "Key not found."}
        if len(value) > MAX_SHORT_TERM_MEMORY_ENTRY_LENGTH:
            return {
                "error": f"Entry is too long. Please shorten the entry to less than {MAX_SHORT_TERM_MEMORY_ENTRY_LENGTH} characters."
            }

        self.short_term_memory[key] = value
        return {"status": "Key replaced."}

    def short_term_memory_clear(self):
        """
        Clear all key-value pairs from the short-term memory.

        Returns:
            status (str): Status of the operation.
        """
        self.short_term_memory = {}
        return {"status": "Short term memory cleared."}

    def short_term_memory_retrieve(self, key: str):
        """
        Retrieve the value associated with a key from the short-term memory.

        Args:
            key (str): The key to retrieve. Case-sensitive.

        Returns:
            value (str): The value associated with the key.

        """
        if key not in self.short_term_memory:
            return {"error": "Key not found."}
        return {"value": self.short_term_memory[key]}

    def short_term_memory_list_keys(self):
        """
        List all keys currently in the short-term memory.

        Returns:
            keys (List[str]): A list of all keys in the short-term memory.
        """
        return {"keys": list(self.short_term_memory.keys())}

    def short_term_memory_retrieve_all(self):
        """
        Retrieve all key-value pairs from the short-term memory.

        Returns:
            dict: A dictionary of all key-value pairs in the short-term memory.
        """
        return self.short_term_memory

    def long_term_memory_add(self, key: str, value: str):
        """
        Add a key-value pair to the long-term memory. Make sure to use meaningful keys for easy retrieval later.
        Args:
            key (str): The key under which the value is stored. The key should be unique and case-sensitive.
            value (str): The value to store in the long-term memory.

        Returns:
            status (str): Status of the operation.
        """
        key, value = str(key), str(value)
        if len(self.long_term_memory) >= MAX_LONG_TERM_MEMORY_SIZE:
            return {"error": "Long term memory is full. Please clear some entries."}
        if len(value) > MAX_LONG_TERM_MEMORY_ENTRY_LENGTH:
            return {
                "error": f"Entry is too long. Please shorten the entry to less than {MAX_LONG_TERM_MEMORY_ENTRY_LENGTH} characters."
            }
        if key in self.long_term_memory:
            return {"error": "Key name must be unique."}

        self.long_term_memory[key] = value
        return {"status": "Key added."}

    def long_term_memory_remove(self, key: str):
        """
        Remove a key-value pair from the long-term memory.

        Args:
            key (str): The key to remove from the long-term memory. Case-sensitive.

        Returns:
            status (str): Status of the operation.
        """
        if key in self.long_term_memory:
            del self.long_term_memory[key]
            return {"status": "Key removed."}
        else:
            return {"error": "Key not found."}

    def long_term_memory_replace(self, key: str, value: str):
        """
        Replace a key-value pair in the long-term memory with a new value.

        Args:
            key (str): The key to replace in the long-term memory. Case-sensitive.
            value (str): The new value associated with the key.

        Returns:
            status (str): Status of the operation.
        """
        key, value = str(key), str(value)
        if key not in self.long_term_memory:
            return {"error": "Key not found."}
        if len(value) > MAX_LONG_TERM_MEMORY_ENTRY_LENGTH:
            return {
                "error": f"Entry is too long. Please shorten the entry to less than {MAX_LONG_TERM_MEMORY_ENTRY_LENGTH} characters."
            }

        self.long_term_memory[key] = value
        return {"status": "Key replaced."}

    def long_term_memory_clear(self):
        """
        Clear all key-value pairs from the long-term memory.

        Returns:
            status (str): Status of the operation.
        """
        self.long_term_memory = {}
        return {"status": "Long term memory cleared."}

    def long_term_memory_retrieve(self, key: str):
        """
        Retrieve the value associated with a key from the long-term memory.

        Args:
            key (str): The key to retrieve. Case-sensitive.

        Returns:
            value (str): The value associated with the key.
        """
        if key not in self.long_term_memory:
            return {"error": "Key not found."}
        return {"value": self.long_term_memory[key]}

    def long_term_memory_list_keys(self):
        """
        List all keys currently in the long-term memory.

        Returns:
            keys (List[str]): A list of all keys in the long-term memory.
        """
        return {"keys": list(self.long_term_memory.keys())}
