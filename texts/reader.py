import json


def read_texts(file_name):
    with open(file_name, 'r', encoding='utf-8') as file:
        return json.load(file)