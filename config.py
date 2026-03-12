import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./agents.db')
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', False)
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    MAX_AGENTS = int(os.getenv('MAX_AGENTS', 100))
    MAX_TASKS_PER_AGENT = int(os.getenv('MAX_TASKS_PER_AGENT', 50))
    TASK_TIMEOUT = int(os.getenv('TASK_TIMEOUT', 3600))
    WEBHOOK_TIMEOUT = int(os.getenv('WEBHOOK_TIMEOUT', 30))
    AGENT_MEMORY_SIZE = int(os.getenv('AGENT_MEMORY_SIZE', 1000))

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

class TestingConfig(Config):
    TESTING = True
    DATABASE_URL = 'sqlite:///./test.db'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}