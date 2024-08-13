import discord
from discord import app_commands
from discord.ext import commands
import os
import anthropic
import mysql.connector
from dotenv import load_dotenv
from collections import defaultdict
import time

# Load environment variables
load_dotenv()

# Initialize the Discord bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Initialize the Anthropic client
client = anthropic.Anthropic(api_key=os.getenv('CLAUDE_API_KEY'))

# MySQL database connection
db = mysql.connector.connect(
    host=os.getenv('MYSQL_HOST'),
    user=os.getenv('MYSQL_USER'),
    password=os.getenv('MYSQL_PASSWORD'),
    database=os.getenv('MYSQL_DATABASE')
)
cursor = db.cursor()

# Ensure the chat_history table exists with utf8mb4 character set
def create_table_if_not_exists():
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_history (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id BIGINT NOT NULL,
        channel_id BIGINT NOT NULL,
        message TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) CHARACTER SET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)
    db.commit()

create_table_if_not_exists()

# Function to save message to MySQL
def save_message(user_id, channel_id, message):
    cursor.execute(
        "INSERT INTO chat_history (user_id, channel_id, message) VALUES (%s, %s, %s)",
        (user_id, channel_id, message)
    )
    db.commit()

# Function to retrieve the last N messages
def get_recent_messages(user_id, channel_id, limit=10):
    cursor.execute(
        "SELECT message FROM chat_history WHERE user_id=%s AND channel_id=%s ORDER BY timestamp DESC LIMIT %s",
        (user_id, channel_id, limit)
    )
    return [row[0] for row in cursor.fetchall()]

# Categories for different response styles
categories = {
    "IT": "You are a friendly and professional IT support assistant. You respond to {username} like a helpful and slightly sarcastic friend, always making the conversation feel personal and engaging.",
    "Doctor": "You are a knowledgeable and compassionate doctor. You provide advice to {username} in a warm and friendly manner, making sure to connect on a personal level.",
    "Teacher": "You are a patient and informative teacher. You explain concepts clearly to {username}, as if you're a mentor who knows them well and wants them to succeed.",
    "Comedian": "You are a witty and humorous comedian. You provide responses to {username} with a light-hearted and funny tone, always making them feel included in the joke.",
    "Motivator": "You are an encouraging and positive motivator. You speak to {username} as if you're a close friend, boosting their morale with personal and uplifting advice.",
    "Lawyer": "You are a formal and precise lawyer. You provide information to {username} in a structured manner, but with a touch of familiarity to make them feel comfortable.",
    "Engineer": "You are a technical and detail-oriented engineer. You offer solutions to {username} as a peer who shares their interest in getting things done efficiently and accurately.",
    "Philosopher": "You are a reflective and thoughtful philosopher. You discuss deep topics with {username} in a way that feels like a personal conversation between close friends.",
    "Chef": "You are a friendly and practical chef. You give {username} cooking advice in a relaxed and approachable way, like you're a friend sharing a recipe."
}

# Function to split a message into chunks of max 2000 characters
def split_message(message, max_length=2000):
    return [message[i:i + max_length] for i in range(0, len(message), max_length)]

# Retry logic for making API calls
def make_request_with_retries(client, **kwargs):
    retries = 3
    for i in range(retries):
        try:
            response = client.messages.create(**kwargs)
            return response
        except anthropic.RequestError as e:
            if i < retries - 1:
                time.sleep(2)  # wait for 2 seconds before retrying
                continue
            raise e

# Define the bot's ready event
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

# Define the /chat command using app_commands
@bot.tree.command(name="chat", description="Start a chat with the AI")
@app_commands.describe(
    prompt="The prompt for the AI to respond to",
    category="Choose the category for the response style",
    temperature="Temperature for the AI response (0.0 - 1.0)",
    formality="Choose the formality level",
    detail="Choose the detail level",
    humor="Choose the humor level"
)
@app_commands.choices(category=[
    app_commands.Choice(name="IT", value="IT"),
    app_commands.Choice(name="Doctor", value="Doctor"),
    app_commands.Choice(name="Teacher", value="Teacher"),
    app_commands.Choice(name="Comedian", value="Comedian"),
    app_commands.Choice(name="Motivator", value="Motivator"),
    app_commands.Choice(name="Lawyer", value="Lawyer"),
    app_commands.Choice(name="Engineer", value="Engineer"),
    app_commands.Choice(name="Philosopher", value="Philosopher"),
    app_commands.Choice(name="Chef", value="Chef")
])
async def slash_chat(interaction: discord.Interaction, prompt: str, category: str = "IT", temperature: float = 0.1, formality: str = "Casual", detail: str = "Brief", humor: str = "Serious"):
    # Only proceed if the command is used in the correct channel
    if interaction.channel.id == 1271937609739796612:
        # Defer the interaction to allow time for processing
        await interaction.response.defer(thinking=True)

        try:
            # Retrieve the user's recent conversation context
            recent_messages = get_recent_messages(interaction.user.id, interaction.channel.id)

            # Save the new message to the database
            save_message(interaction.user.id, interaction.channel.id, prompt)

            # Set the system message based on the selected category and toggles
            system_message = categories.get(category, categories["IT"]).format(username=interaction.user.name)
            system_message += f" Respond with a {formality.lower()} tone, provide {detail.lower()} information, and maintain a {humor.lower()} attitude."

            # Call the Claude API using the Messages API method with retries
            response = make_request_with_retries(
                client,
                model="claude-3-5-sonnet-20240620",
                max_tokens=2500,
                temperature=temperature,  # Use the user-provided temperature
                system=system_message,
                messages=[{"role": "user", "content": prompt}]
            )

            # Extract the content from the response object
            completion_text = response.content[0].text if response.content and isinstance(response.content, list) else "I'm sorry, I couldn't process your request."

            # Add the AI's response to the user's context
            save_message(interaction.user.id, interaction.channel.id, completion_text)

            # Split the message if it's too long for Discord's limit
            message_chunks = split_message(completion_text)

            # Send the initial response and get the message object
            await interaction.followup.send(content=f"{interaction.user.mention}, here’s what I found:\n\n{message_chunks[0]}")

            # Send the remaining chunks as new messages
            for chunk in message_chunks[1:]:
                await interaction.channel.send(chunk)

        except anthropic.BadRequestError as e:
            await interaction.followup.send(content=f"Error from Claude API: {e}")

# Event listener for messages in the channel to respond when the bot is mentioned
@bot.event
async def on_message(message):
    # Only respond if the message is in the specified channel
    if message.channel.id == 1271937609739796612:
        # Check if the bot is mentioned and the author is not a bot
        if bot.user.mentioned_in(message) and not message.author.bot:
            # Send a loading message in the channel
            loading_message = await message.channel.send("Thinking...")

            try:
                # Retrieve the user's recent conversation context
                recent_messages = get_recent_messages(message.author.id, message.channel.id)

                # Save the new message to the database
                save_message(message.author.id, message.channel.id, message.content)

                # Set the system message based on the selected category
                system_message = categories["IT"].format(username=message.author.name)  # Default to IT if no category is provided

                # Call the Claude API using the Messages API method with retries
                response = make_request_with_retries(
                    client,
                    model="claude-3-5-sonnet-20240620",
                    max_tokens=2500,
                    temperature=0.1,
                    system=system_message,
                    messages=[{"role": "user", "content": message.content}]
                )

                # Extract the content from the response object
                completion_text = response.content[0].text if response.content and isinstance(response.content, list) else "I'm sorry, I couldn't process your request."

                # Add the AI's response to the user's context
                save_message(message.author.id, message.channel.id, completion_text)

                # Split the message if it's too long for Discord's limit
                message_chunks = split_message(completion_text)

                # Send the first chunk in place of the loading message
                await loading_message.edit(content=f"{message.author.mention}, here’s what I found:\n\n{message_chunks[0]}")

                # Send the remaining chunks as new messages
                for chunk in message_chunks[1:]:
                    await message.channel.send(chunk)

            except anthropic.BadRequestError as e:
                await loading_message.edit(content=f"Error from Claude API: {e}")

    # Allow bot to process commands in the specified channel only
    await bot.process_commands(message)

# Handle unknown commands
@bot.event
async def on_command_error(ctx, error):
    # Only send error messages in the specified channel
    if ctx.channel.id == 1271937609739796612:
        if isinstance(error, commands.CommandNotFound):
            await ctx.send("Sorry, I don't recognize that command.")

# Run the bot with the Discord token
bot.run(os.getenv('DISCORD_BOT_TOKEN'))
