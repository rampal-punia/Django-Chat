<!--Template to handle the user-LLM interactions and question answer flow-->

{% extends 'base.html' %}
{% load static %}
{% load markdown_filters %}

{% block title %}- chat{% endblock %}

{% block on_page_css %}
<link rel="stylesheet" type="text/css" media="all" href="{% static 'css/style.css' %}">
{% endblock on_page_css %}

{% block content %}
<div class="chat-container">
    <div id="qa-container" class="col-md-11 col-xl-11 mx-4">
        <h2 id="conversation-title">{% if conversation.title %}{{ conversation.title|truncatechars:40 }}{% else %}Untitled Conversation{% endif %}</h2>
        <hr>
        {% if previous_messages %}
            {% for message in previous_messages %}
                <div class="qa-pair" id="qa-pair-{{ forloop.counter }}">
                    {% if message.is_from_user %}
                        <div class="question-area d-flex justify-content-end">
                            <textarea class="question-textarea text-white" readonly>{{ message.chat_content.content }}</textarea>
                        </div>
                    {% else %}
                        <div class="card">
                            <div class="card-body">
                                <div class="answer-area">
                                    <div class="message-content">
                                         {{ message.chat_content.content|markdown_to_html|safe }}
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
        <textarea class="form-control user_query_area" id="chat-message-input" placeholder="Enter your query"></textarea>
        <button class="btn btn-primary" type="button" id="chat-message-submit">
            <i data-feather="arrow-up" class="f-30"></i>
        </button>
    </div>
</div>
{% endblock content %}

{% block on_page_js %}
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<script>
    let conversationUUID = '{{ conversation_id }}';
    let questionCounter = {{ previous_messages|length }};
    let currentPairId = null;
    let accumulatedChunks = '';
    let isNewConversation = true;

    // Establish a websocket connection using the conversation UUID
    const ws = new WebSocket(
        'ws://' + window.location.host + '/ws/chat/' + conversationUUID + '/'
    );

    // Scroll to the bottom of the chat container
    function scrollToBottom() {
        const qaContainer = document.getElementById('qa-container');
        qaContainer.scrollTop = qaContainer.scrollHeight;
    }

    // Generate a UUID for the conversation if it doesn't already exist 
    function generateUUID() {
        if (!conversationUUID) {
            conversationUUID = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
                var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
                return v.toString(16);
            });
        }
        return conversationUUID;
    }

    // Handle incoming websocket message
    ws.onmessage = function(e) {
    const data = JSON.parse(e.data);
    
    if (data.type === 'welcome') {
        console.log(data.message);
        return;
    }

    if (data.type === 'title_update') {
        // Update the title in the UI
        updateConversationTitle(data.title);
    }

    if (data.event === 'on_parser_start' || data.event === 'on_parser_stream') {
        if (data.data && data.data.chunk) {
            if (data.name === "Assistant") {
                accumulatedChunks += data.data.chunk;
                updateAnswer();
            } else {
                accumulatedSimilarQuestions += data.data.chunk;
            }
        }
    }};
    
    function updateConversationTitle(newTitle) {
        // Update the title in the UI
        const titleElement = document.getElementById('conversation-title');
        if (titleElement) {
            titleElement.textContent = newTitle;
        }

        // If using a header or navigation component, update it there as well
        const headerTitleElement = document.getElementById('header-title');
        if (headerTitleElement) {
            headerTitleElement.textContent = newTitle;
        }

        // If want to update the page title
        document.title = `Chat: ${newTitle}`;
    }

    // Add a question-answer pair to the chat container
    function addQuestionAnswerPair(message, isFromUser, pairId, similarQuestions = null) {
        const qaContainer = document.getElementById('qa-container');
        const qaPair = document.createElement('div');
        qaPair.className = 'qa-pair';
        qaPair.id = `qa-pair-${pairId}`;

        if (isFromUser) { // below with class="question-textarea is applied "
            qaPair.innerHTML = `
                <div class="question-area d-flex justify-content-end">
                    <textarea class="question-textarea bg-primary text-white" readonly>${message}</textarea>
                </div> 
            `;
        } else {
            qaPair.innerHTML = `
                <div class="card mb-3">
                    <div class="card-body">
                        <div id="answer-area-${pairId}" class="answer-area">${marked.parse(message)}</div>
                    </div>
                </div>
            `;
        }

        qaContainer.appendChild(qaPair);
        adjustTextareaHeights();
        scrollToBottom();
    }

    // Update the answer area with accumulated chunks of the response
    function updateAnswer() {
        if (currentPairId) {
            let currentAnswerArea = document.getElementById(`answer-area-${currentPairId}`);
            if (!currentAnswerArea) {
                // If the answer area doesn't exist yet, create it with the card structure
                const qaPair = document.getElementById(`qa-pair-${currentPairId}`);
                if (qaPair) {
                    const cardDiv = document.createElement('div');
                    cardDiv.className = 'card';
                    const cardBodyDiv = document.createElement('div');
                    cardBodyDiv.className = 'card-body';
                    const answerArea = document.createElement('div');
                    answerArea.id = `answer-area-${currentPairId}`;
                    answerArea.className = 'answer-area';
                    
                    cardBodyDiv.appendChild(answerArea);
                    cardDiv.appendChild(cardBodyDiv);
                    qaPair.appendChild(cardDiv);
                    
                    currentAnswerArea = answerArea;
                }
            }
            
            if (currentAnswerArea) {
                currentAnswerArea.innerHTML = marked.parse(accumulatedChunks);
                scrollToBottom();
            }
        }
    }

    // Handle the submission of a new chat message
    document.getElementById('chat-message-submit').onclick = function() {
        const messageInput = document.getElementById('chat-message-input');
        const message = messageInput.value.trim();
        
        if (message) {
            questionCounter++;
            currentPairId = questionCounter;
            accumulatedChunks = '';  // Reset accumulatedChunks for the new response
            addQuestionAnswerPair(message, true, currentPairId);
            
            // Create an empty answer area for the AI response
            addQuestionAnswerPair('', false, currentPairId);
            
            ws.send(JSON.stringify({
                message: message,
                type: 'TE',
                uuid: generateUUID()
            }));
            messageInput.value = '';
        }
    };

    // Handle the Enter key press to submit the chat message
    document.getElementById('chat-message-input').onkeypress = function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            document.getElementById('chat-message-submit').click();
        }
    };

    // Handle web socket closure
    ws.onclose = function(e) {
        console.error('Chat socket closed unexpectedly');
    };

    // Handle websocket error
    ws.onerror = function(event) {
        console.error('WebSocket error:', event);
    };

    function adjustTextareaHeights() {
        const textareas = document.querySelectorAll('.question-textarea');

        textareas.forEach(textarea => {
            // Initial height adjustment
            adjustHeight(textarea);

            // Add event listener for future input
            textarea.addEventListener('input', function() {
                adjustHeight(this);
            });
        });

        // Helper function to adjust a single textarea's height
        function adjustHeight(element) {
            element.style.height = 'auto';
            element.style.height = (element.scrollHeight) + 'px';
        }
    }

    // Ensure the chat container is scrolled to the bottom on page load
    // and resize text areas
    document.addEventListener('DOMContentLoaded', function() {
        scrollToBottom();
        adjustTextareaHeights();
    });
</script>
{% endblock on_page_js %}

{% block extra_js %}
<script>
    document.addEventListener('DOMContentLoaded', (event) => {
        document.querySelectorAll('pre code').forEach((el) => {
            el.innerHTML = el.innerHTML.replace(/&lt;/g, '<').replace(/&gt;/g, '>');
        });
    });
</script>
{% endblock extra_js %}