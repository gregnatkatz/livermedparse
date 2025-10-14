import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    USE_MOCK_DATA: bool = os.getenv("USE_MOCK_DATA", "true").lower() == "true"
    
    AZURE_TENANT_ID: str = os.getenv("AZURE_TENANT_ID", "")
    AZURE_CLIENT_ID: str = os.getenv("AZURE_CLIENT_ID", "")
    AZURE_CLIENT_SECRET: str = os.getenv("AZURE_CLIENT_SECRET", "")
    AZURE_SUBSCRIPTION_ID: str = os.getenv("AZURE_SUBSCRIPTION_ID", "")
    
    AZURE_OPENAI_ENDPOINT: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    AZURE_OPENAI_API_KEY: str = os.getenv("AZURE_OPENAI_API_KEY", "")
    AZURE_OPENAI_API_VERSION: str = os.getenv("AZURE_OPENAI_API_VERSION", "2025-01-01-preview")
    
    AZURE_OPENAI_DEPLOYMENT_O1: str = os.getenv("AZURE_OPENAI_DEPLOYMENT_O1", "o1")
    AZURE_OPENAI_DEPLOYMENT_O3: str = os.getenv("AZURE_OPENAI_DEPLOYMENT_O3", "o3")
    AZURE_OPENAI_DEPLOYMENT_GPT41: str = os.getenv("AZURE_OPENAI_DEPLOYMENT_GPT41", "gpt-4.1")
    AZURE_OPENAI_DEPLOYMENT_GPT41_MINI: str = os.getenv("AZURE_OPENAI_DEPLOYMENT_GPT41_MINI", "gpt-4.1-mini")
    AZURE_OPENAI_DEPLOYMENT_DEEPSEEK: str = os.getenv("AZURE_OPENAI_DEPLOYMENT_DEEPSEEK", "DeepSeek-V3-0324")
    
    O3_ENDPOINT: str = os.getenv("O3_ENDPOINT", "")
    O3_API_KEY: str = os.getenv("O3_API_KEY", "")
    O1_ENDPOINT: str = os.getenv("O1_ENDPOINT", "")
    O1_API_KEY: str = os.getenv("O1_API_KEY", "")
    GPT41_ENDPOINT: str = os.getenv("GPT41_ENDPOINT", "")
    GPT41_API_KEY: str = os.getenv("GPT41_API_KEY", "")
    
    MEDIMAGEPARSE3D_ENDPOINT: str = os.getenv("MEDIMAGEPARSE3D_ENDPOINT", "")
    MEDIMAGEPARSE3D_API_KEY: str = os.getenv("MEDIMAGEPARSE3D_API_KEY", "")
    
    AZURE_RESOURCE_GROUP: str = os.getenv("AZURE_RESOURCE_GROUP", "")
    AZURE_ML_WORKSPACE: str = os.getenv("AZURE_ML_WORKSPACE", "")
    
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

settings = Settings()
