import sys
import asyncio
import aiohttp
from datetime import datetime, timedelta


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


async def main():
    if len(sys.argv) < 2:
        print("Please provide the number of days as a command line argument.")
        return
    try:
        days = int(sys.argv[1])
        if days < 1 or days > 10:
            print("Number of days should be between 1 and 10.")
            return
    except ValueError:
        print("Invalid number of days.")
        return

    try:
        rates = await get_exchange_rates(days)
        print(rates)
    except aiohttp.ClientError as e:
        print("An error occurred during the HTTP request:", str(e))


if __name__ == "__main__":
    asyncio.run(main())
