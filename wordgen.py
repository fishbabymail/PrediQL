import copy
import os
from typing import List, Optional

import requests
import json
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LLMWordGenerator:
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama2"):
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.available_models = self._get_available_models()

        if not self._validate_model(self.model):
            available_models_str = ", ".join(self.available_models)
            raise ValueError(
                f"Model '{self.model}' is not available. "
                f"Available models: {available_models_str}"
            )

    def _validate_model(self, model: str) -> bool:
        return model in self.available_models

    def _get_available_models(self) -> List[str]:
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                models = [model['name'] for model in response.json()['models']]
                logger.info(f"Available models: {models}")
                return models
            else:
                logger.error(f"Failed to fetch models. Status code: {response.status_code}")
                return []
        except requests.exceptions.RequestException as e:
            logger.error(f"Error connecting to Ollama API: {e}")
            return []

    def llm_model(self, ep: str)-> Optional[str]:
        """Generate words using the specified LLM model"""
        url = "http://localhost:11434/api/chat"
        prompt = (f"Please generate 100 single words without about schema of {ep} as a python list. "
                  f"The returned list must follow the format like this: ['xx', 'xx', 'xx', ...] "
                  f"Return only full word list for me, no more extra explanation.")
        data = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt

                }
            ],
            "stream": False,
        }

        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                headers={"Content-Type": "application/json"},
                json=data,
                timeout=30
            )
            response.raise_for_status()
            return response.json()["message"]["content"]
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return None

    def wordlist_gen(self, endpoint: str, file_save_path: str, filename: str, target_words: int = 1000, max_rounds: int = 20) -> List[str]:
        if not os.path.exists(file_save_path):
            os.makedirs(file_save_path)
        exist_words = []
        word_num = 0
        round_count = 0

        while word_num < target_words and round_count < max_rounds:
            round_count += 1
            try:
                data = self.llm_model(endpoint)
                if not data:
                    continue
                try:
                    idx_l = data.find('[')
                    idx_r = data.rfind(']')
                    if idx_l == -1 or idx_r == -1:
                        raise ValueError("Invalid response format")
                    lpart = data[idx_l : idx_r+1]
                    round_words = eval(lpart)
                    if not isinstance(round_words, list):
                        raise ValueError("Response is not a list")

                except (SyntaxError, ValueError) as e:
                    logger.error(f"Failed to parse response: {e}")
                    continue
                filepath = os.path.join(file_save_path, filename)
                with open(filepath, "w") as file:
                    for w in round_words:
                        if isinstance(w, str) and w.strip() and w not in exist_words:
                            exist_words.append(w)
                            file.write(f"{w}\n")
                            word_num += 1
                            if word_num >= target_words:
                                break
            except Exception as e:
                logger.error(f"Error in round {round_count}: {e}")
                continue
        if word_num < target_words:
            logger.warning(f"Only generated {word_num} words out of {target_words} requested")

        return exist_words

def main():
    # Configuration
    endpoint = "https://covid19-graphql.now.sh/"
    model = "llama3.1:latest"  # Change this to use a different model
    base_url = "http://localhost:11434"
    output_dir = "wordlist"
    output_file = "llama_wordlist.txt"
    target_words = 1000
    max_rounds = 20

    try:
        # Initialize generator with specified model
        generator = LLMWordGenerator(base_url=base_url, model=model)

        # Generate words
        words = generator.wordlist_gen(
            endpoint=endpoint,
            file_save_path=output_dir,
            filename=output_file,
            target_words=target_words,
            max_rounds=max_rounds
        )
        logger.info(f"Successfully generated {len(words)} words using model {model}")

    except Exception as e:
        logger.error(f"Program failed: {e}")


if __name__ == "__main__":
    main()