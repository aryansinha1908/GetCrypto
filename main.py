import os
import discord
import asyncio
import functools
import requests
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("token")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
coins = requests.get("https://api.coingecko.com/api/v3/coins/list")


def get_price(symbol):
    symbol = symbol.lower()
    response = requests.get(f"https://api.coingecko.com/api/v3/search?query={symbol}")
    data = response.json()

    symbol = symbol.upper()
    for coin in data["coins"]:
        if coin["symbol"] == symbol:
            coin_id = coin["id"]
            break

    response = requests.get(
        f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd",
        {},
    )
    data = response.json()

    return data[coin_id]["usd"]


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("!hello"):
        await message.channel.send("Hello Bro")

    if message.content.startswith("!price"):
        parts = message.content.split()

        if len(parts) < 2:
            await message.channel.send("Please provide a symbol")

        symbol = parts[1]

        loop = asyncio.get_event_loop()
        price = await loop.run_in_executor(None, functools.partial(get_price, symbol))

        if price:
            await message.channel.send(
                f"The price of {symbol.upper()} is ${price:,.2f}."
            )
        else:
            await message.channel.send("Invalid Coin or API Error")


client.run(TOKEN)
