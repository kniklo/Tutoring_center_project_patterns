import aiomysql
from observers import Observer, RequestObserver, ObserverSubject, ConcreteObserverSubject


# Класс Singleton для подключения к базе данных
class SingletonDatabaseConnection:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SingletonDatabaseConnection, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.connection = None

    async def connect(self):
        self.connection = await aiomysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='12345678',
            db='tutor',
        )

    async def close(self):
        if self.connection:
            self.connection.close()
            await self.connection.wait_closed()

# Класс фабрики для создания объектов доступа к данным
class DAOFactory:
    def create_dao(self):
        raise NotImplementedError()


# Конкретная фабрика для создания объектов доступа к данным MySQL
class MySQLDAOFactory(DAOFactory):
    def create_dao(self):
        return DAO()


class DAO:

    def __init__(self):
        self.concrete_os = ConcreteObserverSubject()
        self.observer1 = RequestObserver('Observer 1')
        self.concrete_os.add_observer(self.observer1)

    @staticmethod
    async def connect_to_database():
        connection = await aiomysql.connect(
            host="localhost",
            user="root",
            password="12345678",
            db="tutor")
        return connection

    async def get_repetitors(self):
        connection = await self.connect_to_database()
        cursor = await connection.cursor()
        sql = "SELECT user.name FROM repetitor JOIN user ON repetitor.user_id = user.id"
        values = []
        await cursor.execute(sql, values)
        repetitors = await cursor.fetchall()
        await cursor.close()
        connection.close()
        return repetitors

    async def add_query(self, user_id, subject_id, theme, qtext):
        connection = await self.connect_to_database()
        cursor = await connection.cursor()
        sql = "INSERT INTO query (user_id, subject_id, theme, text) VALUES (%s, %s, %s, %s)"
        values = (user_id, subject_id, theme, qtext)
        await cursor.execute(sql, values)

        query_id = cursor.lastrowid
        status_id = 0

        sql = "INSERT INTO request (query_id, status_id, time) VALUES (%s, %s, NOW())"
        values = [query_id, status_id]
        await cursor.execute(sql, values)
        await connection.commit()
        await cursor.close()
        connection.close()

    async def accept_request(self, user_id, request_id):
        connection = await self.connect_to_database()
        cursor = await connection.cursor()
        sql = "UPDATE request SET status_id = 1, time = NOW(), repetitor_id = %s WHERE id = %s"
        values = [user_id, request_id]
        await cursor.execute(sql, values)
        await connection.commit()
        sql = "SELECT name, email FROM user WHERE id = %s"
        values = [user_id]
        await cursor.execute(sql, values)
        user = await cursor.fetchone()
        await cursor.close()
        connection.close()
        self.concrete_os.set_status(user, 1)

    async def confirm_request(self, user_id, request_id):
        connection = await self.connect_to_database()
        cursor = await connection.cursor()
        sql = "UPDATE request SET status_id = 2, time = NOW() WHERE id = %s"
        values = [request_id]
        await cursor.execute(sql, values)
        await connection.commit()
        sql = "SELECT name, email FROM user WHERE id = %s"
        values = [user_id]
        await cursor.execute(sql, values)
        user = await cursor.fetchone()
        await cursor.close()
        connection.close()
        self.concrete_os.set_status(user, 2)

    async def finish_request(self, request_id):
        connection = await self.connect_to_database()
        cursor = await connection.cursor()
        sql = "UPDATE request SET status_id = 3, time = NOW() WHERE id = %s"
        values = [request_id]
        await cursor.execute(sql, values)
        await connection.commit()
        await cursor.close()
        connection.close()

    async def get_tutorrequestlist(self, status_id, user_id):
        connection = await self.connect_to_database()
        cursor = await connection.cursor()
        sql = "SELECT " \
              "request.id, " \
              "subject.name, " \
              "query.theme, " \
              "request.status_id, " \
              "request.time " \
              "FROM query JOIN request ON query.id = request.query_id " \
              "JOIN subject ON query.subject_id = subject.id " \
              "WHERE request.status_id = %s AND " \
              "subject_id IN (SELECT subject_id FROM repetitor_subject WHERE user_id = %s)"
        values = [status_id, user_id]
        await cursor.execute(sql, values)
        querylist1 = list(await cursor.fetchall())
        sql = "SELECT " \
              "request.id, " \
              "subject.name, " \
              "query.theme, " \
              "request.status_id, " \
              "request.time " \
              "FROM query JOIN request ON query.id = request.query_id " \
              "JOIN subject ON query.subject_id = subject.id " \
              "WHERE request.repetitor_id = %s"
        values = [user_id]
        await cursor.execute(sql, values)
        querylist2 = list(await cursor.fetchall())
        await cursor.close()
        connection.close()
        return querylist1, querylist2

    async def get_clientrequestlist(self, user_id):
        connection = await self.connect_to_database()
        cursor = await connection.cursor()
        sql = "SELECT " \
              "request.id, " \
              "subject.name, " \
              "query.theme, " \
              "request.status_id, " \
              "request.time " \
              "FROM query JOIN request ON query.id = request.query_id " \
              "JOIN subject ON query.subject_id = subject.id " \
              "WHERE query.user_id = %s"

        values = [user_id]
        await cursor.execute(sql, values)
        querylist = list(await cursor.fetchall())
        await cursor.close()
        connection.close()
        return querylist

    async def get_request_details(self, request_id):
        connection = await self.connect_to_database()
        cursor = await connection.cursor()
        sql = "SELECT subject.name, " \
              "query.theme, " \
              "query.text, " \
              "request.status_id " \
              "FROM query " \
              "JOIN request ON request.query_id = query.id " \
              "JOIN subject ON query.subject_id = subject.id " \
              "WHERE request.id = %s"
        values = [request_id]
        await cursor.execute(sql, values)
        query = await cursor.fetchone()
        await cursor.close()
        connection.close()
        return query

    async def register_client(self, user):
        connection = await self.connect_to_database()
        cursor = await connection.cursor()
        sql = "INSERT INTO user (login, password, usertype, name, email) VALUES (%s, %s, %s, %s, %s)"
        values = (user.login, user.password, 2, user.name, user.email)
        await cursor.execute(sql, values)
        userid = cursor.lastrowid
        sql = "INSERT INTO client (user_id) VALUES (%s)"
        values = [userid]
        await cursor.execute(sql, values)
        await connection.commit()
        await cursor.close()
        connection.close()

    async def register_tutor(self, user):
        connection = await self.connect_to_database()
        cursor = await connection.cursor()
        sql = "INSERT INTO user (login, password, usertype, name, email) VALUES (%s, %s, %s, %s, %s)"
        values = (user.login, user.password, 1, user.name, user.email)
        await cursor.execute(sql, values)
        userid = cursor.lastrowid
        sql = "INSERT INTO repetitor (user_id, indeal, hourly_rate) VALUES (%s, %s, %s)"
        values = [userid, 1, 0]
        await cursor.execute(sql, values)
        await connection.commit()
        await cursor.close()
        connection.close()

    async def login(self, login, password):
        connection = await self.connect_to_database()
        cursor = await connection.cursor()
        sql = "SELECT id, login, usertype, name FROM user WHERE login = %s AND password = %s"
        values = (login, password)
        await cursor.execute(sql, values)
        user = await cursor.fetchone()
        await cursor.close()
        connection.close()
        return user

    async def personal_tutor_get(self, user_id):
        connection = await self.connect_to_database()
        cursor = await connection.cursor()
        sql = "SELECT user.login, user.name, user.email, repetitor.hourly_rate FROM user JOIN repetitor ON user.id = repetitor.user_id WHERE user.id = %s"
        values = [user_id]
        await cursor.execute(sql, values)
        userdata = await cursor.fetchone()

        sql = "SELECT subject.id, subject.name FROM repetitor_subject JOIN subject ON repetitor_subject.subject_id = subject.id WHERE repetitor_subject.user_id = %s"
        values = [user_id]
        await cursor.execute(sql, values)
        subjects = set(sorted(list(await cursor.fetchall())))

        sql = "SELECT id, name FROM subject"
        await cursor.execute(sql)
        allsubjects = set(sorted(list(await cursor.fetchall()))).difference(subjects)

        await cursor.close()
        connection.close()
        return userdata, subjects, allsubjects

    async def personal_tutor_post(self, repetitor, user_id):
        connection = await self.connect_to_database()
        cursor = await connection.cursor()
        sql = "UPDATE user SET name=%s, email=%s WHERE id = %s"
        values = [repetitor.name, repetitor.email, user_id]
        await cursor.execute(sql, values)
        sql = "UPDATE repetitor SET hourly_rate=%s, indeal=%s WHERE user_id = %s"
        values = [repetitor.hourly_rate, repetitor.indeal, user_id]
        await cursor.execute(sql, values)
        await connection.commit()
        await cursor.close()
        connection.close()

    async def get_allsubjects(self):
        connection = await self.connect_to_database()
        cursor = await connection.cursor()
        sql = "SELECT id, name FROM subject"
        values = []
        await cursor.execute(sql, values)
        subjects = list(await cursor.fetchall())
        await cursor.close()
        connection.close()
        return subjects

    async def add_subject(self, subject_id, user_id):
        connection = await self.connect_to_database()
        cursor = await connection.cursor()
        sql = "INSERT INTO repetitor_subject (subject_id, user_id) VALUES (%s, %s)"
        values = [subject_id, user_id]
        await cursor.execute(sql, values)
        await connection.commit()
        await cursor.close()
        connection.close()

    async def remove_subject(self, subject_id, user_id):
        connection = await self.connect_to_database()
        cursor = await connection.cursor()
        sql = "DELETE FROM repetitor_subject WHERE subject_id = %s AND user_id = %s;"
        values = [subject_id, user_id]
        await cursor.execute(sql, values)
        await connection.commit()
        await cursor.close()
        connection.close()

    async def sql_request(self):
        connection = await self.connect_to_database()
        cursor = await connection.cursor()
        sql = " SELECT subject.name, COUNT(subject.name) as count FROM subject JOIN query ON query.subject_id = subject.id " \
              "JOIN request ON query.id = request.query_id " \
              "WHERE request.status_id = 3 GROUP BY subject.name ORDER BY count DESC"
        values = []
        await cursor.execute(sql, values)
        result = await cursor.fetchall()
        await cursor.close()
        connection.close()
        return result
