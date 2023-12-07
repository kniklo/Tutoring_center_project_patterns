import aiomysql


class Singleton:


    def __init__(self):
        self.connection = None

    async def connect_to_database(self):
        connection = await aiomysql.connect(
            host="localhost",
            user="root",
            password="12345678",
            db="tutor")
        return connection

    async def close_connection(self):
        self.connection.close()