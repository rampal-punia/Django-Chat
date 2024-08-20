{% extends 'base.html' %}
{% load static %}

{% block title %}
    Home Page
{% endblock title %}

{% block content %}
<div class="col-md-11 col-sm-11 mx-2">
    <div class="row">
        <h1 class="display-4 mb-4">Django Chat Platform: Features</h1>
        <div class="col-sm-6 mb-3 mb-sm-0">
            <div class="card border-primary mb-3">
                <div class="card-header">
                    Dj-ChatBot
                </div>
                <div class="card-body">
                    <h5 class="card-title">Start a chat</h5>
                    <p class="card-text">Start Chatting with DjChat</p>
                    <a href="{% url "chat:new_conversation_url" %}" class="btn btn-outline-primary">DjChat</a>
                </div>
            </div>
        </div>
        <div class="col-sm-6 mb-3 mb-sm-0">
            <div class="card border-primary mb-3">
                <div class="card-header">
                    Dj-AudioChatBot
                </div>
                <div class="card-body">
                    <h5 class="card-title">Start an Audio chat</h5>
                    <p class="card-text">Get talkative with Dj-AudioChatBot</p>
                    <a href="{% url "audio_interface:new_audio_url" %}" class="btn btn-outline-primary">DjAudioChat</a>
                </div>
            </div>
        </div>
        <div class="col-sm-6 mb-3 mb-sm-0">
            <div class="card border-primary mb-3">
                <div class="card-header">
                    Dj-DocSummarizer
                </div>
                <div class="card-body">
                    <h5 class="card-title">Upload Doc and Start a chat</h5>
                    <p class="card-text">Explor your docs with Dj-DocSummarizer</p>
                    <a href="{% url "audio_interface:new_audio_url" %}" class="btn btn-outline-primary">DjDocSumarizerChat</a>
                </div>
            </div>
        </div>
        <div class="col-sm-6 mb-3 mb-sm-0">
            <div class="card border-primary mb-3">
                <div class="card-header">
                    Dj-ImageDescriber
                </div>
                <div class="card-body">
                    <h5 class="card-title">Upload Doc and Start a chat</h5>
                    <p class="card-text">Explor your docs with Dj-ImageDescriber</p>
                    <a href="{% url "audio_interface:new_audio_url" %}" class="btn btn-outline-primary">DjImageDescriberChat</a>
                </div>
            </div>
        </div>
    </div>
</div>  
{% endblock content %}