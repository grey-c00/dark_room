from abc import ABC, abstractmethod

class NotificationReceiver:
    def __init__(self, info: str):
        self.info = info

class NotificationMsg:
    def __init__(self, msg: str):
        self.msg = msg

class Notification(ABC):
    @abstractmethod
    def send_notification(self, receiver: NotificationReceiver, msg: NotificationMsg):
        pass


class EmailSender(Notification):
    def __init__(self):
        pass

    def send_notification(self, receiver: NotificationReceiver, msg: NotificationMsg):
        print(f"Sending email to {receiver.info} with message: {msg.msg}")


class SMSSender(Notification):
    def __init__(self):
        pass

    def send_notification(self, receiver: NotificationReceiver, msg: NotificationMsg):
        print(f"sending sms to {receiver.info} with message: {msg.msg}")


class PushSender(Notification):
    def __init__(self):
        pass

    def send_notification(self, receiver: NotificationReceiver, msg: NotificationMsg):
        print(f"sending push to {receiver.info} with message: {msg.msg}")



class NotificationFactory:
    @staticmethod
    def get_notification_sender(notification_type: str) -> Notification:
        if notification_type == "email":
            return EmailSender()
        elif notification_type == "sms":
            return SMSSender()
        elif notification_type == "push":
            return PushSender()
        else:
            raise ValueError(f"Unknown notification type: {notification_type}")

