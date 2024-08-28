import sqlite3


class DBConnector:
    def __init__(self, connection_string: str = 'example.db'):
        self.connection_string = connection_string

    def get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.connection_string)

    def execute_query(self, query: str, params: tuple = None):
        """
        Executes a query against the database.

        Args:
            query (str): The SQL query to execute.
            params (tuple, optional): The parameters to use with the query.

        Returns:
            list: If the query is a SELECT statement, returns a list of rows.
                  For other queries (INSERT, UPDATE, DELETE), returns an empty list.
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        if params is None:
            params = ()

        try:
            cursor.execute(query, params)

            if query.strip().upper().startswith('SELECT'):
                # Fetch all results if it's a SELECT query
                results = cursor.fetchall()
            else:
                # Commit changes if it's an INSERT, UPDATE, or DELETE query
                conn.commit()
                results = []

        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            results = []

        finally:
            # Close the connection
            conn.close()

        return results
