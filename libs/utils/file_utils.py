import os

from libs.utils.customer_logger import CustomLogger


class FileUtils:
    def __init__(self):
        self.log = CustomLogger()
        self.log.setup_logger()

    def get_list_of_files(self, dirName):
        # create a list of file and sub directories
        # names in the given directory
        list_of_files = os.listdir(dirName)
        all_files = list()
        # Iterate over all the entries
        for entry in list_of_files:
            # Create full path
            full_path = os.path.join(dirName, entry)
            # If entry is a directory then get the list of files in this directory
            if os.path.isdir(full_path):
                all_files = all_files + self.get_list_of_files(full_path)
            else:
                all_files.append(full_path)

        return all_files

    def filter_only_test_files(self, file_list):
        test_file_list = []
        if len(file_list) > 0:
            for file_name in file_list:
                only_file_name = file_name.split("/")[-1]
                if only_file_name.startswith("test") and only_file_name.endswith(".py"):
                    test_file_list.append(file_name)
            return test_file_list
        else:
            return []

    def divide_list_with_range(self, l,index_range):
        final_list = []
        for i in range(0, len(l), index_range):
            # self.log.printStep(l[i:i + 1])
            final_list.append(l[i:i + index_range])
        return final_list

    def get_index_files_list(self, l, devices):
        # looping till length l
        self.log.printStep("number of test cases:{}".format(len(l)))
        self.log.printStep("number of devices:{}".format(devices))
        if len(l)==0 or devices == 0:
            self.log.printStep( "No testcass or devices found...")
            exit()
        if len(l)==1 or devices==1:
            # self.log.printStep(l)
            return [l]
        if len(l)< devices or len(l)== devices:
            return self.divide_list_with_range(l,1)

        else:
            index_range = len(l) // devices
            reminder = len(l) % devices
            final_even_list = l[:-reminder]
            reminder_list = l[-reminder:]
            if reminder == 0:
                return self.divide_list_with_range(reminder_list, index_range)

            # self.log.printStep("index range :{}".format(index_range))
            # self.log.printStep("reminder list:{}".format(l[-reminder:]))
            # self.log.printStep("final Even list:{}".format(l[:-reminder]))

            divided_indexed_list = self.divide_list_with_range(final_even_list,index_range)
            for item in reminder_list:
                divided_indexed_list[0].append(item)
            return divided_indexed_list
