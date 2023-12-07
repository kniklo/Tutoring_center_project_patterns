class User:
    def __init__(self, login: str, password: str, name: str = None, email: str = None):
        self.login = login
        self.password = password
        self.name = name
        self.email = email


# Класс Builder для создания объектов User
class UserBuilder:
    def __init__(self, login: str, password: str):
        self.user = User(login, password)

    def set_name(self, name: str):
        self.user.name = name
        return self

    def set_email(self, email: str):
        self.user.email = email
        return self

    def build(self):
        return self.user

class Repetitor(User):

    def __init__(self, login: str, password: str, indeal: int = 0, hourly_rate: float = 0.0):
        super().__init__(login, password)
        self.indeal = indeal
        self.hourly_rate = hourly_rate


# Класс Builder для создания объектов Repetitor
class RepetitorBuilder:
    def __init__(self, login: str, password: str):
        self.repetitor = Repetitor(login, password)

    def set_indeal(self, indeal: int):
        self.repetitor.indeal = indeal
        return self

    def set_hourly_rate(self, hourly_rate: int):
        self.repetitor.hourly_rate = hourly_rate
        return self

    def build(self):
        return self.repetitor