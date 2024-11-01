import requests
import logging


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_llm_model(prompt):
    url = "http://localhost:11434/api/chat"
    data = {
        "model": "llama3.1",
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
            url,
            headers={"Content-Type": "application/json"},
            json=data,
            timeout=60
        )
        response.raise_for_status()
        logger.info("Get response from LLama successfully.")
        return response.json()["message"]["content"]
    except requests.exceptions.RequestException as e:
        raise Exception("Get response from LLama failed.")