import hashlib
import datetime
import os
import traceback

from telegram import InlineKeyboardMarkup
from google.cloud import storage




def build_keyboard(button, n_per_row=2):
    return InlineKeyboardMarkup(
        [button[i:i + n_per_row] for i in range(0, len(button), n_per_row)]
    )


def generate_id(data_to_hash: list) -> str:
    combined = ','.join(data_to_hash)
    hash_object = hashlib.sha256(combined.encode('utf-8'))
    return hash_object.hexdigest()



def get_game_announcement() -> list:
    # Query to get games of the selected type from the database
    query = """
            SELECT master_id, game_name, players_count, system_name, setting, game_type, game_time, cost, experience, free_text, image_url FROM games
            """
    # Execute a request with the selected game type parameter
    result = db.execute_query(query)
    list_player = []
    # Generating a list of games to display to the user
    for game in result:
        temp_string = ''
        for i, key in enumerate(keys_map):

            if key != 'image_url':
                if key == 'master_id':
                    temp_string += keys_map[key] + ': ' + '@' + str(game[i]) + '\n'
                else:
                    temp_string += keys_map[key] + ': ' + str(game[i]) + '\n'
            else:
                image_url = game[i]
        list_player.append((temp_string, image_url))
    print(result)
    # Sending a list of available games to the user
    # Ending the dialogue
    return list_player



def write_exception_to_local_file(path='/logs/error.log'):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tb = traceback.format_exc()  # full traceback as a string
    log_entry = f"""
######################################
\n{now} - Exception occurred:\n{tb}
######################################
    """
    if path:
        with open(path, "a") as f:
            f.write(log_entry)



def upload_image_to_bucket(path):
    bucket_name = 'roc_images'
    project_id = 'articulate-bird-464515-n5'
    client = storage.Client(project=project_id)

    bucket = client.bucket(bucket_name)
    blob = bucket.blob(path)
    blob.upload_from_filename(path)

    os.remove(path)


def load_from_bucket(blob_name):
    bucket_name = 'roc_images'
    project_id = 'articulate-bird-464515-n5'
    client = storage.Client(project=project_id)

    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.download_to_filename(blob_name)
    return blob_name


def delete_from_bucket(blob_name):
    bucket_name = 'roc_images'
    project_id = 'articulate-bird-464515-n5'
    client = storage.Client(project=project_id)

    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.delete()
