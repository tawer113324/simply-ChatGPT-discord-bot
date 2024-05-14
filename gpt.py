import disnake
from disnake.ext import commands
import openai
from openai import OpenAI
from openai import AsyncOpenAI
import random

OPENAI_API_KEY = ''

client = AsyncOpenAI(api_key=(OPENAI_API_KEY))

bot = commands.Bot(command_prefix='!', intents=disnake.Intents.all())

INITIAL_PROMPT = ""

bot_settings = {
    "respond_chance": 0.2,
    "active": True
}

last_messages = {}
last_bot_message = {}

def update_message_history(channel_id, message, is_bot=False):
    if channel_id not in last_messages:
        last_messages[channel_id] = []
    if len(last_messages[channel_id]) > 50:
        last_messages[channel_id].pop(0)
    last_messages[channel_id].append(message)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} (ID: {bot.user.id})')

@bot.slash_command(description="Установить шанс ответа бота")
async def set_chance(inter, chance: float):
    bot_settings["respond_chance"] = chance
    await inter.response.send_message(f"Шанс ответа бота установлен на {chance:.0%}")

@bot.slash_command(description="Включить или отключить бота")
async def toggle_bot(inter):
    bot_settings["active"] = not bot_settings["active"]
    state = "активирован" if bot_settings["active"] else "деактивирован"
    await inter.response.send_message(f"Бот теперь {state}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if not bot_settings["active"]:
        return

    update_message_history(message.channel.id, message.content)

    if random.random() < bot_settings["respond_chance"] or bot.user in message.mentions:
        await message.channel.trigger_typing()

        history = "\n".join(last_messages[message.channel.id])
        prompt = f"{INITIAL_PROMPT}\n{history}\n{message.content}"

        response = await client.chat.completions.create(
            messages=[{"role": "system", "content": prompt}],
            model="gpt-4o",
            max_tokens=500,
        )
        reply = response.choices[0].message.content
        last_bot_message[message.channel.id] = reply
        update_message_history(message.channel.id, reply, is_bot=True)
        await message.reply(reply)
    else:
        return


bot.run('')
