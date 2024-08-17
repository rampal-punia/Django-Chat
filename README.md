# Django Chat Webapp

A real-time chat application built with Django, featuring seamless communication with an AI language model.

## Table of Contents
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [API Integration](#api-integration)
- [Contributing](#contributing)
- [License](#license)

## Features

- Real-time chat functionality using WebSockets
- Integration with AI language models for intelligent responses
- User authentication and conversation management
- Automatic conversation title generation
- Markdown support for message rendering
- Responsive design for various devices

## Technologies Used

- Django: Web framework for backend development
- Channels: For WebSocket support and asynchronous capabilities
- Langchain: For integrating with various language models
- Hugging Face Transformers: For accessing pre-trained language models
- JavaScript: For frontend interactivity
- HTML/CSS: For structuring and styling the user interface

## Project Structure

The main components of the chat application include:

- `consumers.py`: WebSocket consumer for handling real-time communication
- `models.py`: Database models for Conversation and Message
- `views.py`: Django views for rendering pages and handling requests
- `urls.py`: URL routing for the application
- `routing.py`: WebSocket routing configuration
- `configure_llm.py`: Configuration for language model integration
- `chat.html`: Main template for the chat interface

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
   - Add necessary variables (e.g., `SECRET_KEY`, `DEBUG`, `HUGGINGFACE_API_TOKEN`)

5. Run migrations:
   ```
   python manage.py migrate
   ```

6. Start the development server:
   ```
   python manage.py runserver
   ```

## Usage

1. Register a new account or log in to an existing one.
2. Start a new conversation or select an existing one from the dashboard.
3. Type your message in the input field and press enter to send.
4. The AI assistant will respond in real-time.
5. You can view your conversation history and manage your chats from the dashboard.

## API Integration

This project integrates with the Hugging Face API for language model inference and title generation. To use these features:

1. Sign up for a Hugging Face account and obtain an API token.
2. Add your Hugging Face API token to the `.env` file:
   ```
   HUGGINGFACE_API_TOKEN=your_token_here
   ```

The application uses the following models:
- Text generation: Various models including Mistral and LLaMA variants
- Title generation: "czearing/article-title-generator"

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Hit Start

Like this project! Consider hitting the star ⭐ button.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.