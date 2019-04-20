import logging

from notices.mail_notice import send_email
from notices.telegram import send_message
from flaps_killer import FlapsKiller

WAY_SCORES = {'email': 1, 'telegram' : 2, 'sms' : 4}

logging.basicConfig(filename="mornlight.log", level=logging.INFO)
log = logging.getLogger("mornlight")


class Notification(object):

    def __init__(self, host, status, checks, session):
        self.host = host
        self.host_status = status
        self.checks_data = checks
        self.config = ['email', 'telegram', 'sms']
        checks_dict = {}

        for item in self.checks_data:
            checks_dict[item.name] = {"status": item.status, "value": item.value}
        try:
            flapskiller_resolution = FlapsKiller(host, checks, session).get_host_resolution()
        except Exception as exc:
            log.error('Cannot go to FlapsKiller', exc_info=True)

        if flapskiller_resolution:  # If not flap

            if 'email' in self.config:
                send_email(self.host, self.host_status, checks_dict)
            if 'telegram' in self.config:
                send_message(self.host, self.host_status, checks_dict)
        else:
            print('Flap. No notice')


if __name__ == "__main__":
    pass
