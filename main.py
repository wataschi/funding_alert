import json
import logging
import time
import requests as r

from datetime import datetime
from plyer import notification

from common.utils import Utils

logging.basicConfig(
    format='[%(asctime)s %(levelname)s] %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')


def obtener_funding():
    config = Utils.read_config()
    url = config['configuracion']['coinglass_url']
    api_key = config['configuracion']['coinglass_apikey']

    url = "https://open-api.coinglass.com/public/v2/funding"

    headers = {
        "accept": "application/json",
        "coinglassSecret": api_key
    }

    response = r.get(url, headers=headers)
    return response

def enviar_mensaje(titulo, mensaje):
    notification.notify(title=titulo, message=mensaje, app_icon='favicon.ico', timeout=10)


def convertir_fecha_funding(next_funding_time):
    formato_fecha = '%Y-%m-%d %H:%M:%S'

    falta = ''
    formatNextFundingTime = 'NO INFORMA'
    if not next_funding_time is None:
        next_time = datetime.fromtimestamp(next_funding_time / 1000)
        formatNextFundingTime = next_time.strftime(formato_fecha)
        falta = cuanto_falta(next_time)
    return formatNextFundingTime, falta


def cuanto_falta(next_time):
    # Obtener la hora actual
    hora_actual = datetime.now()

    # Calcular la diferencia entre la hora actual y 'nextTime'
    diferencia = next_time - hora_actual

    # Extraer la diferencia en horas, minutos y segundos
    horas = diferencia.seconds // 3600
    minutos = (diferencia.seconds // 60) % 60
    segundos = diferencia.seconds % 60

    return f'{horas}h {minutos}m {segundos}s'


def obtener_symbols(exchange_list, funding_fee):
    entro = False
    # Obtiene de la api los funding
    response = obtener_funding()
    json_response = json.loads(response.text)

    symbol_rates = []
    for item in json_response['data']:
        symbol = item['symbol']

        # Filta los exchange que usamos
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

    # Filtra los que el funding es mayor a la variable funding_fee
    funding_positivos = [
        item for item in symbol_rates if item['rate'] >= funding_fee]

    funding_negativos = [
        item for item in symbol_rates if item['rate'] <= (funding_fee * -1)]

    # Imprime si tiene registros para short
    if len(funding_positivos) > 0:
        entro = True
        logging.info(f'[PAGANDO SHORTs] ======================================================')
        for item in sorted(funding_positivos, key=lambda x: x['rate'], reverse=True):
            formatNextFundingTime, falta = convertir_fecha_funding(
                item['nextFundingTime'])
            logging.info(
                f"EXCHANGE: {item['exchange']}, SYMBOL: {item['symbol']}, RATE: {item['rate']}, FECHA: {formatNextFundingTime}, FALTA: {falta}")
            enviar_mensaje(f"{item['exchange']} [PAGANDO SHORTs]", f"SYMBOL: {item['symbol']}, RATE: {item['rate']}")

    # Imprime si tiene registros para long
    if len(funding_negativos) > 0:
        entro = True
        logging.info(f'[PAGANDO LONGs] ======================================================')
        for item in sorted(funding_negativos, key=lambda x: x['rate']):
            formatNextFundingTime, falta = convertir_fecha_funding(
                item['nextFundingTime'])
            logging.info(
                f"EXCHANGE: {item['exchange']}, SYMBOL: {item['symbol']}, RATE: {item['rate']}, FECHA: {formatNextFundingTime}, FALTA: {falta}")
            enviar_mensaje(f"{item['exchange']} [PAGANDO LONGs]", f"SYMBOL: {item['symbol']}, RATE: {item['rate']}")
            
    if not entro:
        logging.info(f'No se encontraron resultados...')


if __name__ == '__main__':
    config = Utils.read_config()
    funding_fee = float(config['configuracion']['funding'])
    descanso = int(config['configuracion']['minutos_revision']) * 60

    # Los exchanges que se utilizan
    exchange_list = ['Binance', 'Bybit', 'OKX', 'Bitget']

    while True:
        try:
            # Busca que fundings hay
            obtener_symbols(exchange_list, funding_fee)

            # Descansa cinco minutos
            time.sleep(descanso)
        except KeyboardInterrupt:
            break
        except Exception as ex:
            logging.error(ex)
            pass

    
