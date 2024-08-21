{% extends 'base.html' %}
{% load static %}
{% load markdown_filters %}

{% block on_page_css %}
<link rel="stylesheet" type="text/css" media="all" href="{% static 'css/style.css' %}">
{% endblock on_page_css %}

{% block content %}
<div class="chat-container">
    <div id="qa-container" class="col-md-11 col-xl-11 mx-4">
        <h2 id="conversation-title">
            {% if conversation.title %}{{ conversation.title|truncatechars:40 }}{% else %}Untitled Conversation{% endif %}
        </h2>
        <hr>

        {% if previous_messages %}
            {% for message in previous_messages %}
                <div id="qa-pair-{{ forloop.counter }}" class="qa-pair">
                    {% if message.is_from_user %}
                        <div class="question-area d-flex justify-content-end">
                            {% if message.content_type == 'AU' %}
                                <div class="audio-message">
                                    <audio controls src="{{ message.audio_content.audio_file.url }}"></audio>
                                    <span>{{ message.audio_content.transcript }}</span>
                                </div>
                            {% else %}
                                <p>{{ message.chat_content.content }}</p>
                            {% endif %}
                        </div>
                    {% else %}
                        <div class="card">
                            <div class="card-body">
                                <div class="answer-area">
                                    <div class="message-content">
                                        {% if message.content_type == 'AU' %}
                                            <div class="audio-message">
                                                <audio controls src="{{ message.audio_content.audio_file.url }}"></audio>
                                                <span>{{ message.audio_content.transcript }}</span>
                                            </div>
                                        {% else %}
                                            {{ message.chat_content.content|markdown_to_html|safe }}
                                        {% endif %}
                                    </div>
                                </div>
                            </div>
                        </div>
                    {% endif %}
                </div>
            {% endfor %}
        {% endif %}
    </div>

    <div class="input-group mb-1 fixed-bottom-input bg-light">
        <div class="audio-controls">
            <button id="startRecording" class="btn btn-primary">Start Recording</button>
            <button id="stopRecording" class="btn btn-danger" disabled>Stop Recording</button>
        </div>
        <input type="text" id="messageInput" class="form-control" placeholder="Type your message...">
        <button id="sendMessage" class="btn btn-primary">Send</button>
    </div>
</div>
{% endblock content %}

{% block extra_js %}
<script src="https://cdnjs.cloudflare.com/ajax/libs/RecordRTC/5.6.2/RecordRTC.min.js"></script>
<script>
    let recorder;
    const startRecordingButton = document.getElementById('startRecording');
    const stopRecordingButton = document.getElementById('stopRecording');
    const messageInput = document.getElementById('messageInput');
    const sendMessageButton = document.getElementById('sendMessage');
    const qaContainer = document.getElementById('qa-container');
    const conversationTitle = document.getElementById('conversation-title');

    let chatSocket;

    function connectWebSocket() {
        const conversationId = '{{ conversation.id }}';
        const wsScheme = window.location.protocol === 'http:' ? 'ws' : 'ws';
        const wsPath = `${wsScheme}://${window.location.host}/ws/audio_chat/${conversationId}/`;
        
        chatSocket = new WebSocket(wsPath);

        chatSocket.onopen = function(e) {
            console.log('WebSocket connection established');
        };

        chatSocket.onmessage = function(e) {
            const data = JSON.parse(e.data);
            handleWebSocketMessage(data);
        };

        chatSocket.onclose = function(e) {
            console.error('WebSocket closed unexpectedly');
        };
    }

    function handleWebSocketMessage(data) {
        if (data.type === 'welcome') {
            console.log(data.message);
        } else if (data.type === 'title_update') {
            conversationTitle.textContent = data.title;
        } else if (data.type === 'transcription' || data.type === 'ai_response') {
            updateOrCreateMessage(data);
        }
    }

    function updateOrCreateMessage(data) {
        let messageElement = document.getElementById(`message-${data.id}`);
        if (!messageElement) {
            messageElement = document.createElement('div');
            messageElement.id = `message-${data.id}`;
            messageElement.className = 'card mb-3';
            qaContainer.appendChild(messageElement);
        }

        if (data.type === 'transcription') {
            messageElement.innerHTML = `
                <div class="card-body">
                    <div class="message-content">${data.message}</div>
                </div>
            `;
        } else if (data.type === 'ai_response') {
            messageElement.innerHTML = `
                <div class="card-body">
                    <div class="audio-message">
                        <audio controls src="${data.audio_url}"></audio>
                        <div class="message-content">${marked(data.message)}</div>
                    </div>
                </div>
            `;
        }

        qaContainer.scrollTop = qaContainer.scrollHeight;
    }

    startRecordingButton.onclick = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            recorder = new RecordRTC(stream, {
                type: 'audio',
                mimeType: 'audio/webm',
                recorderType: RecordRTC.StereoAudioRecorder,
                numberOfAudioChannels: 1,
                desiredSampRate: 16000
            });
            recorder.startRecording();

            startRecordingButton.disabled = true;
            stopRecordingButton.disabled = false;
        } catch (error) {
            console.error('Error starting recording:', error);
        }
    };

    stopRecordingButton.onclick = () => {
        recorder.stopRecording(() => {
            const blob = recorder.getBlob();
            sendAudioMessage(blob);

            startRecordingButton.disabled = false;
            stopRecordingButton.disabled = true;
        });
    };

    function sendAudioMessage(audioBlob) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const base64Audio = e.target.result.split(',')[1];
            chatSocket.send(JSON.stringify({
                'type': 'AU',
                'message': base64Audio,
                'uuid': '{{ conversation.id }}'
            }));
        };
        reader.readAsDataURL(audioBlob);
    }

    sendMessageButton.onclick = function(e) {
        const message = messageInput.value.trim();
        if (message) {
            chatSocket.send(JSON.stringify({
                'type': 'TE',
                'message': message,
                'uuid': '{{ conversation.id }}'
            }));
            messageInput.value = '';
        }
    };

    messageInput.onkeyup = function(e) {
        if (e.key === 'Enter') {
            sendMessageButton.click();
        }
    };

    // Connect WebSocket when the page loads
    connectWebSocket();
</script>
{% endblock extra_js %}