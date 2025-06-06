from openai import OpenAI
import tempfile
import os
import logging

class TextToSpeech:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
    
    async def generate_speech(self, text: str, language: str = "en") -> str:
        try:
            voice = "alloy" 

            response = self.client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text
            )
            

            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
                response.with_streaming_response(temp_file.name)
                return temp_file.name
                
        except Exception as e:
            logging.error(f"TTS error: {e}")
            return None