# """
# curl -X POST -u admin:11f7c27a2e0b65dcd0581bc69fb6668d27 http://localhost:8080/job/parameterised_job1/buildWithParameters\?param1\=siba\&param2\=mohanta
# """
#
# import time
# import ast
# import inspect
# import json
# import logging
# from pprint import pformat
# import requests
# import voluptuous
# from datetime import datetime
#
# from utils.aruba_automation_config import ArubaAutomationError
# from utils.customer_logger import CustomLogger
#
# PREV_REQUEST = None
#
#
# class Response:
#
#     def __init__(self, http_code, body, headers, cookie):
#         self.http_code = http_code
#         self.body = body
#         self.headers = headers
#         self.cookie = cookie
#
#     def header_length(self):
#         """Get the length of the header
#
#         Returns:
#             The length of the header of a response
#         """
#         return len(json.dumps(self.headers))
#
#
# class Request:
#
#     def __init__(self):
#         pass
#
#     @staticmethod
#     def save_request(*args, **kwargs):
#         global PREV_REQUEST
#         PREV_REQUEST = (args, kwargs)
#
#     @staticmethod
#     def get_prev_request():
#         return PREV_REQUEST
#
#     @staticmethod
#     def request(url, method, caller=None, token=None, cookie=None, body=None, headers=None, params=None,
#                 content_type=None, accept=None, validate=False, schema=None, files=None, quiet=False, auth=None,
#                 session=None, use_color=True, verify=None, retries=0, benchmark=False):
#
#         Request.save_request(url, method, caller=caller, token=token, cookie=cookie, body=body, headers=headers,
#                              params=params, content_type=content_type, accept=accept, validate=validate,
#                              schema=schema, files=files, quiet=quiet, auth=auth, session=session, use_color=use_color,
#                              verify=verify, retries=retries, benchmark=benchmark)
#
#         if caller is None:
#             current_frame = inspect.currentframe()
#             caller_frame = inspect.getouterframes(current_frame, 2)
#             caller = caller_frame[1][3]
#             del current_frame
#             del caller_frame
#         if cookie:
#             cookie = cookie
#         if content_type is None:
#             content_type = 'application/json'
#         if body is None:
#             body = ''
#         elif content_type == "application/octet-stream":
#             body = body
#         elif content_type == 'application/json' and len(body) >= 0:
#             body = json.dumps(body, sort_keys=True)
#         elif content_type == 'multipart/form-data':
#             body = body
#             content_type = None
#         if headers is None:
#             headers = dict()
#         if params is None:
#             params = ''
#         if accept is None:
#             accept = 'application/json'
#         if token is not None:
#             headers['auth_token'] = '%s' % token
#         headers['Content-Type'] = content_type
#         headers['Accept'] = accept
#         logging.getLogger('requests').setLevel(logging.WARNING)
#         while True:
#             start_time = datetime.now()
#             if session:
#                 r = session.request(
#                     url=url,
#                     method=method,
#                     data=body,
#                     headers=headers,
#                     params=params,
#                     cookies=cookie,
#                     files=files,
#                     auth=auth,
#                     verify=verify
#                 )
#             else:
#                 r = requests.request(
#                     url=url,
#                     method=method,
#                     data=body,
#                     headers=headers,
#                     params=params,
#                     cookies=cookie,
#                     files=files,
#                     auth=auth,
#                     verify=verify
#                 )
#             end_time = datetime.now()
#             if benchmark:
#                 response_time = (end_time - start_time).total_seconds()
#             else:
#                 response_time = None
#             try:
#                 if r.content:
#                     r.json = Request.process_response_body(r.content)
#                 else:
#                     r.json = ''
#             except UnicodeDecodeError:
#                 r.json = r.content
#             response = Response(r.status_code, r.json, Request.form_real_dict(r.headers), r.cookies.get_dict())
#             if schema:
#                 schema_http_code = Request.schema_http_code(schema)
#                 error = r.status_code != schema_http_code and validate
#             else:
#                 error = r.status_code >= 400 and validate
#             exception_message = ''
#             exception = None
#             if error:
#                 exception_message = 'Unexpected HTTP code {}'.format(r.status_code)
#                 exception = ArubaHTTPError((exception_message, response, r))
#             elif validate and schema:
#                 try:
#                     schema(response)
#                 except voluptuous.Error as e:
#                     error = True
#                     schema_data = Request.schema_data(schema)
#                     exception_message = str(type(e)) + ': ' + str(e) + '\nEXPECTED:\n' + pformat(schema_data, width=140)
#                     exception = ArubaHTTPError((exception_message, response, r))
#             Request.nice_print_out(r=r, caller=caller, error=error, quiet=quiet, use_color=use_color,
#                                    response_time=response_time)
#             if error and exception:
#                 logging.error(exception_message)
#                 if r.status_code in [502, 503, 504, 429] and retries > 0:
#                     if r.status_code == 429:
#                         logging.error('Waiting 5 seconds after getting 429 - Too Many Requests')
#                         time.sleep(5)  # 429 = "Too Many Requests", so delay
#                     logging.error('Retrying... {} retries left'.format(retries))
#                     retries -= 1
#                     continue
#                 raise exception
#             break
#         response.headers['automation_response_time'] = str(r.elapsed.total_seconds())
#         return response
#
#     @staticmethod
#     def general_request(url, method, **kwargs):
#         """ This method use for returning plain vanilla response object which includes more fields like URL, history etc
#             without any schema validation
#             purpose = /oauth/authorize API where response does redirection to URL and generates authentication_code
#         """
#         response = requests.request(method=method, url=url, **kwargs)
#         return response
#
#     @staticmethod
#     def form_real_dict(d):
#         d1 = dict()
#         for key in d:
#             d1[key] = d[key]
#         return d1
#
#     @staticmethod
#     def nice_print_out(r, caller, error=False, quiet=False, use_color=True, response_time=None):
#         if quiet:
#             return
#         curl = Request.get_curl(r)
#         if response_time is None:
#             response_time_str = ''
#         else:
#             response_time_str = '\t# Response time = %0.3f secs' % response_time
#         CustomLogger.printDebug(caller + '\n' + curl + response_time_str, error=error, use_color=use_color)
#         CustomLogger.printDebug(caller + '\nResponse HTTP code: %s' % r.status_code, error=error, use_color=use_color)
#         if 'Text' in r.headers:
#             CustomLogger.printDebug(caller + '\nText header: "%s"' % r.headers['Text'],
#                                     error=error, use_color=use_color)
#         if len(r.content):
#             try:
#                 CustomLogger.printDebug(caller + '\nResponse body:\n %s' % json.dumps(r.json, indent=2, sort_keys=True),
#                                         error=error, use_color=use_color)
#             except TypeError:
#                 CustomLogger.printDebug(caller + '\nResponse body:\n %s' % r.json, error=error, use_color=use_color)
#         else:
#             CustomLogger.printDebug(caller + '\nNo body in the response.', error=error, use_color=use_color)
#         if error:
#             CustomLogger.printDebug(caller + '\nResponse headers:\n' + pformat(Request.form_real_dict(r.headers)),
#                                     error=error, use_color=use_color)
#
#     @staticmethod
#     def get_curl(r):
#         if 'users/sign_in' in r.request.url and isinstance(r.request.body, str):
#             body_data = ast.literal_eval(r.request.body)
#             body_data['user']['password'] = '<HIDDEN>'
#             r.request.body = json.dumps(body_data, sort_keys=True)
#         header_string = ''
#         for key in r.request.headers:
#             if key not in ['Accept-Encoding', 'Connection', 'User-Agent', 'Content-Length']:
#                 header_string += "-H '%s: %s' " % (key, r.request.headers[key])
#         if r.request.body:
#             curl = "curl -X %s '%s' -d '%s' %s" % (r.request.method, r.request.url, r.request.body, header_string)
#         else:
#             curl = "curl -X %s '%s' %s" % (r.request.method, r.request.url, header_string)
#         return curl
#
#     @staticmethod
#     def process_response_body(content):
#         try:
#             json_resp = json.loads(content.decode('utf-8'))
#             return json_resp
#         except ValueError:
#             return content.decode('utf-8')
#
#     @staticmethod
#     def schema_data(schema):
#         if type(schema) == voluptuous.Schema:
#             data = {'Schema': Request.schema_data(schema.schema)}
#         elif type(schema) == voluptuous.Object:
#             data = Request.schema_dict(schema)
#         elif type(schema) == dict:
#             data = Request.schema_dict(schema)
#         elif type(schema) == voluptuous.Required:
#             data = {'Required': Request.schema_data(schema.schema)}
#         elif type(schema) == voluptuous.Optional:
#             data = {'Optional': Request.schema_data(schema.schema)}
#         elif type(schema) == voluptuous.All:
#             data = {'All': Request.schema_validators(schema)}
#         elif type(schema) == voluptuous.Any:
#             data = {'Any': Request.schema_validators(schema)}
#         else:
#             data = schema
#         return data
#
#     @staticmethod
#     def schema_dict(schema):
#         data = dict()
#         for key, value in schema.items():
#             if type(key) == voluptuous.Required:
#                 data['Required(' + str(key) + ')'] = Request.schema_data(value)
#             elif type(key) == voluptuous.Optional:
#                 data['Optional(' + str(key) + ')'] = Request.schema_data(value)
#             else:
#                 data[str(key)] = Request.schema_data(value)
#         return data
#
#     @staticmethod
#     def schema_validators(schema):
#         my_validators = []
#         for v in schema.validators:
#             my_validators.append(Request.schema_data(v))
#         return tuple(my_validators)
#
#     @staticmethod
#     def schema_http_code(schema):
#         for skey, svalue in schema.schema.items():
#             if str(skey) == 'http_code':
#                 return svalue
#         raise ArubaAutomationError('http_code not found in schema')
#
#
# class ArubaHTTPError(Exception):
#
#     def __init__(self, args):
#         if type(args) is tuple:
#             message, resp, r = args
#             self.message = message
#             self.http_code = resp.http_code
#             self.body = resp.body
#             self.headers = resp.headers
#             self.cookie = resp.cookie
#             self.url = r.request.url
#             self.r = r
#         else:
#             self.raw_message = args
#
#     def __str__(self):
#         if hasattr(self, 'raw_message'):
#             return self.raw_message
#         else:
#             if 'Text' in self.headers:
#                 text_header = '\nText Header: "%s"' % self.headers['Text']
#             else:
#                 text_header = ''
#             msg = '{}\nACTUAL:\n{}\nResponse HTTP code: {}{}\nResponse body:\n{}\nResponse headers:\n{}'.format(
#                 self.message, Request.get_curl(self.r), self.http_code, text_header, pformat(self.body),
#                 pformat(self.headers))
#             return msg
