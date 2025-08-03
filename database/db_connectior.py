import sqlite3
import mysql.connector
from mysql.connector import Error

# Keys map

keys_map = {
	'master_id': 'Никнейм мастера',
	'game_name': 'Название игры',
	'players_count': 'Количество игроков',
	'system_name': 'Система',
	'setting': 'Сеттинг',
	'game_type': 'Тип игры',
	'game_time': 'Время',
	'cost': 'Стоимость',
	'experience': 'Опыт игроков',
	'free_text': '\nОписание',
	'image_url': 'Картинка',
}

players_keys = {
	'player_name': 'Имя игрока',
	'contact': 'Способ связи',
	'game_type': 'Тип игры',
	'system_name': 'Сеттинг',
	'game_time': 'Предпочтительное время',
	'price': 'Предпочтительный прайс',
	'free_text': '\nПожелания'
}


class DBConnector:
	def __init__(self, host: str, port: int, user: str, password: str, database: str):
		self.host = host
		self.port = port
		self.user = user
		self.password = password
		self.database = database

	def get_connection(self) -> sqlite3.Connection:
		conn = mysql.connector.connect(
			host=self.host,
			port=self.port,
			user=self.user,
			password=self.password,
			database=self.database
		)
		return conn

	def execute_query(self, query: str, params: tuple = None):
		"""
		Executes a query against the MySQL database.

		Args:
			query (str): The SQL query to execute.
			params (tuple, optional): Parameters to use with the query.

		Returns:
			list: Rows for SELECT queries, empty list otherwise.
		"""
		conn = self.get_connection()
		cursor = conn.cursor()

		if params is None:
			params = ()

		try:
			cursor.execute(query, params)

			if query.strip().upper().startswith('SELECT'):
				results = cursor.fetchall()
				print(results)
			else:
				conn.commit()
				results = []

		except Error as e:
			print(f"An error occurred: {e}")
			results = []

		finally:
			cursor.close()
			conn.close()

		return results


from config import db_password, db_user, db_host, db_port, db_name

db = DBConnector(
	host=db_host, port=db_port, user=db_user, password=db_password, database=db_name
)
