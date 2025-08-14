import requests
import csv
import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
NAME_MAP_FILE = os.path.join(DATA_DIR, "name_map.csv")
TRAINING_LOGS_FILE = os.path.join(DATA_DIR, "training_logs.csv")

def load_name_mapping():
    mapping = {}
    if not os.path.isfile(NAME_MAP_FILE):
        return mapping
    try:
        with open(NAME_MAP_FILE, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                if len(row) == 2:
                    japanese_name, english_name = row
                    mapping[japanese_name] = english_name
        return mapping
    except FileNotFoundError:
        return {}

name_map = load_name_mapping()
english_map = {v.lower(): k for k, v in name_map.items()}

def convert_name(user_input):
    if user_input.isdigit():
        return user_input
    if user_input in name_map:
        return name_map[user_input].lower()
    return user_input.lower()

def get_pokemon_data(name_or_id):
    url = f"https://pokeapi.co/api/v2/pokemon/{name_or_id}"
    res = requests.get(url)
    if res.status_code != 200:
        return None
    data = res.json()
    english_name = data["name"]
    japanese_name = english_map.get(english_name, english_name.capitalize())
    pokemon_info = {
        "name": english_name,
        "japanese_name": japanese_name,
        "image": data["sprites"]["front_default"],
        "types": [t["type"]["name"].capitalize() for t in data["types"]],
        "stats": {s["stat"]["name"].capitalize(): s["base_stat"] for s in data["stats"]}
    }
    return pokemon_info

def generate_rotom_comment(pokemon_info):
    comment_template = "⚡ {japanese_name}！タイプは {types} だぞ！⚡"
    types_str = "、".join(pokemon_info["types"])
    return comment_template.format(japanese_name=pokemon_info["japanese_name"], types=types_str)

def save_training_log(pokemon_info, evs, memo):
    os.makedirs(DATA_DIR, exist_ok=True)
    is_empty = not os.path.isfile(TRAINING_LOGS_FILE) or os.stat(TRAINING_LOGS_FILE).st_size == 0
    with open(TRAINING_LOGS_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if is_empty:
            writer.writerow(["japanese_name", "types", "image", "evs", "memo"])
        evs_json = json.dumps(evs, ensure_ascii=False)
        writer.writerow([
            pokemon_info["japanese_name"],
            "/".join(pokemon_info["types"]),
            pokemon_info["image"],
            evs_json,
            memo
        ])
    return True

def load_training_logs():
    if not os.path.isfile(TRAINING_LOGS_FILE) or os.stat(TRAINING_LOGS_FILE).st_size == 0:
        return []
    try:
        with open(TRAINING_LOGS_FILE, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return list(reader)
    except (FileNotFoundError, csv.Error):
        return []