class Table:
    def __init__(self, table_name):
        self.table_name = table_name

class Game(Table):
    def __init__(self, player_count, system, setting, game_type, time, cost, experience, free_text, master_is):
        super().__init__('games')
        self.player_count = player_count
        self.system = system
        self.setting = setting
        self.game_type = game_type
        self.time = time
        self.cost = cost
        self.experience = experience
        self.free_text = free_text
        self.master_is = master_is


class Master(Table):
    def __init__(self, telegram_name, master_name):
        super().__init__('masters')
        self.player_count = telegram_name
        self.system = master_name

