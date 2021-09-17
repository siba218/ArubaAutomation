import math
import time
from datetime import datetime, timedelta

import pytz
from tzlocal import get_localzone

from libs.utils.customer_logger import CustomLogger


class TimeUtils:

    def __init__(self):
        self.log = CustomLogger()
        self.log.setup_logger()

    def get_current_epoc_time(self, minute_time_ahead):
        millisecond = datetime.now() + timedelta(minutes=minute_time_ahead)
        epoch_time = math.trunc(time.mktime(millisecond.timetuple()) * 1000)
        self.log.printLog("epoch time is: {}".format(epoch_time))
        return epoch_time

    def get_current_time_as_utc_in_epoch(self, minute_time_ahead):
        """ This method has specific logic for upgrade type like - device_local _time
        eg. if current time is 1:39PM IST then we are returning 1:39PM UTC in epoch format
        if we are not converting like this and passing the epoch time to firmware upgrade payload
        then scheduling not happening
        """
        local_time_stamp = datetime.now()
        utc_timezone = pytz.timezone("UTC")

        current_timezone = get_localzone()
        zone = current_timezone.zone
        new_timezone = pytz.timezone(zone)

        new_timezone_timestamp = utc_timezone.localize(local_time_stamp).astimezone(new_timezone)

        time_to_convert = new_timezone_timestamp + timedelta(minutes=minute_time_ahead)
        epoch_time = math.trunc(time.mktime(time_to_convert.timetuple()) * 1000)
        self.log.printLog("epoch time is :{}".format(epoch_time))
        return epoch_time

#
#
# if __name__ == "__main__":
#     # print(TimeUtils().get_current_utc_epoc_time(5))
#     print(TimeUtils().get_current_utc_time_as_current_in_epoch(5))
