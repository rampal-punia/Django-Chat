# apps/audio_interface/services.py

import io
import numpy as np
import librosa
import speech_recognition as sr
from transformers import AutoFeatureExtractor
from gtts import gTTS
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async

from .models import AudioMessage


class VoiceModalHandler:
    def __init__(self) -> None:
        self.speech_recognizer = sr.Recognizer()

    async def process_message(self, message):
        if message.content_type == 'AU':
            return await self.process_audio(message)
        else:
            return

    async def process_audio(self, message):
        audio_file = message.file.path
        text = await sync_to_async(self.speech_to_text)(audio_file)
        analysis_result = {'transcription': text}
        await self.create_audio_analysis(message, analysis_result)
        return analysis_result

    @database_sync_to_async
    def create_audio_analysis(self, message, analysis_result):
        AudioMessage.objects.create(
            message=message,
            transcript=analysis_result,
            duration=duration
        )

    def speech_to_text(self, audio_file):
        with sr.AudioFile(audio_file) as source:
            audio = self.speech_recognizer.record(source)
        try:
            text = self.speech_recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            text = "Speech recognition could not understand the audio"
        except sr.RequestError:
            text = "Could not request results from the speech recognition service"
        return text

    async def text_to_speech(self, text, output_file):
        def _text_to_speech():
            tts = gTTS(text=text, lang='en')
            tts.save(output_file)
            return output_file

        return await sync_to_async(_text_to_speech)()
