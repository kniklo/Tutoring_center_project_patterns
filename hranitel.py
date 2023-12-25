# Создаем класс, представляющий хранителя (Memento), который будет хранить состояние
class Memento:
    def __init__(self, state):
        self._state = state

    def get_state(self):
        return self._state

# Создаем класс Опекун, который хранит список хранителей
class Caretaker:
    def __init__(self):
        self._mementos = {}

    def add_memento(self, id, memento):
        res = self._mementos.get(id, None)
        if not res:
            self._mementos[id] = [memento]
        else:
            self._mementos[id].append(memento)

    def get_memento(self, id):
        res = self._mementos.get(id, None)
        if not res:
            return None
        else:
            m = self._mementos[id][-1]
            self._mementos[id] = self._mementos[id][:-1]
            return m
