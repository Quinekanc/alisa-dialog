import os
import random
from flask import Flask, request
import logging
import json
from geo import get_country, get_distance, get_coordinates

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, filename='app.log',
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')

cities_id = {
    'москва': ['997614/56ad30efbc03beed9291',
               '1533899/f079b042fa8e49586e3d'],
    'нью-йорк': ['213044/d09dfd821c8924149fee',
                 '1533899/33d7d09de5e0ade4b1a4'],
    'париж': ['1030494/25b8adb1ceca2ea236b3',
              '1521359/5c5d4ee1417a38f22759']
}


@app.route('/')
def default():
    return 'Сайт работает'


@app.route('/post', methods=['POST'])
def main():
    logging.info('Request: %r', request.json)
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    handle_dialog(response, request.json)
    logging.info('Request: %r', response)
    return json.dumps(response)


def handle_dialog(res, req):
    user_id = req['session']['user_id']
    if req['session']['new']:
        res['response']['text'] = \
            'Привет! Я могу показать город или сказать расстояние между городами!'
        return
    cities = get_cities(req)
    if not cities:
        res['response']['text'] = 'Ты не написал название не одного города!'
    elif len(cities) == 1:
        if cities[0] in ['москва', 'нью-йорк', 'париж']:
            res['response']['text'] = 'Этот город в стране - ' + get_country(cities[0])
            res['response']['card'] = {}
            res['response']['card']['type'] = 'BigImage'
            res['response']['card']['title'] = 'Этот город в стране - ' + get_country(cities[0])
            res['response']['card']['image_id'] = random.choice(cities_id[cities[0]])

        else:
            res['response']['text'] = 'Этот город в стране - ' + get_country(cities[0])

    elif len(cities) == 2:
        distance = get_distance(get_coordinates(
            cities[0]), get_coordinates(cities[1]))
        res['response']['text'] = 'Расстояние между этими городами: ' + \
                                  str(round(distance)) + ' км.'
    else:
        res['response']['text'] = 'Слишком много городов!'


def get_cities(req):
    cities = []
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.GEO':
            if 'city' in entity['value']:
                cities.append(entity['value']['city'])
    return cities


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
