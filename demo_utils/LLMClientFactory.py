from openai import OpenAI
import json
from pathlib import Path

class LLMClientFactory:
    _instance = None
    _config = None
    
    def __init__(self, config_path='./llm_config.json'):
        self.config_path = config_path
    
    def load_config(self):
        if self._config is None:
            self._config = json.load(open(self.config_path, 'r'))
        return self._config
    
    @classmethod
    def get_client(cls, config_path='./llm_config.json'):
        if cls._instance is None:
            factory = cls(config_path)
            config = factory.load_config()
            cls._instance = OpenAI(
                api_key=config['api_key'],
                base_url=config['base_url']
            )
        return cls._instance
    
    @classmethod
    def reset_client(cls):
        cls._instance = None
        cls._config = None