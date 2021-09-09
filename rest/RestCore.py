from __future__ import print_function

import ast
import inspect
import logging
from builtins import object

__author__ = 'rrkrishnan, pchallapalli'

###############IMPORT STATEMENTS #########################
from datetime import datetime

import voluptuous

from libs.utils.customer_logger import CustomLogger
from rest import LogModule as log
import requests, copy
from requests.packages.urllib3.util import Retry
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import pprint
import sys
import json
import time
import os
###############IMPORT STATEMENTS #########################

# To turn off File Warnings
import warnings

# from utils.aruba_automation_config import ArubaAutomationError


warnings.filterwarnings('ignore')

# Remove unwanted requests package warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# DEFAULT Timeout
DEFAULT_TIMEOUT = 120

logger = log.getLogger(__name__)

SUCCESS_CODES = [200, 201, 202, 204]

class Response:

    def __init__(self, status_code, body, headers, cookie):
        self.status_code = status_code
        self.body = body
        self.headers = headers
        self.cookie = cookie

    def header_length(self):
        """Get the length of the header

        Returns:
            The length of the header of a response
        """
        return len(json.dumps(self.headers))


class TimeoutSession(requests.Session):
    """
    TimeoutSession is a wrapper class for Session
    For all session requests, if timeout param is not passed,
    DEFAULT_TIMEOUT timeout will be taken.
    """

    def request(self, *args, **kwargs):
        if kwargs.get('timeout') is None:
            kwargs['timeout'] = DEFAULT_TIMEOUT
        return super(TimeoutSession, self).request(*args, **kwargs)


class RestCore(object):

    def __init__(self, verify=False, validate_response=True):
        self.session = TimeoutSession()
        retry = Retry(total=3, connect=3, read=3, status=3, backoff_factor=5)
        adapter = requests.adapters.HTTPAdapter(max_retries=retry)
        self.session.mount("https://", adapter)
        self.logger = logger.getChild(self.__class__.__name__)
        self.verify = verify
        self.validate_response = validate_response

    @staticmethod
    def save_request(*args, **kwargs):
        global PREV_REQUEST
        PREV_REQUEST = (args, kwargs)

    @staticmethod
    def get_prev_request():
        return PREV_REQUEST

    @staticmethod
    def get_request(url, method, caller=None, token=None, cookie=None, body=None, headers=None, params=None,
                content_type=None, accept=None, validate=False, schema=None, files=None, quiet=False, auth=None,
                session=None, use_color=True, verify=None, retries=0, benchmark=False):

        RestCore.save_request(url, method, caller=caller, token=token, cookie=cookie, body=body, headers=headers,
                             params=params, content_type=content_type, accept=accept, validate=validate,
                             schema=schema, files=files, quiet=quiet, auth=auth, session=session, use_color=use_color,
                             verify=verify, retries=retries, benchmark=benchmark)

        if caller is None:
            current_frame = inspect.currentframe()
            caller_frame = inspect.getouterframes(current_frame, 2)
            caller = caller_frame[1][3]
            del current_frame
            del caller_frame
        if cookie:
            cookie = cookie
        if content_type is None:
            content_type = 'application/json'
        if body is None:
            body = ''
        elif content_type == "application/octet-stream":
            body = body
        elif content_type == 'application/json' and len(body) >= 0:
            body = json.dumps(body, sort_keys=True)
        elif content_type == 'multipart/form-data':
            body = body
            content_type = None
        if headers is None:
            headers = dict()
        if params is None:
            params = ''
        if accept is None:
            accept = 'application/json'
        if token is not None:
            headers['auth_token'] = '%s' % token
        headers['Content-Type'] = content_type
        headers['Accept'] = accept
        logging.getLogger('requests').setLevel(logging.WARNING)
        while True:
            start_time = datetime.now()
            if session:
                r = session.request(
                    url=url,
                    method=method,
                    data=body,
                    headers=headers,
                    params=params,
                    cookies=cookie,
                    files=files,
                    auth=auth,
                    verify=verify
                )
            else:
                r = requests.request(
                    url=url,
                    method=method,
                    data=body,
                    headers=headers,
                    params=params,
                    cookies=cookie,
                    files=files,
                    auth=auth,
                    verify=verify
                )
            end_time = datetime.now()
            if benchmark:
                response_time = (end_time - start_time).total_seconds()
            else:
                response_time = None
            try:
                if r.content:
                    r.json = RestCore.process_response_body(r.content)
                else:
                    r.json = ''
            except UnicodeDecodeError:
                r.json = r.content
            response = Response(r.status_code, r.json, RestCore.form_real_dict(r.headers), r.cookies.get_dict())
            if schema:
                schema_http_code = RestCore.schema_http_code(schema)
                error = r.status_code != schema_http_code and validate
            else:
                error = r.status_code >= 400 and validate
            exception_message = ''
            exception = None
            if error:
                exception_message = 'Unexpected HTTP code {}'.format(r.status_code)
                exception = ArubaHTTPError((exception_message, response, r))
            elif validate and schema:
                try:
                    schema(response)
                except voluptuous.Error as e:
                    error = True
                    schema_data = RestCore.schema_data(schema)
                    exception_message = str(type(e)) + ': ' + str(e) + '\nEXPECTED:\n' + pprint.pformat(schema_data, width=140)
                    exception = ArubaHTTPError((exception_message, response, r))
            RestCore.nice_print_out(r=r, caller=caller, error=error, quiet=quiet, use_color=use_color,
                                   response_time=response_time)
            if error and exception:
                logging.error(exception_message)
                if r.status_code in [502, 503, 504, 429] and retries > 0:
                    if r.status_code == 429:
                        logging.error('Waiting 5 seconds after getting 429 - Too Many Requests')
                        time.sleep(5)  # 429 = "Too Many Requests", so delay
                    logging.error('Retrying... {} retries left'.format(retries))
                    retries -= 1
                    continue
                raise exception
            break
        response.headers['automation_response_time'] = str(r.elapsed.total_seconds())
        return response

    # def __init__(self, verify=False, validate_response=True):
    #     """
    #     Core class for the Central session libraries
    #     :param verify: Class level verification flag to skip the cert validation
    #     """
    #     self.session = TimeoutSession()
    #     retry = Retry(total=3, connect=3, read=3, status=3, backoff_factor=5)
    #     adapter = requests.adapters.HTTPAdapter(max_retries=retry)
    #     self.session.mount("https://", adapter)
    #     self.logger = logger.getChild(self.__class__.__name__)
    #     self.verify = verify
    #     self.validate_response = validate_response

    def __recoverable(self, error, url, request, counter=1, retry_codes=[]):
        if hasattr(error, 'status_code'):
            if error.status_code in [502, 503, 504, 500] + retry_codes:
                error = "HTTP %s" % error.status_code
            elif "ReadTimeout" in "%s" % error:
                self.logger.error("Read Timeout Error")
            else:
                return False
        DELAY = 10 * counter
        self.logger.warning(
            "Got recoverable error [%s] from %s %s, retry #%s in %ss" % (error, request, url, counter, DELAY))
        time.sleep(DELAY)
        return True

    def _validate_response(self, response):
        method = sys._getframe().f_back.f_code.co_name
        if response.status_code in SUCCESS_CODES:
            self.logger.info("{0} Successful".format(method.upper()))
        else:
            if 'PYTEST_CURRENT_TEST' in list(os.environ.keys()):
                self.logger.info(
                    "NON_2XX:{0} url failed with {1} error in {2} test case".format(response.url, response.status_code,
                                                                                    os.environ['PYTEST_CURRENT_TEST']))
            self.logger.error("{0} Failed".format(method.upper()))
            self.logger.info("################ EXITING {0} BLOCK ###################".format(method.upper()))
            raise Exception(response)

    def _convert_payload(self, data):
        if data is not None and isinstance(data, dict):
            return json.dumps(data)
        else:
            return data

    def get(self, url,
            params=None,
            data=None,
            headers=None,
            cookies=None,
            files=None,
            auth=None,
            timeout=None,
            allow_redirects=True,
            proxies=None,
            hooks=None,
            stream=None,
            verify=None,
            cert=None,
            json=None,
            validate_response=True,
            print_response=True,
            **kwargs):
        """
        Get wrapper to add on Central URL and print anomoly in the responses
        :param url: Request URL
        :param kwargs: Different params that requires to be passed in get call
        :return: Returns the response as it is
        """
        if not params:
            q_param = {}
            kw = kwargs
            kwargs = {}
            for k, v in kw.items():
                q_param[k] = v
            params = q_param

        if verify == None:
            verify = self.verify
        # if print_response:
        #     self.logger.info("############# INTO GET BLOCK ###############")
        #     self.logger.info("REQUEST URL: %s" % (url))
        #     self.logger.info("REQUEST DATA: %s" % (self._convert_payload(data)))
        #     self.logger.info("REQUEST HEADERS: %s" % (self.session.headers))
        #     self.logger.info("REQUEST COOKIES: %s" % (self.session.cookies.get_dict()))

        api_request_time = time.time()
        counter = 0
        while counter < 3:
            counter += 1
            try:
                r = self.session.get(url,
                                            params=params,
                                            data=self._convert_payload(data),
                                            headers=headers,
                                            cookies=cookies,
                                            files=files,
                                            auth=auth,
                                            timeout=timeout,
                                            allow_redirects=allow_redirects,
                                            proxies=proxies,
                                            hooks=hooks,
                                            stream=stream,
                                            verify=verify,
                                            cert=cert,
                                            json=json, **kwargs)
                # r = copy.deepcopy(response)
                api_response_time = time.time() - api_request_time
                RestCore.nice_print_out(r, caller="", error=False, quiet=False, use_color=True, response_time=None)
                try:
                    if r.content:
                        r.json = RestCore.process_response_body(r.content)
                    else:
                        r.json = ''
                except UnicodeDecodeError:
                    r.json = r.content
                response = Response(r.status_code, r.json, RestCore.form_real_dict(r.headers), r.cookies.get_dict())


                if self.validate_response and validate_response:
                    self._validate_response(response)
                if int(api_response_time) >= 3:
                    self.logger.error("API REQUEST-RESPONSE TIME LIMIT EXCEEDED : {} sec".format(api_response_time))
            except Exception as e:
                r = e.args[0]
                self.logger.error("Exception occured : {}".format(r))
            if self.__recoverable(r, url, 'GET', counter, retry_codes=[400, 401]):
                continue
            if self.validate_response and validate_response:
                self._validate_response(response)
            else:
                if response.status_code not in SUCCESS_CODES:
                    if 'PYTEST_CURRENT_TEST' in list(os.environ.keys()):
                        self.logger.info("NON_2XX:{0} url failed with {1} error in {2} test case".format(response.url,
                                                                                                         response.status_code,
                                                                                                         os.environ[
                                                                                                             'PYTEST_CURRENT_TEST']))
            if print_response:
                self.logger.info("################ EXITING GET BLOCK ###################")
            return response
        if self.validate_response and validate_response:
            self._validate_response(response)
        self.logger.info("################ EXITING GET BLOCK ###################")
        return response

    def delete(self, url,
               params=None,
               data=None,
               headers=None,
               cookies=None,
               files=None,
               auth=None,
               timeout=None,
               allow_redirects=True,
               proxies=None,
               hooks=None,
               stream=None,
               verify=None,
               cert=None,
               json=None,
               validate_response=True,
               **kwargs):
        """
        Delete wrapper to add on Central URL and print anomoly in the responses
        :param url: Request URL
        :param kwargs: Different params that requires to be passed in delete call
        :return: Returns the response as it is
        """
        if not params:
            q_param = {}
            kw = kwargs
            kwargs = {}
            for k, v in kw.items():
                q_param[k] = v
            params = q_param

        if verify == None:
            verify = self.verify

        # self.logger.info("############# INTO DELETE BLOCK ###############")
        # self.logger.info("REQUEST URL: %s" % (url))
        # self.logger.info("REQUEST DATA: %s" % (self._convert_payload(data)))
        # self.logger.info("REQUEST HEADERS: %s" % (self.session.headers))
        # self.logger.info("REQUEST COOKIES: %s" % (self.session.cookies.get_dict()))

        api_request_time = time.time()
        counter = 0
        while counter < 3:
            counter += 1
            try:
                r = self.session.delete(url,
                                               params=params,
                                               data=self._convert_payload(data),
                                               headers=headers,
                                               cookies=cookies,
                                               files=files,
                                               auth=auth,
                                               timeout=timeout,
                                               allow_redirects=allow_redirects,
                                               proxies=proxies,
                                               hooks=hooks,
                                               stream=stream,
                                               verify=verify,
                                               cert=cert,
                                               json=json,
                                               **kwargs)
                # r = copy.deepcopy(response)
                api_response_time = time.time() - api_request_time
                RestCore.nice_print_out(r, caller="", error=False, quiet=False, use_color=True, response_time=None)
                try:
                    if r.content:
                        r.json = RestCore.process_response_body(r.content)
                    else:
                        r.json = ''
                except UnicodeDecodeError:
                    r.json = r.content
                response = Response(r.status_code, r.json, RestCore.form_real_dict(r.headers), r.cookies.get_dict())

                if self.validate_response and validate_response:
                    self._validate_response(response)
                if int(api_response_time) >= 3:
                    self.logger.error("API REQUEST-RESPONSE TIME LIMIT EXCEEDED : {} sec".format(api_response_time))
            except Exception as e:
                r = e.args[0]
                self.logger.error("Exception occured : {}".format(r))
            if self.__recoverable(r, url, 'DELETE', counter):
                continue
            if self.validate_response and validate_response:
                self._validate_response(response)
            else:
                if response.status_code not in SUCCESS_CODES:
                    if 'PYTEST_CURRENT_TEST' in list(os.environ.keys()):
                        self.logger.info("NON_2XX:{0} url failed with {1} error in {2} test case".format(response.url,
                                                                                                         response.status_code,
                                                                                                         os.environ[
                                                                                                             'PYTEST_CURRENT_TEST']))

            self.logger.info("################ EXITING DELETE BLOCK ###################")
            return response
        if self.validate_response and validate_response:
            self._validate_response(response)
        self.logger.info("################ EXITING DELETE BLOCK ###################")
        return response

    def post(self, url,
             params=None,
             data=None,
             headers=None,
             cookies=None,
             files=None,
             auth=None,
             timeout=None,
             allow_redirects=True,
             proxies=None,
             hooks=None,
             stream=None,
             verify=None,
             cert=None,
             json=None,
             validate_response=True,
             **kwargs):
        """
        Post wrapper to add on Central URL and print anomoly in the responses
        :param url: Request URL
        :param kwargs: Different params that requires to be passed in post call
        :return: Returns the response as it is
        """
        if not params and kwargs != {}:
            print(kwargs)
            print(data)
            q_param = {}
            kw = kwargs
            kwargs = {}
            for k, v in kw.items():
                q_param[k] = v
            params = q_param

        if verify == None:
            verify = self.verify

        # self.logger.info("############# INTO POST BLOCK ###############")
        # self.logger.info("REQUEST URL: %s" % (url))
        # self.logger.info("REQUEST DATA: %s" % (self._convert_payload(data)))
        # self.logger.info("REQUEST HEADERS: %s" % (self.session.headers))
        # self.logger.info("REQUEST COOKIES: %s" % (self.session.cookies.get_dict()))

        api_request_time = time.time()
        counter = 0
        while counter < 3:
            counter += 1
            try:
                r = self.session.post(url,
                                             params=params,
                                             data=self._convert_payload(data),
                                             headers=headers,
                                             cookies=cookies,
                                             files=files,
                                             auth=auth,
                                             timeout=timeout,
                                             allow_redirects=allow_redirects,
                                             proxies=proxies,
                                             hooks=hooks,
                                             stream=stream,
                                             verify=verify,
                                             cert=cert,
                                             json=json,
                                             **kwargs)
                # r = copy.deepcopy(response)
                api_response_time = time.time() - api_request_time

                RestCore.nice_print_out(r, caller="", error=False, quiet=False, use_color=True, response_time=None)
                try:
                    if r.content:
                        r.json = RestCore.process_response_body(r.content)
                    else:
                        r.json = ''
                except UnicodeDecodeError:
                    r.json = r.content
                response = Response(r.status_code, r.json, RestCore.form_real_dict(r.headers), r.cookies.get_dict())

                if self.validate_response and validate_response:
                    self._validate_response(response)
                if int(api_response_time) >= 3:
                    self.logger.error("API REQUEST-RESPONSE TIME LIMIT EXCEEDED : {} sec".format(api_response_time))
            except Exception as e:
                r = e.args[0]
                self.logger.error("Exception occured : {}".format(r))
            if self.__recoverable(r, url, 'POST', counter):
                continue
            if self.validate_response and validate_response:
                self._validate_response(response)
            else:
                if response.status_code not in SUCCESS_CODES:
                    if 'PYTEST_CURRENT_TEST' in list(os.environ.keys()):
                        self.logger.info("NON_2XX:{0} url failed with {1} error in {2} test case".format(response.url,
                                                                                                         response.status_code,
                                                                                                         os.environ[
                                                                                                             'PYTEST_CURRENT_TEST']))

            self.logger.info("################ EXITING POST BLOCK ###################")
            return response
        if self.validate_response and validate_response:
            self._validate_response(response)
        self.logger.info("################ EXITING POST BLOCK ###################")
        return response

    def put(self, url,
            params=None,
            data=None,
            headers=None,
            cookies=None,
            files=None,
            auth=None,
            timeout=None,
            allow_redirects=True,
            proxies=None,
            hooks=None,
            stream=None,
            verify=None,
            cert=None,
            json=None,
            validate_response=True,
            **kwargs):
        """
        Put wrapper to add on Central URL and print anomoly in the responses
        :param url: Request URL
        :param kwargs: Different params that requires to be passed in put call
        :return: Returns the response as it is
        """
        if not params:
            q_param = {}
            kw = kwargs
            kwargs = {}
            for k, v in kw.items():
                q_param[k] = v
            params = q_param

        if verify == None:
            verify = self.verify

        # self.logger.info("############# INTO PUT BLOCK ###############")
        # self.logger.info("REQUEST URL: %s" % (url))
        # self.logger.info("REQUEST DATA: %s" % (self._convert_payload(data)))
        # self.logger.info("REQUEST HEADERS: %s" % (self.session.headers))
        # self.logger.info("REQUEST COOKIES: %s" % (self.session.cookies.get_dict()))

        api_request_time = time.time()
        counter = 0
        while counter < 3:
            counter += 1
            try:
                r = self.session.put(url,
                                            params=params,
                                            data=self._convert_payload(data),
                                            headers=headers,
                                            cookies=cookies,
                                            files=files,
                                            auth=auth,
                                            timeout=timeout,
                                            allow_redirects=allow_redirects,
                                            proxies=proxies,
                                            hooks=hooks,
                                            stream=stream,
                                            verify=verify,
                                            cert=cert,
                                            json=json,
                                            **kwargs)
                # r = copy.deepcopy(response)
                api_response_time = time.time() - api_request_time
                RestCore.nice_print_out(r, caller="", error=False, quiet=False, use_color=True, response_time=None)
                try:
                    if r.content:
                        r.json = RestCore.process_response_body(r.content)
                    else:
                        r.json = ''
                except UnicodeDecodeError:
                    r.json = r.content
                response = Response(r.status_code, r.json, RestCore.form_real_dict(r.headers), r.cookies.get_dict())

                if self.validate_response and validate_response:
                    self._validate_response(response)
                if int(api_response_time) >= 3:
                    self.logger.error("API REQUEST-RESPONSE TIME LIMIT EXCEEDED : {} sec".format(api_response_time))
            except Exception as e:
                r = e.args[0]
                self.logger.error("Exception occured : {}".format(r))
            if self.__recoverable(r, url, 'PUT', counter):
                continue
            if self.validate_response and validate_response:
                self._validate_response(response)
            self.logger.info("################ EXITING PUT BLOCK ###################")
            return response
        if self.validate_response and validate_response:
            self._validate_response(response)
        else:
            if response.status_code not in SUCCESS_CODES:
                if 'PYTEST_CURRENT_TEST' in list(os.environ.keys()):
                    self.logger.info("NON_2XX:{0} url failed with {1} error in {2} test case".format(response.url,
                                                                                                     response.status_code,
                                                                                                     os.environ[
                                                                                                         'PYTEST_CURRENT_TEST']))

        self.logger.info("################ EXITING PUT BLOCK ###################")
        return response

    def patch(self, url,
              params=None,
              data=None,
              headers=None,
              cookies=None,
              files=None,
              auth=None,
              timeout=None,
              allow_redirects=True,
              proxies=None,
              hooks=None,
              stream=None,
              verify=None,
              cert=None,
              json=None,
              validate_response=True,
              **kwargs):
        """
        Patch wrapper to add on Central URL and print anomoly in the responses
        :param url: Request URL
        :param kwargs: Different params that requires to be passed in patch call
        :return: Returns the response as it is
        """
        if not params:
            q_param = {}
            kw = kwargs
            kwargs = {}
            for k, v in kw.items():
                q_param[k] = v
            params = q_param

        if verify == None:
            verify = self.verify

        self.logger.info("############# INTO PATCH BLOCK ###############")
        self.logger.info("REQUEST URL: %s" % (url))
        self.logger.info("REQUEST DATA: %s" % (self._convert_payload(data)))
        self.logger.info("REQUEST HEADERS: %s" % (self.session.headers))
        self.logger.info("REQUEST COOKIES: %s" % (self.session.cookies.get_dict()))

        api_request_time = time.time()
        counter = 0
        while counter < 3:
            counter += 1
            try:
                r = self.session.patch(url,
                                              params=params,
                                              data=self._convert_payload(data),
                                              headers=headers,
                                              cookies=cookies,
                                              files=files,
                                              auth=auth,
                                              timeout=timeout,
                                              allow_redirects=allow_redirects,
                                              proxies=proxies,
                                              hooks=hooks,
                                              stream=stream,
                                              verify=verify,
                                              cert=cert,
                                              json=json,
                                              **kwargs)
                # r = copy.deepcopy(response)
                api_response_time = time.time() - api_request_time

                RestCore.nice_print_out(r, caller="", error=False, quiet=False, use_color=True, response_time=None)
                try:
                    if r.content:
                        r.json = RestCore.process_response_body(r.content)
                    else:
                        r.json = ''
                except UnicodeDecodeError:
                    r.json = r.content
                response = Response(r.status_code, r.json, RestCore.form_real_dict(r.headers), r.cookies.get_dict())

                if self.validate_response and validate_response:
                    self._validate_response(response)
                if int(api_response_time) >= 3:
                    self.logger.error("API REQUEST-RESPONSE TIME LIMIT EXCEEDED : {} sec".format(api_response_time))
            except Exception as e:
                r = e.args[0]
                self.logger.error("Exception occured : {}".format(r))
                if self.__recoverable(r, url, 'PATCH', counter):
                    continue
            if self.validate_response and validate_response:
                self._validate_response(response)
            self.logger.info("################ EXITING PATCH BLOCK ###################")
            return response
        if self.validate_response and validate_response:
            self._validate_response(response)
        else:
            if response.status_code not in SUCCESS_CODES:
                if 'PYTEST_CURRENT_TEST' in list(os.environ.keys()):
                    self.logger.info("NON_2XX:{0} url failed with {1} error in {2} test case".format(response.url,
                                                                                                     response.status_code,
                                                                                                     os.environ[
                                                                                                         'PYTEST_CURRENT_TEST']))

        self.logger.info("################ EXITING PATCH BLOCK ###################")
        return response

    def disconnect(self):
        self.session.close()

    @staticmethod
    def nice_print_out(r, caller, error=False, quiet=False, use_color=True, response_time=None):
        if quiet:
            return
        curl = RestCore.get_curl(r)
        if response_time is None:
            response_time_str = ''
        else:
            response_time_str = '\t# Response time = %0.3f secs' % response_time
        CustomLogger.printDebug(caller + '\n' + curl + response_time_str, error=error, use_color=use_color)
        CustomLogger.printDebug(caller + '\nResponse HTTP code: %s' % r.status_code, error=error, use_color=use_color)
        if 'Text' in r.headers:
            CustomLogger.printDebug(caller + '\nText header: "%s"' % r.headers['Text'],
                                    error=error, use_color=use_color)
        if len(r.content):
            try:
                CustomLogger.printDebug(caller + '\nResponse body:\n %s' % json.dumps(r.json(), indent=2, sort_keys=True),
                                        error=error, use_color=use_color)
            except TypeError:
                CustomLogger.printDebug(caller + '\nResponse body:\n %s' % r.json, error=error, use_color=use_color)
        else:
            CustomLogger.printDebug(caller + '\nNo body in the response.', error=error, use_color=use_color)
        if error:
            CustomLogger.printDebug(caller + '\nResponse headers:\n' + pprint.pformat(RestCore.form_real_dict(r.headers)),
                                    error=error, use_color=use_color)

    @staticmethod
    def get_curl(r):
        if 'users/sign_in' in r.request.url and isinstance(r.request.body, str):
            body_data = ast.literal_eval(r.request.body)
            body_data['user']['password'] = '<HIDDEN>'
            r.request.body = json.dumps(body_data, sort_keys=True)
        header_string = ''
        for key in r.request.headers:
            if key not in ['Accept-Encoding', 'Connection', 'User-Agent', 'Content-Length']:
                header_string += "-H '%s: %s' " % (key, r.request.headers[key])
        if r.request.body:
            curl = "curl -X %s '%s' -d '%s' %s" % (r.request.method, r.request.url, r.request.body, header_string)
        else:
            curl = "curl -X %s '%s' %s" % (r.request.method, r.request.url, header_string)
        return curl

    @staticmethod
    def form_real_dict(d):
        d1 = dict()
        for key in d:
            d1[key] = d[key]
        return d1

    @staticmethod
    def process_response_body(content):
        try:
            json_resp = json.loads(content.decode('utf-8'))
            return json_resp
        except ValueError:
            return content.decode('utf-8')

    @staticmethod
    def schema_data(schema):
        if type(schema) == voluptuous.Schema:
            data = {'Schema': RestCore.schema_data(schema.schema)}
        elif type(schema) == voluptuous.Object:
            data = RestCore.schema_dict(schema)
        elif type(schema) == dict:
            data = RestCore.schema_dict(schema)
        elif type(schema) == voluptuous.Required:
            data = {'Required': RestCore.schema_data(schema.schema)}
        elif type(schema) == voluptuous.Optional:
            data = {'Optional': RestCore.schema_data(schema.schema)}
        elif type(schema) == voluptuous.All:
            data = {'All': RestCore.schema_validators(schema)}
        elif type(schema) == voluptuous.Any:
            data = {'Any': RestCore.schema_validators(schema)}
        else:
            data = schema
        return data

    @staticmethod
    def schema_dict(schema):
        data = dict()
        for key, value in schema.items():
            if type(key) == voluptuous.Required:
                data['Required(' + str(key) + ')'] = RestCore.schema_data(value)
            elif type(key) == voluptuous.Optional:
                data['Optional(' + str(key) + ')'] = RestCore.schema_data(value)
            else:
                data[str(key)] = RestCore.schema_data(value)
        return data

    @staticmethod
    def schema_validators(schema):
        my_validators = []
        for v in schema.validators:
            my_validators.append(RestCore.schema_data(v))
        return tuple(my_validators)

    # @staticmethod
    # def schema_http_code(schema):
    #     for skey, svalue in schema.schema.items():
    #         if str(skey) == 'http_code':
    #             return svalue
    #     raise ArubaAutomationError('http_code not found in schema')


class ArubaHTTPError(Exception):

    def __init__(self, args):
        if type(args) is tuple:
            message, resp, r = args
            self.message = message
            self.http_code = resp.http_code
            self.body = resp.body
            self.headers = resp.headers
            self.cookie = resp.cookie
            self.url = r.request.url
            self.r = r
        else:
            self.raw_message = args

    def __str__(self):
        if hasattr(self, 'raw_message'):
            return self.raw_message
        else:
            if 'Text' in self.headers:
                text_header = '\nText Header: "%s"' % self.headers['Text']
            else:
                text_header = ''
            msg = '{}\nACTUAL:\n{}\nResponse HTTP code: {}{}\nResponse body:\n{}\nResponse headers:\n{}'.format(
                self.message, RestCore.get_curl(self.r), self.http_code, text_header, pprint.pformat(self.body),
                pprint.pformat(self.headers))
            return msg
