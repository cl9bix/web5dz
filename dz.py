import aiohttp
import asyncio
import datetime
import json
import sys


class CurrencyRatesFetcher:
    API_URL = 'https://api.privatbank.ua/p24api/exchange_rates'

    async def fetch_currency_rates(self, date):
        async with aiohttp.ClientSession() as session:
            params = {'json': '', 'date': date}
            async with session.get(self.API_URL, params=params) as response:
                return await response.json()

    def get_formatted_currency_rates(self, rates):
        formatted_rates = []
        for rate in rates:
            date = rate['date']
            eur_sale = next((r['sale'] for r in rate['exchangeRate'] if r['currency'] == 'EUR'), None)
            eur_purchase = next((r['purchase'] for r in rate['exchangeRate'] if r['currency'] == 'EUR'), None)
            usd_sale = next((r['sale'] for r in rate['exchangeRate'] if r['currency'] == 'USD'), None)
            usd_purchase = next((r['purchase'] for r in rate['exchangeRate'] if r['currency'] == 'USD'), None)

            formatted_rate = {
                date: {
                    'EUR': {'sale': eur_sale, 'purchase': eur_purchase},
                    'USD': {'sale': usd_sale, 'purchase': usd_purchase}
                }
            }
            formatted_rates.append(formatted_rate)

        return formatted_rates


async def main():
    if len(sys.argv) != 2:
        print('Usage: python main.py <days>')
        return

    try:
        days = int(sys.argv[1])
        if days > 10:
            raise ValueError('Number of days should not exceed 10.')
    except ValueError as e:
        print(f'Invalid input: {str(e)}')
        return

    today = datetime.date.today()
    dates = [str(today - datetime.timedelta(days=i)) for i in range(days)]

    fetcher = CurrencyRatesFetcher()
    tasks = [fetcher.fetch_currency_rates(date) for date in dates]
    results = await asyncio.gather(*tasks)

    formatted_rates = fetcher.get_formatted_currency_rates(results)
    print(json.dumps(formatted_rates, indent=2))


if __name__ == '__main__':
    asyncio.run(main())
