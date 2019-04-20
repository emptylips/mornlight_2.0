from logger import logger

from database_refactor import get_host_condition_by_time

AVERAGE_COEFFICIENT_SCOPE = [i/100 for i in range(80, 111, 1)]
LEAPS_COEFFICIENT = 1.4


def sortByTimestamp(element):
    return element['timestamp']


class Resolution(object):
    def __init__(self, check, check_history, session):
        self.session = session
        self.check = check
        self.countable = None
        self.triple_values = []
        self.average = None

        if self.check.type.countable:
            self.countable = True

        if self.countable:
            self.check_history = sorted(check_history, key=sortByTimestamp)
            for i in range(0, len(self.check_history) + 1, 3):
                sum = 0
                for j in range(i, i + 3):
                    try:
                        sum += float(self.check_history[j]['value'])
                    except IndexError:
                        break
                self.triple_values.append(sum)

            self.close_to_average = self.get_average('c')
            self.greater_th_average = self.get_average('g')
            self.increase = self.detect_increase()
            self.stagnation = self.detect_stagnation()
            self.leaps, self.leaps_count = self.detect_leaps()

    def get_average(self, type):
        self.average = sum(self.triple_values) // len(self.triple_values)
        if type == 'c':
            return round(abs(self.triple_values[-1] / self.average), 2) in AVERAGE_COEFFICIENT_SCOPE
        if type == 'g':
            return self.triple_values[-1] > self.average

    def detect_stagnation(self):
        for item in self.triple_values:
            if item not in AVERAGE_COEFFICIENT_SCOPE:
                return False
            else:
                return True

    def detect_leaps(self):
        count = 0
        for item in self.triple_values:
            if item >= self.average * LEAPS_COEFFICIENT:
                count += 1
        if count > 0:
            return True, count
        else:
            return False, None

    def detect_increase(self):
        left_average = sum(self.triple_values[0:len(self.triple_values) // 2])
        right_everage = sum(self.triple_values[len(self.triple_values) // 2:])

        return left_average < self.average < right_everage

    def get_resolution(self):
        flap_scores = 0
        resolution = []
        if self.countable:
            if self.close_to_average:
                flap_scores -= 1
                resolution.append('close_to_average')
            if self.increase:
                flap_scores += 2
                resolution.append('increase')
            if self.stagnation:
                flap_scores -= 1
                resolution.append('stagnation')
            if self.leaps:
                flap_scores += 1
            if self.greater_th_average:
                resolution.append('greater_th_average')
                flap_scores += 1

        print(resolution)
        if flap_scores > 1:
            logger.info('FLAPSKILLER ' + self.check.name + ' IS NOT FLAP ' + ' '.join(resolution) + self.session)
            return False  # Not flap. Need to notice
        else:
            logger.info('FLAPSKILLER ' + self.check.name + ' IS FLAP ' + ' '.join(resolution) + self.session)
            return True  # Flap. No notice


class FlapsKiller(object):
    def __init__(self, host, checks, session):
        self.host_condition = get_host_condition_by_time(host)
        self.checks = checks
        self.flaps_check = []

        for item in self.checks:
            self.flaps_check.append(Resolution(item, self.host_condition[host][item.name], session).get_resolution())

    def get_host_resolution(self):
        for item in self.flaps_check:
            if not item:
                return True  #  Not flap
        return False  # Flap
















