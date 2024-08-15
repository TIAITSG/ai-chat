# Discord AI Chat Bot

## Overview

Welcome to the **Discord AI Chat Bot**! This bot leverages the power of AI to provide interactive and engaging conversations. Built using the `discord.py` library, it integrates with the Anthropic API for AI responses and uses a MySQL database to store chat history. Get ready for some fun and intelligent chats! 🎉

## Features

### 🛠️ Environment Setup
- **Environment Variables**: The bot uses environment variables for configuration, loaded using `dotenv`.

### 🤖 Discord Bot Initialization
- **Intents**: The bot is initialized with default intents, with message content enabled.
- **Command Prefix**: The bot listens for commands prefixed with `!`.

### 🌐 Anthropic Client
- **API Integration**: The bot integrates with the Anthropic API using an API key stored in environment variables.

### 🗄️ MySQL Database
- **Database Connection**: The bot connects to a MySQL database using credentials stored in environment variables.
- **Table Creation**: Ensures the `chat_history` table exists with the appropriate character set for storing messages.

### 💬 Chat History
- **Save Messages**: Functionality to save messages to the MySQL database.
- **Retrieve Messages**: Placeholder for retrieving the last N messages from the database.

### 🎭 Response Categories
The bot can respond in various styles, each tailored to a specific persona:
- **IT**: Friendly and professional IT support assistant.
- **Doctor**: Knowledgeable and compassionate doctor.
- **Teacher**: Patient and informative teacher.
- **Comedian**: Witty and humorous comedian.
- **Motivator**: Encouraging and positive motivator.
- **Lawyer**: Formal and precise lawyer.
- **Engineer**: Technical and detail-oriented engineer.
- **Philosopher**: Reflective and thoughtful philosopher.
- **Chef**: Friendly and practical chef.

### 📜 Message Handling
- **Message Splitting**: Functionality to split messages into chunks of a maximum of 2000 characters.

### 🔄 API Request Handling
- **Retry Logic**: Placeholder for making API calls with retry logic.

### 📝 Bot Commands
- **/chat Command**: 
  - **Description**: Start a chat with the AI.
  - **Parameters**:
    - `prompt`: The prompt for the AI to respond to.
    - `category`: Choose the category for the response style.
    - `temperature`: Temperature for the AI response (0.0 - 1.0).
    - `formality`: Choose the formality level.
    - `detail`: Choose the detail level.
    - `humor`: Choose the humor level.
  - **Choices**: 
    - IT
    - Doctor
    - Teacher
    - Comedian
    - Motivator
    - Lawyer
    - Engineer
    - Philosopher
    - Chef

### 📅 Event Listeners
- **Ready Event**: Placeholder for actions to perform when the bot is ready.
- **Message Listener**: Placeholder for responding to messages when the bot is mentioned.
- **Unknown Command Handler**: Placeholder for handling unknown commands.

### 🚀 Running the Bot
- **Bot Token**: The bot runs using a Discord token stored in environment variables.

## Requirements

The project dependencies are listed in the `requirements.txt` file:
- `discord.py`
- `requests`
- `dotenv`
- `python-dotenv`
- `anthropic`
- `mysql-connector-python`
- `discord`

## Setup

1. **Clone the repository**:
    ```sh
    git clone https://github.com/dcodeu/ai-chat
    cd ai-chat
    ```

2. **Install dependencies**:
    ```sh
    pip install -r requirements.txt
    ```

3. **Set up a MySQL Database**:
    - Create a MySQL database to store conversation history.
    - Note down the database credentials (host, user, password, database name).

4. **Set up environment variables**:
    Create a `.env` file in the project root and add the following variables:
    ```env
    DISCORD_BOT_TOKEN=your_discord_bot_token
    CLAUDE_API_KEY=your_anthropic_api_key
    MYSQL_HOST=your_mysql_host
    MYSQL_USER=your_mysql_user
    MYSQL_PASSWORD=your_mysql_password
    MYSQL_DATABASE=your_mysql_database
    ```

5. **Run the bot**:
    ```sh
    python bot.py
    ```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any changes.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.