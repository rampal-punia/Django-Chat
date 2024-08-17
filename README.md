# Django-Chat Webapp

## About

Django-Chat is an innovative, AI-powered chat application that combines the robustness of Django with cutting-edge language models. This project showcases the seamless integration of real-time communication and artificial intelligence, providing users with an intelligent conversational experience. Leveraging WebSockets for instant messaging and Hugging Face's state-of-the-art language models, Django-Chat offers responsive, context-aware interactions. The application features user authentication, conversation management, and automatic title generation, all wrapped in a clean, intuitive interface. With its RESTful API and detailed documentation, Django-Chat is not just a functional chat platform but also a valuable learning resource for developers interested in combining Django, WebSockets, and AI technologies. Whether you're looking to deploy a smart chatbot or explore advanced web development techniques, Django-Chat provides a solid foundation for your next-level web application.

## Table of Contents
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [WebSocket Integration](#websocket-integration)
- [Contributing](#contributing)
- [License](#license)

## Features

- Real-time chat functionality using WebSockets
- Integration with AI language models for intelligent responses
- User authentication and conversation management
- Automatic conversation title generation
- Markdown support for message rendering
- RESTful API for conversations and messages
- Responsive design for various devices

## Technologies Used

- Django 5.x: Web framework for backend development
- Channels: For WebSocket support and asynchronous capabilities
- Django Rest Framework: For building RESTful APIs
- Langchain: For integrating with various language models
- Hugging Face Transformers: For accessing pre-trained language models
- Redis: As a channel layer for WebSocket communication
- Daphne: ASGI server for running Django with WebSocket support
- Bootstrap 5: For responsive frontend design
- JavaScript: For frontend interactivity

## Project Structure

The main components of the chat application include:

- `chat/consumers.py`: WebSocket consumer for handling real-time communication
- `chat/models.py`: Database models for Conversation and Message
- `chat/views.py`: Django views for rendering pages and handling requests
- `chat/urls.py`: URL routing for the chat application
- `config/routing.py`: WebSocket routing configuration
- `chat/configure_llm.py`: Configuration for language model integration
- `chat/templates/chat/chat.html`: Main template for the chat interface
- `chat/api.py`: ViewSets for RESTful API
- `chat/serializers.py`: Serializers for API data representation

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/Django-Chat.git
   cd Django-Chat
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Set up your environment variables:
   - Create a `.env` file in the project root
   - Add necessary variables (e.g., `DJANGO_SECRET_KEY`, `DEBUG`, `HUGGINGFACEHUB_API_TOKEN`)

5. Run migrations:
   ```
   python manage.py migrate
   ```

6. Start the development server:
   ```
   python manage.py runserver
   ```

## Configuration

The project uses a `base.py` file for Django settings. Key configurations include:

- `INSTALLED_APPS`: Includes 'daphne', 'channels', 'rest_framework', 'corsheaders', and 'drf_spectacular' among others.
- `ASGI_APPLICATION`: Set to 'config.asgi.application' for WebSocket support.
- `CHANNEL_LAYERS`: Configured to use Redis as the backend.
- `REST_FRAMEWORK`: Configured with default permission classes and authentication classes.
- `SPECTACULAR_SETTINGS`: Configuration for API documentation using drf-spectacular.
- `HUGGINGFACE_API_TOKEN`: Token for accessing Hugging Face models.

## Usage

1. Register a new account or log in to an existing one.
2. Start a new conversation or select an existing one from the dashboard.
3. Type your message in the input field and press enter to send.
4. The AI assistant will respond in real-time.
5. You can view your conversation history and manage your chats from the dashboard.

## API Endpoints

The project includes a RESTful API for conversations and messages. Key endpoints include:

- `/api/conversations/`: List and create conversations
- `/api/conversations/<uuid:pk>/`: Retrieve, update, or delete a specific conversation
- `/api/messages/`: List and create messages
- `/api/messages/<int:pk>/`: Retrieve, update, or delete a specific message

API documentation is available at:
- `/api/schema/swagger-ui/`: Swagger UI for API documentation
- `/api/schema/redoc/`: ReDoc for API documentation

## WebSocket Integration

The application uses WebSockets for real-time communication. The WebSocket consumer is defined in `chat/consumers.py` and handles the following operations:

- Establishing WebSocket connections
- Receiving and processing messages
- Generating AI responses using language models
- Sending responses back to the client

WebSocket routing is configured in `config/routing.py`.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Hit Start

Like this project! Consider hitting the star ⭐ button.