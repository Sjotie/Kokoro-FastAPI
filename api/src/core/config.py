from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API Settings
    api_title: str = "Kokoro TTS API"
    api_description: str = "API for text-to-speech generation using Kokoro"
    api_version: str = "1.0.0"
    host: str = "0.0.0.0"
    port: int = 8880

    # TTS Settings
    output_dir: str = "output"
    default_voice: str = "af"
    model_path: str = "kokoro-v0_19.pth"
    voices_dir: str = "voices"
    sample_rate: int = 24000

    class Config:
        env_file = ".env"


settings = Settings()