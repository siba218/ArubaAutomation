import configparser
import json
import os
import os.path
import random
import sys

from libs.utils.customer_logger import CustomLogger
from libs.utils.file_utils import FileUtils

MAX_UNIQUE_ID = 10000000  # Non-inclusive
RANDOM_UNIQUE_ID = random.randrange(MAX_UNIQUE_ID)


class ArubaAutomationError(Exception):

    def __init__(self, value):
        self.value = value


class SingletonPerEnv(type):
    _instances = dict()

    def __call__(cls, *args, **kwargs):
        if 'env' in kwargs:
            env = kwargs['env']
        else:
            env = None
        if env not in cls._instances:
            cls._instances[env] = dict()
        if cls not in cls._instances[env]:
            cls._instances[env][cls] = super(SingletonPerEnv, cls).__call__(*args, **kwargs)
        return cls._instances[env][cls]


class ArubaAutomationConfig(metaclass=SingletonPerEnv):
    """ Class used to configure Aruba Automation. Test Classes use this class to get properties """

    aruba_automation_config_file = 'aruba_automation.cfg'
    aruba_automation_environment_config_file = 'aruba_automation_{0}.cfg'
    my_aruba_automation_environment_config_file = 'my_aruba_automation_environment.cfg'

    def __init__(self, env=None, dump_flag=False, quiet=True):
        self.config = configparser.ConfigParser()
        BASE_DIR = os.path.dirname(os.path.dirname(__file__))
        self.config_dir = BASE_DIR + '/../tests/config'

        self.log = CustomLogger()
        self.config._interpolation = configparser.ExtendedInterpolation()
        self.quiet = quiet

        # configure
        if dump_flag:
            self.configure_aruba_automation(env=env)
            module_name = self.get_module_name()
            device_type = self.get_device_type()
            testcases_list = self.get_all_test_files_list()
            self.assign_testcases_with_devices(testcases_list, device_type, module_name)
            self.dump_all_properties()
        else:
            self.configure_aruba_automation(env=env)

    def get_sections(self):
        return ','.join(self.config.sections())

    def get_device_sections(self, device_type, module_name):
        sections = self.config.sections()
        device_section = []
        for item in sections:
            if item.__contains__(device_type) and item.__contains__(module_name):
                device_section.append(item)
        return device_section

    def get_section_keys(self, section):
        return list(map(lambda x: x.upper(), self.config.options(section)))

    def get_property(self, section_name, property_name, default_value=''):
        property_value = self.config.get(section_name, property_name)
        if not property_value:
            return default_value
        else:
            return property_value

    def get_property_check(self, section_name, property_name):
        property_value = self.config.get(section_name, property_name)
        if not property_value:
            raise ArubaAutomationError('[{}].{} does not exist in aruba_automation.cfg or overrides'
                                       .format(section_name, property_name))
        else:
            return property_value

    def get_aruba_env(self, section_name, property_name):
        """
        Get from a standardized environment variable, and if it does not exist, look in the config file
        """
        env_var = 'ARUBA_AUTOMATION_' + section_name.upper() + '_' + property_name.upper()
        env_value = os.getenv(env_var, '')
        if env_value:
            self.log.printDebug('[{}] {} config property loaded from environment variable {}'
                                .format(section_name, property_name, env_var), quiet=self.quiet)
            self.config.set(section_name, property_name, env_value)
        return env_value

    def get_property_env(self, section_name, property_name, default_value=''):
        self.get_aruba_env(section_name, property_name)
        return self.get_property(section_name, property_name, default_value=default_value)

    def get_property_env_check(self, section_name, property_name):
        self.get_aruba_env(section_name, property_name)
        return self.get_property_check(section_name, property_name)

    def get_environment(self):
        return self.config.get('System', 'environment')

    def configure_aruba_automation(self, env):

        # Load default config file
        self.log.printDebug('\nBegin Scanning automation config files inside base directory.', quiet=self.quiet)
        self.config_file_path = self.config_dir + '/' + self.aruba_automation_config_file
        self.debugIsConfigFileFound = os.path.isfile(self.config_file_path)
        self.debugFileFoundStr = 'File was found.' if self.debugIsConfigFileFound else 'File not found'
        self.log.printDebug('Base directory is: {}'.format(self.config_dir), quiet=self.quiet)
        self.log.printDebug('Checking for Base Aruba Automation config file: {} ... {}'
                            .format(self.aruba_automation_config_file, self.debugFileFoundStr), quiet=self.quiet)
        self.config.read(self.config_file_path)

        # Load My Aruba Automation config file
        self.my_environment = None
        self.my_aruba_automation_config_file_path = self.config_dir + '/' + \
                                                    self.my_aruba_automation_environment_config_file
        if env:
            self.my_environment = env
        else:
            # Configure environment from optional file
            if os.path.isfile(self.my_aruba_automation_config_file_path):
                self.my_env_config = configparser.ConfigParser()
                self.my_env_config.read(self.my_aruba_automation_config_file_path)
                self.my_environment = self.my_env_config.get('System', 'environment')

        self.debugIsConfigFileFound = os.path.isfile(self.my_aruba_automation_config_file_path)
        self.debugFileFoundStr = 'File was found.' if self.debugIsConfigFileFound else 'File not found'
        self.log.printDebug('Checking for My Aruba Automation config file: {} ... {}'
                            .format(self.my_aruba_automation_environment_config_file, self.debugFileFoundStr),
                            quiet=self.quiet)
        if self.my_environment:
            self.config.set('System', 'environment', self.my_environment)
        else:
            self.log.printDebug('My Aruba Automation config file was not found. Assigning default: yoda and '
                                'continuing', quiet=self.quiet)
            self.config.set('System', 'environment', 'yoda')

        # Configure Aruba Automation Environment from environment variable
        environment = os.getenv('ARUBA_AUTOMATION_ENVIRONMENT', '')
        if environment:
            self.log.printDebug('Overriding Aruba Automation Environment via System Environment Variable!',
                                quiet=self.quiet)
            self.config.set('System', 'environment', environment)

        self.debugFileFoundStr = 'Env variable overrides found' if environment else 'No Env variable overrides found.'
        self.log.printDebug('Checking for any System Environment Variable overrides: ... {}'.format(
            self.debugFileFoundStr), quiet=self.quiet)
        self.log.printDebug('Aruba Automation environment detected: ' + self.get_environment(), quiet=self.quiet)

        # Load environment specific config file
        self.environment_config_path = self.aruba_automation_environment_config_file.format(self.get_environment())
        self.environment_config_file_path = self.config_dir + '/' + self.environment_config_path
        self.debugIsConfigFileFound = os.path.isfile(self.environment_config_file_path)
        self.debugFileFoundStr = 'File was found.' if self.debugIsConfigFileFound else 'File not found'
        self.log.printDebug('Checking for {} config file: {} ... {}'
                            .format(self.get_environment(), self.environment_config_path, self.debugFileFoundStr),
                            quiet=self.quiet)

        if os.path.isfile(self.environment_config_file_path):
            self.config.read(self.environment_config_file_path)
        else:
            self.log.printDebug('Aruba Automation environment config file was not found. Invalid environment: {} '
                                '.Exiting.'.format(self.get_environment()), quiet=self.quiet)
            sys.exit(1)

        # Load non-environment specific overrides file specified through an environment variable
        overrides_file_path = os.getenv('ARUBA_AUTOMATION_OVERRIDES_FILE_PATH', '')
        self.debugFileFoundStr = 'Overrides file path env variable was found ' \
            if overrides_file_path else 'No overrides file path env variable was found'
        if overrides_file_path:
            self.log.printDebug('File paths below are absolute.', quiet=self.quiet)
            self.log.printDebug('Aruba Automation env overrides variable config path: {}'
                                .format(overrides_file_path), quiet=self.quiet)
            self.log.printDebug('Aruba Automation env overrides variable config file exists: {}'
                                .format(os.path.isfile(overrides_file_path)), quiet=self.quiet)
            if os.path.isfile(overrides_file_path):
                self.config.read(overrides_file_path)
            else:
                self.log.printDebug('Aruba Automation env overrides variable config file was not found. Continuing',
                                    quiet=self.quiet)
            self.log.printDebug('File paths below are relative to base directory.', quiet=self.quiet)
        else:
            self.log.printDebug('Checking for any overrides file path env Variable: ... {}'.format(
                self.debugFileFoundStr), quiet=self.quiet)

        # Load environment specific overrides file in config directory
        self.env_overrides_file_path = 'overrides_{}.cfg'.format(self.get_environment())
        self.env_overrides_file_in_config_dir = self.config_dir + '/' + self.env_overrides_file_path
        self.debugIsConfigFileFound = os.path.isfile(self.env_overrides_file_in_config_dir)
        self.debugFileFoundStr = 'File was found.' if self.debugIsConfigFileFound else 'File not found'
        self.log.printDebug('Checking for {} overrides config file: {} ... {}'
                            .format(self.get_environment(), self.env_overrides_file_path, self.debugFileFoundStr),
                            quiet=self.quiet)
        if os.path.isfile(self.env_overrides_file_in_config_dir):
            self.log.printDebug('Initializing overrides_{}.cfg file in config directory: {}'
                                .format(self.get_environment(), self.env_overrides_file_in_config_dir),
                                quiet=self.quiet)
            self.config.read(self.env_overrides_file_in_config_dir)

        # Load fallback overrides file in 'config' directory.
        # configure sensitive information like password etc through this 'overrides.cfg' file
        self.final_overrides_file_path = 'overrides.cfg'
        self.final_overrides_file_in_config_dir = self.config_dir + '/' + self.final_overrides_file_path
        self.debugIsConfigFileFound = os.path.isfile(self.final_overrides_file_in_config_dir)
        self.debugFileFoundStr = 'File was found.' if self.debugIsConfigFileFound else 'File not found'
        self.log.printDebug('Checking for final overrides config file: {} ... {}'
                            .format(self.final_overrides_file_path, self.debugFileFoundStr)
                            , quiet=self.quiet)
        if os.path.isfile(self.final_overrides_file_in_config_dir):
            self.log.printDebug('Initializing final overrides.cfg file in config directory', quiet=self.quiet)
            self.config.read(self.final_overrides_file_in_config_dir, encoding='utf-8')
        else:
            self.log.printDebug('Final overrides config file was not found in config directory. '
                                'Continuing', quiet=self.quiet)
        self.log.printDebug('End Scanning automation config files inside base directory.\n', quiet=self.quiet)

        # testing few things
        # self.config.set('TestCase', 'test_sample1_iap1.py', 'SG9AGYW0F7')

    def dump_all_properties(self):
        self.log.printDebug('Starting to dump all available properties!', quiet=self.quiet)
        if self.config.get('System', 'dump_non_system_properties').lower() == 'true':
            for section in self.config.sections():
                for option in self.config.options(section):
                    # skip password properties
                    if not option.find('password') > -1:
                        self.log.printDebug('Section: {} , Property: {} , Value: {}'.format(
                            section, option, self.get_property(section, option)), quiet=self.quiet)
            self.log.printDebug('Completed dumping all available properties!', quiet=self.quiet)
        else:
            for option in self.config.options('System'):
                self.log.printDebug('Section: System , Property: {} , Value: {}'.format(option, self.get_property(
                    'System', option)), quiet=self.quiet)
            self.log.printDebug('Completed dumping just System properties!', quiet=self.quiet)

    def get_all_test_files_list(self):
        # fetch all the test files given in a  folder
        file_utils = FileUtils()
        all_test_files = []

        self.log.printStep("Fetching -ARUBA_AUTOMATION_TESTCASE_PATH- from env variable..")
        test_execution_path = os.getenv('ARUBA_AUTOMATION_TESTCASE_PATH')
        if test_execution_path is not None:
            self.log.printStep(
                "ARUBA_AUTOMATION_TESTCASE_PATH found from env variables :{}".format(test_execution_path))
            if os.path.isfile(test_execution_path):
                all_test_files.append(test_execution_path)
                return all_test_files
            all_files = file_utils.get_list_of_files(test_execution_path)
            all_test_files = file_utils.filter_only_test_files(all_files)
            return all_test_files
        else:
            self.log.printStep("ARUBA_AUTOMATION_TESTCASE_PATH env variable not found..")
            self.log.printStep("Fetching testcase path from local overrides file..")
            try:
                overrides_execution_path = self.get_property("System", "ARUBA_AUTOMATION_TESTCASE_PATH")
            except:
                self.log.printStep("Not found testcase path in local overrides env specific files. ")
                self.log.printStep("please provide testcase path in local env specific overrides file")
                self.log.printStep("exiting from the program...")
                sys.exit(1)

            if overrides_execution_path:
                self.log.printStep("Found testcase path from local overrides file")
                self.log.printStep("Test execution path from local overrides file: {}".format(overrides_execution_path))
                if os.path.isfile(overrides_execution_path):
                    all_test_files.append(overrides_execution_path)
                    return all_test_files
                all_files = file_utils.get_list_of_files(overrides_execution_path)
                all_test_files = file_utils.filter_only_test_files(all_files)
                return all_test_files

    def get_module_name(self):
        self.log.printLog("Fetching -MODULE_NAME- from env variable")
        device_type_from_env = os.getenv('MODULE_NAME')
        if device_type_from_env is not None:
            self.log.printLog("MODULE_NAME found from env variable..")
            return device_type_from_env
        else:
            self.log.printStep("MODULE_NAME env variable not found..")
            self.log.printStep("Fetching MODULE_NAME from local overrides file..")
            try:
                device_type = self.get_property("System", "MODULE_NAME")
            except:
                self.log.printStep("Not found MODULE_NAME  in local overrides env specific files. ")
                self.log.printStep("please provide MODULE_NAME  in local env specific overrides file")
                self.log.printStep("exiting from the program...")
                sys.exit(1)
            self.log.printLog("-MODULE_NAME- found from local overrides files")
            return device_type

    def get_device_type(self):
        self.log.printLog("Fetching -DEVICE_TYPE- from env variable")
        device_type_from_env = os.getenv('DEVICE_TYPE')
        if device_type_from_env is not None:
            self.log.printLog("DEVICE_TYPE found from env variable")
            return device_type_from_env
        else:
            self.log.printStep("DEVICE_TYPE env variable not found..")
            self.log.printStep("Fetching DEVICE_TYPE from local overrides file..")
            try:
                device_type = self.get_property("System", "DEVICE_TYPE")
            except:
                self.log.printStep("Not found DEVICE_TYPE  in local overrides env specific files. ")
                self.log.printStep("please provide DEVICE_TYPE  in local env specific overrides file")
                self.log.printStep("exiting from the program...")
                sys.exit(1)
            self.log.printLog("-DEVICE_TYPE- found from local overrides files")
            return device_type

    def assign_testcases_with_devices(self, all_test_files, device_type, module_name):
        file_utils = FileUtils()
        device_list_from_config = []
        if device_type == "SWITCH":
            device_list_from_config = ArubaAutomationConfig().get_device_sections(device_type, module_name)
        elif device_type == "IAP":
            device_list_from_config = ArubaAutomationConfig().get_device_sections(device_type, module_name)
        elif device_type == "GATEWAY":
            device_list_from_config = ArubaAutomationConfig().get_device_sections(device_type, module_name)
        else:
            self.log.printLog("{} - not found in the list of devices. supported - SWITCH/IAP/GATEWAY")
            sys.exit(1)

        indexed_testcase_list = file_utils.get_index_files_list(all_test_files, len(device_list_from_config))
        final_data_dict = {}
        if len(device_list_from_config) > len(indexed_testcase_list):
            for i in range(len(indexed_testcase_list)):
                final_data_dict[device_list_from_config[i]] = indexed_testcase_list[i]

        elif len(device_list_from_config) == len(indexed_testcase_list):
            for i in range(len(device_list_from_config)):
                final_data_dict[device_list_from_config[i]] = indexed_testcase_list[i]

        # pushing all testcase with device_serial to config
        for key in final_data_dict.keys():
            files_list = final_data_dict[key]
            for item in files_list:
                self.config.set('TestCase', item, key)
        # self.log.printStep("indexed testcases list: {}".format(indexed_testcase_list))
        self.log.printStep("final data dict:{}".format(final_data_dict))

        # Pushing the final data dict to env variable
        # os.environ["FINAL_DATA_DICT"] = "\""+str(final_data_dict)+"\""
        os.environ["FINAL_DATA_DICT"] = json.dumps(final_data_dict)
