from abc import ABC, abstractmethod


# Observer
class Observer(ABC):
    @abstractmethod
    def update(self, user, status):
        pass


# ConcreteObserver
class RequestObserver(Observer):
    def __init__(self, name):
        self.name = name

    def update(self, user, status):
        match status:
            case 1:
                self.send_mail_to_client(user)
            case 2:
                self.send_mail_to_tutor(user)

    def send_mail_to_client(self, user):
        print(f"{self.name} says: email to {user[1]} sent with next prompt: \nDear {user[0]}!!! \n"
              f"Your request was accepted by tutor.")

    def send_mail_to_tutor(self, user):
        print(f"{self.name} says: email to {user[1]} sent with next prompt: \nDear {user[0]}!!! \n"
              f"Your request was confirmed by client.")


# Subject
class ObserverSubject:
    def __init__(self):
        self.observers = []

    def add_observer(self, observer):
        self.observers.append(observer)

    def remove_observer(self, observer):
        self.observers.remove(observer)

    def notify_observers(self, user, status):
        for observer in self.observers:
            observer.update(user, status)


# ConcreteSubject
class ConcreteObserverSubject(ObserverSubject):
    def __init__(self):
        super().__init__()
        self._status = None

    def set_status(self, user, status):
        self._status = status
        self.notify_observers(user, status)
