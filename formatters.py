from database.db_connectior import keys_map, players_keys

# def format_game_for_master_view(game_tuple: tuple, keys: list) -> (str, str | None):
#     """Formats game details for the master who owns it."""
#     # The query for this view doesn't include master_id or game_id in the result set.
#     keys = [
#         'game_name', 'players_count', 'system_name', 'setting', 'game_type',
#         'game_time', 'cost', 'experience', 'free_text', 'image_url'
#     ]
#     temp_string = ''
#     image_url = None
#     for i, key in enumerate(keys):
#         if key == 'image_url':
#             image_url = game_tuple[i]
#         else:
#             temp_string += f"{keys_map[key]}: {str(game_tuple[i])}\n"
#     return temp_string, image_url


def format_game_for_view(game_tuple: tuple, game_keys: list) -> (str, str | None):
    """Formats game details for any player to view."""
    temp_string = ''
    image_url = None
    for i, key in enumerate(game_keys):
        value = game_tuple[i]
        if key == 'image_url':
            image_url = value
        elif key == 'master_id':
            temp_string += f"{keys_map[key]}: @{str(value)}\n"
        else:
            temp_string += f"{keys_map[key]}: {str(value)}\n"
    return temp_string, image_url
