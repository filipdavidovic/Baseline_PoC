# System modules
import datetime
# Imported modules
import scipy.stats
# Project modules
import utils

WEEK_LEN = 7
DAY_LEN = 24


def _create_base_slots(metrics):
    weeks = [BaseSlot(metrics[0][0])]

    # Place metrics into base slots
    week_i = 0
    for dp in metrics:
        if dp[0] > weeks[week_i].end_time:
            weeks.append(BaseSlot(dp[0]))
            week_i += 1
        day = dp[0].weekday()
        hour = dp[0].hour
        weeks[week_i].add_item(day, hour, dp[1])

    return weeks


class Baseline:
    def __init__(self, metrics, window_size: int):
        """
        :param metrics: Array in which each row contains a datetime object and a value for the metric. The first and
                        last week don't need to be complete, but all weeks in between do. In other words, metrics
                        shouldn't contain gaps. Finally, the number of complete weeks should be at least window_size.
        :param window_size: Number of (last) base slots that should be taken into consideration as the baseline.
        """
        if window_size <= 0:
            raise ValueError('Window size must be a positive integer')

        self.window_size = window_size
        metrics = sorted(metrics, key=lambda x: x[0])

        weeks = _create_base_slots(metrics)

        # Find last window_size complete base slots
        week_i = 0
        for i, week in enumerate(reversed(weeks)):
            if week.is_complete():
                week_i = len(weeks) - i
                break

        if week_i < window_size \
                or not weeks[week_i - window_size].is_complete():
            raise ValueError('There are not enough complete weeks to use window size of {}.'.format(window_size))

        self.base_slots = weeks[(week_i - window_size):week_i]

        # Initialize base slot objects
        for base_slot in self.base_slots:
            base_slot.initialize()

        # Initialize baseline using base slots
        self._calculate()

    def _calculate(self):
        """
        Private method used to calculate the baseline from the base slots. Base slots are not used as the baseline
        because this approach would require additional computation with each is_alerting call.
        """
        bl = [[[] for _ in range(DAY_LEN)] for _ in range(WEEK_LEN)]
        self.baseline = [[None for _ in range(DAY_LEN)] for _ in range(WEEK_LEN)]

        # Build collection slot arrays
        for base_slot in self.base_slots:
            for day in range(WEEK_LEN):
                for hour in range(DAY_LEN):
                    bl[day][hour].append(base_slot.get_item(day, hour))

        # Build baseline object
        for day in range(WEEK_LEN):
            for hour in range(DAY_LEN):
                stats = utils.stats(bl[day][hour])
                self.baseline[day][hour] = CollectionSlot(stats['mean'], stats['std_dev'])

    def is_alerting(self, time: datetime.datetime, val: float, threshold: float):
        """
        Method used to check whether a value observed at a certain time is alerting.

        :param time: Time at which the value is observed. This value decides the collection slot that will be used.
        :param val: Observed value with which an alert might be triggered.
        :param threshold: Number representing the minimum probability to accept as non-alerting. If the CDF of a
                          certain value returns a value lower than this, and alert will be triggered.
        :return: True if the alert should be triggered, False otherwise
        """
        if threshold > 1.0 or threshold < 0.0:
            raise ValueError('Threshold has to be in the [0, 1] interval.')

        day = time.weekday()
        hour = time.hour

        # Find x such that CDF(x) = threshold => PPF(threshold) = x
        x = scipy.stats.norm.ppf(threshold, loc=self.baseline[day][hour].mean, scale=self.baseline[day][hour].std_dev)

        if val > x:
            return True
        else:
            return False

    def add_data(self, metrics):
        """
        Method used to add new data to the baseline. At most window_size base slots are replaced from the initial
        baseline. Note that base slots need to be complete in order to be added. Finally, this method makes the
        assumption that there are no gaps in the metrics, i.e. only the first and the last base slot can be
        incomplete.

        :param metrics: Metrics to potentially include in the baseline
        """
        # Sort the data points in ascending order by date, and remove all data points which are older than the
        # current baseline
        metrics = sorted(metrics, key=lambda x: x[0])
        metrics = filter(lambda x: x[0] > self.base_slots[self.window_size - 1].end_time, metrics)

        weeks = _create_base_slots(metrics)

        # Find newest complete base slot
        last_complete_week_i = 0
        for i, week in enumerate(reversed(weeks)):
            if week.is_complete():
                last_complete_week_i = len(weeks) - i - 1
                break

        # Find oldest needed base slot
        first_complete_week_i = last_complete_week_i
        counter = 1
        for i, week in enumerate(reversed(weeks[0:last_complete_week_i])):
            is_complete = week.is_complete()
            if is_complete and counter < self.window_size:
                counter += 1
                first_complete_week_i = last_complete_week_i - i - 1
            else:
                break

        # Replace at most window_size base slots in the baseline
        for _ in range(last_complete_week_i - first_complete_week_i + 1):
            self.base_slots.pop(0)

        self.base_slots += weeks[first_complete_week_i:(last_complete_week_i + 1)]

        # Recalculate baseline collection slots using the new base slots
        self._calculate()


class BaseSlot:
    def __init__(self, time_in_week):
        self.start_time = time_in_week - datetime.timedelta(days=time_in_week.weekday())
        self.start_time = self.start_time.replace(hour=0, minute=0, second=0, microsecond=0)
        self.end_time = time_in_week + datetime.timedelta(days=(6 - time_in_week.weekday()))
        self.end_time = self.end_time.replace(hour=23, minute=59, second=59, microsecond=999999)

        self.collection_slots = [[[] for _ in range(DAY_LEN)] for _ in range(WEEK_LEN)]
        self.initialized = False

    def add_item(self, day, hour, val):
        if self.initialized:
            raise ValueError('More items cannot be added after initialization')
        self.collection_slots[day][hour].append(val)

    def get_item(self, day, hour):
        if not self.initialized:
            raise ValueError('Items cannot be fetched before initialization')
        return self.collection_slots[day][hour]

    def is_complete(self):
        for day in range(WEEK_LEN):
            for hour in range(DAY_LEN):
                if len(self.collection_slots[day][hour]) == 0:
                    return False
        return True

    def initialize(self):
        self.initialized = True


class CollectionSlot:
    def __init__(self, mean, std_dev):
        self.mean = mean
        self.std_dev = std_dev
