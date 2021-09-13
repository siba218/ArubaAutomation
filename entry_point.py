import json
import multiprocessing
import os
import time

from libs.utils.customer_logger import CustomLogger
from tests.base_universal_test import BaseUniversalTest


class FinalRunClass:
    # @classmethod
    # def setUpClass(cls):
    #     cls.log = CustomLogger()
    #     cls.log.setup_logger()
    #     cls.aruba_automation_config = ArubaAutomationConfig(dump_flag=True, quiet=False)

    def __init__(self):
        # super().setUpClass()
        self.log = CustomLogger()
        self.log.setup_logger()
        BaseUniversalTest().setUpClass()

    def run_test(self, *test_files_list):
        for item in test_files_list:
            time.sleep(5)
            commad = "pytest -v -s {}".format(item)
            print("#######################################")
            print("command is : {}".format(commad))
            print("#######################################")
            print("executing command")
            os.system(commad)
            print("Command execution completed")

    def get_final_data_dictionary(self):
        final_data_dict = os.getenv("FINAL_DATA_DICT")
        print("final data dict as string format:{}".format(final_data_dict))
        return json.loads(final_data_dict)


if __name__ == "__main__":
    obj = FinalRunClass()
    data_dict = obj.get_final_data_dictionary()
    data_dict_keys = list(data_dict.keys())

    # Creating a list of processes
    processes = [multiprocessing.Process(target=obj.run_test, args=(tuple(data_dict[data_dict_keys[i]],))) for i in range(len(data_dict_keys))]

    for p in processes:
        p.start()

    for p in processes:
        p.join()

    # data_dict = {'SWITCH_SG9AGYW0F7': [
    #     '/Users/sibasishmohanta/Documents/Development/ArubaAutomation/tests/workout/sub1/test_sample2_sub1.py',
    #     '/Users/sibasishmohanta/Documents/Development/ArubaAutomation/tests/workout/sub1/test_sample3_sub1.py',
    #     '/Users/sibasishmohanta/Documents/Development/ArubaAutomation/tests/workout/sub1/test_sample1_sub1.py'],
    #     'SWITCH_CN80HKW005': [
    #         '/Users/sibasishmohanta/Documents/Development/ArubaAutomation/tests/workout/test_sample4.py',
    #         '/Users/sibasishmohanta/Documents/Development/ArubaAutomation/tests/workout/test_sample1.py',
    #         '/Users/sibasishmohanta/Documents/Development/ArubaAutomation/tests/workout/test_sample2.py'],
    #     'SWITCH_CN80HKW006': [
    #         '/Users/sibasishmohanta/Documents/Development/ArubaAutomation/tests/workout/test_sample3.py',
    #         '/Users/sibasishmohanta/Documents/Development/ArubaAutomation/tests/workout/sub2/test_sample1_sub2.py',
    #         '/Users/sibasishmohanta/Documents/Development/ArubaAutomation/tests/workout/sub2/test_sample2_sub2.py']}
    # # creating processes
    # p1 = multiprocessing.Process(target=obj.run_test, args=(
    #     "/Users/sibasishmohanta/Documents/Development/ArubaAutomation/tests/workout/sub1/test_sample2_sub1.py",))
    # p2 = multiprocessing.Process(target=obj.run_test, args=(
    #     ("/Users/sibasishmohanta/Documents/Development/ArubaAutomation/tests/workout/test_sample4.py",)))
    #
    # # starting process 1
    # p1.start()
    # # starting process 2
    # p2.start()
    #
    # # wait until process 1 is finished
    # p1.join()
    # # wait until process 2 is finished
    # p2.join()
    #
    # # both processes finished
    print("Done!")
