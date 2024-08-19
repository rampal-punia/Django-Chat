# apps/chat/services.py

import io
import numpy as np
import librosa
import speech_recognition as sr
from PIL import Image
from transformers import pipeline, AutoFeatureExtractor
from gtts import gTTS
import torch
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async

from .models import Message, ImageAnalysis, AudioAnalysis
# from ultralytics import YOLOWorld


class MultiModalHandler:
    def __init__(self) -> None:
        model_name = "google/vit-base-patch16-224"
        feature_extractor = AutoFeatureExtractor.from_pretrained(
            model_name, use_fast=True)

        device = 0 if torch.cuda.is_available() else -1

        self.image_classifier = pipeline(
            "image-classification",
            model=model_name,
            feature_extractor=feature_extractor,
            device=device
        )
        self.speech_recognizer = sr.Recognizer()

    async def process_message(self, message):
        if message.content_type == 'IM':
            return await self.process_image(message)
        elif message.content_type == 'AU':
            return await self.process_audio(message)
        elif message.content_type == 'VI':
            return await self.process_video(message)

    async def process_image(self, message):
        image = await sync_to_async(Image.open)(message.file.path)
        results = await sync_to_async(self.image_classifier)(image)
        analysis_result = {'classifications': results}
        await self.create_image_analysis(message, analysis_result)
        return analysis_result

    @database_sync_to_async
    def create_image_analysis(self, message, analysis_result):
        ImageAnalysis.objects.create(
            message=message, analysis_result=analysis_result)

    async def process_audio(self, message):
        audio_file = message.file.path
        text = await sync_to_async(self.speech_to_text)(audio_file)
        analysis_result = {'transcription': text}
        await self.create_audio_analysis(message, analysis_result)
        return analysis_result

    @database_sync_to_async
    def create_audio_analysis(self, message, analysis_result):
        AudioAnalysis.objects.create(
            message=message, analysis_result=analysis_result)

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

    @sync_to_async
    def text_to_speech(self, text, output_file):
        tts = gTTS(text=text, lang='en')
        tts.save(output_file)
        return output_file

    async def process_video(self, message):
        # Implement video processing logic here
        pass
