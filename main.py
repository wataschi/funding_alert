import json
import logging
import time
import telebot
import requests as r


from datetime import datetime
from plyer import notification

funding = 0.2
minutes_revision = 30
list_exchange =['Binance']

# telegram_id
bot = telebot.TeleBot("6450084533:AAHK7z2H6TLl2vfzWo-7xXSxdG2HNuUcpIs")
ID = 568690953

logging.basicConfig(
    format='[%(asctime)s %(levelname)s] %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')


def bot_message(text) -> None:
    bot.send_message(ID, text)


def get_funding():

    url = "https://open-api.coinglass.com/public/v2/funding"

    headers = {
        "accept": "application/json",
        "coinglassSecret": "95f8083f7a6b4c949247e43861994b08"
    }

    response = r.get(url, headers=headers)
    return response


def send_message(title, message):
    notification.notify(title=title, message=message, app_icon='favicon.ico', timeout=10)


def convert_funding_date(next_funding_time):
    format_date = '%H:%M:%S'

    formatNextFundingTime = 'NO INFORMATION'
    if next_funding_time is not None:
        next_time = datetime.fromtimestamp(next_funding_time / 1000)
        formatNextFundingTime = next_time.strftime(format_date)
    return formatNextFundingTime

# def time_left(funding_time):
#     currentH, currentM, currentS = datetime.now().strftime('%H:%M:%S').split(":")
#     nextH, nextM, nextS = funding_time.split(":")
#
#     defi_h = int(nextH) - int(currentH)
#     defi_m = int(nextM) - int(currentM)
#     defi_s = int(nextS) - int(currentS)
#     print(f"{defi_h} : {defi_m} : {defi_s}")


def get_symbols(exchange_list, funding_fee):
    inside = False
    response = get_funding()
    json_response = json.loads(response.text)

    symbol_rates = []
    for item in json_response['data']:
        symbol = item['symbol']

        filter_rates = [margin for margin in item['uMarginList']
                        if margin['exchangeName'] in exchange_list and 'rate' in margin]

        for exchange in filter_rates:
            nextFundingTime = exchange.get('nextFundingTime')

            symbol_rate = {
                'symbol': symbol,
                'exchange': str.upper(exchange['exchangeName']),
                'rate': exchange['rate'],
                'nextFundingTime': nextFundingTime
            }

            symbol_rates.append(symbol_rate)

    funding_positive = [
        item for item in symbol_rates if item['rate'] >= funding_fee]

    funding_negative = [
        item for item in symbol_rates if item['rate'] <= (funding_fee * -1)]

    if len(funding_positive) > 0:
        inside = True
        logging.info(f'=========================[Оплата шортів]=============================')
        bot_message(f"=========[Оплата шортів]========= \n=====Поточний час: {datetime.now().strftime('%H:%M:%S')}====")
        for item in sorted(funding_positive, key=lambda x: x['rate'], reverse=True):
            formatNextFundingTime = convert_funding_date(item['nextFundingTime'])
            logging.info(f"Біржа: {item['exchange']}, Токен: {item['symbol']}, Ставка: {item['rate']}, Дата: {formatNextFundingTime}")
            bot_message(f"\nЧас фандингу: {formatNextFundingTime} \nБіржа: {item['exchange']}, Токен: {item['symbol']} \nСтавка: {item['rate']},\n")

    if len(funding_negative) > 0:
        inside = True
        logging.info(f'=========================[Оплата лонгів]=============================')
        bot_message(f"=========[Оплата лонгів]========= \n======[Поточний час: {datetime.now().strftime('%H:%M:%S')}]=====")
        for item in sorted(funding_negative, key=lambda x: x['rate']):
            formatNextFundingTime = convert_funding_date(item['nextFundingTime'])
            logging.info(f"Біржа: {item['exchange']}, Токен: {item['symbol']}, Ставка: {item['rate']}, Дата: {formatNextFundingTime}")
            bot_message(f"\nЧас фандингу: {formatNextFundingTime} \nБіржа: {item['exchange']}, Токен: {item['symbol']} \nСтавка: {item['rate']}\n")

    if not inside:
        logging.info(f'Нічого не знайдено...')


if __name__ == '__main__':
    funding_fee = float(funding)
    time_out = int(minutes_revision) * 60

    exchange_list = list_exchange

    while True:
        try:
            get_symbols(exchange_list, funding_fee)
            time.sleep(time_out)
        except KeyboardInterrupt:
            break
        except Exception as ex:
            logging.error(ex)
            pass
