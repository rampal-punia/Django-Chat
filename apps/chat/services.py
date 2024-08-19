# apps/chat/services.py

import io
import numpy as np
import librosa
import speech_recognition as sr
from PIL import Image
from transformers import pipeline, AutoFeatureExtractor
from gtts import gTTS
import torch

from .models import Message, ImageAnalysis, AudioAnalysis
from ultralytics import YOLOWorld


class MultiModalHandler:
    def __init__(self) -> None:
        model_name = "google/vit-base-patch16-224"
        # Use the fast image processor
        feature_extractor = AutoFeatureExtractor.from_pretrained(
            model_name, use_fast=True)

        # Determine the device (CPU or GPU)
        device = 0 if torch.cuda.is_available() else -1

        self.image_classifier = pipeline(
            "image-classification",
            model=model_name,
            feature_extractor=feature_extractor,
            device=device
        )
        self.speech_recognizer = sr.Recognizer()

    def process_message(self, message):
        if message.content_type == 'IM':
            return self.process_image(message)
        elif message.content_type == 'AU':
            return self.process_audio(message)
        elif message.content_type == 'VI':
            return self.process_video(message)

    def process_image(self, message):
        image = Image.open(message.file)
        results = self.image_classifier(image)
        analysis_result = {'classifications': results}
        message.imageanalysis.create(analysis_result=analysis_result)
        return analysis_result

    def process_audio(self, message):
        audio_file = message.file.path
        text = self.speech_to_text(audio_file)
        analysis_result = {'transcription': text}
        message.audioanalysis.create(analysis_result=analysis_result)
        return analysis_result

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

    def text_to_speech(self, text, output_file):
        tts = gTTS(text=text, lang='en')
        tts.save(output_file)
        return output_file

    def process_video(self, message):
        # Implement video processing logic here
        pass
