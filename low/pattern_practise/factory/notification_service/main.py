from low.pattern_practise.factory.notification_service.notification_classes import NotificationFactory, \
    NotificationReceiver, NotificationMsg


def test_notification():
    notification_factory = NotificationFactory()
    lst = []
    for notification_type in ["email", "sms"]:
        lst.append(notification_factory.get_notification_sender(notification_type=notification_type))

    receiver = NotificationReceiver("test@gmail.com")
    msg = NotificationMsg("test msg")

    for notification_sender in lst:
        notification_sender.send_notification(receiver, msg)

    return True

if __name__=="__main__":
    test_notification()