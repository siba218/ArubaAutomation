import configparser
import os
import os.path
import random
import sys

from libs.utils.customer_logger import CustomLogger

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
            self.dump_all_properties()
        else:
            self.configure_aruba_automation(env=env)

    def get_sections(self):
        return ','.join(self.config.sections())

    def get_section_keys(self, section):
        return list(map(lambda x:x.upper(),self.config.options(section)))

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

        # testing few things
        self.config.set('TestCase', 'new_test_key', 'device_serial_key')

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

