import sys
import asyncio
import aiohttp
from datetime import datetime, timedelta
import aiofiles
import aiohttp
import aiopath


async def get_exchange_rates(days):
    url = 'https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response.raise_for_status()
            data = await response.json()
            rates = []
            today = datetime.now().strftime('%d.%m.%Y')
            for _ in range(days):
                daily_rates = {}
                for rate in data:
                    if rate['ccy'] in ['USD', 'EUR']:
                        currency = rate['ccy']
                        daily_rates[currency] = {
                            'sale': rate['sale'],
                            'purchase': rate['buy']
                        }
                rates.append({today: daily_rates})
                today = (datetime.strptime(today, '%d.%m.%Y') -
                         timedelta(days=1)).strftime('%d.%m.%Y')
            return rates


async def handle_exchange_command(command):
    parts = command.split()
    if len(parts) < 2:
        return "Please provide the number of days as an argument for the 'exchange' command."
    try:
        days = int(parts[1])
        if days < 1 or days > 10:
            return "Number of days should be between 1 and 10."
    except ValueError:
        return "Invalid number of days."

    try:
        rates = await get_exchange_rates(days)
        return rates
    except aiohttp.ClientError as e:
        return f"An error occurred during the HTTP request: {str(e)}"


async def log_command(command):
    log_path = aiopath.Path("chat_log.txt")
    async with aiofiles.open(log_path, mode="a") as file:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"{timestamp}: {command}\n"
        await file.write(log_line)


async def handle_chat_message(message):
    if message.startswith("exchange"):
        response = await handle_exchange_command(message)
        await log_command(message)
    else:
        response = "Unknown command."
    return response


async def chat_client():
    url = "ws://localhost:8000/chat"
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect(url) as ws:
            print("Connected to chat server.")
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    message = msg.data.strip()
                    print(f"Received message from chat server: {message}")
                    response = await handle_chat_message(message)
                    await ws.send_str(response)
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    print("Error during WebSocket communication:", ws.exception())
                    break


async def main():
    await chat_client()


if __name__ == "__main__":
    asyncio.run(main())
