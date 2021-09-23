from __future__ import print_function

from future import standard_library

standard_library.install_aliases()
from builtins import str
from builtins import range

__author__ = 'rrkrishnan'

import platform

if platform.system() == "Darwin":
    import gevent.monkey

    # gevent.monkey.patch_all()
######## IMPORT STATEMENTS ############
import re
import json
import pprint
import requests
import lxml.html
import time
import os
from email_split import email_split
from six.moves.urllib.parse import urljoin, urlparse
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from libs.utils import LogModule as log
from libs.utils.RestCore import RestCore
########################################

# To turn off File Warnings
import warnings

warnings.filterwarnings('ignore')

# Remove unwanted requests package warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

logger = log.getLogger(__name__)


class AuthenticationException(Exception):
    """Wrapper class for AuthenticationException"""

    def __init__(self):
        Exception.__init__(self, "Authentication Failed, please check credentials!")


class CustomerNotFound(Exception):
    """Wrapper class for CustomerNotFound exception """

    def __init__(self, msg):
        Exception.__init__(self, msg)


class RestFrontEnd(RestCore):
    def __init__(self, host, user, password, customer_id=None, verify=False):
        """
        Class for Central UI REST interface
        :param host: Central URL
        :param user: Central Login Username
        :param password: Central Login Password
        :param customer_id: Central Customer ID
        :param verify: Flag to enable/disable cert verification
        """
        super(RestFrontEnd, self).__init__(verify=verify)
        self.logger = logger.getChild(self.__class__.__name__)
        self.host = host
        self.central_host = None
        self.portal_host = None
        self.user = user
        self.password = password
        self.loggedin = False
        self.csrfToken = ""
        self.customer_id = customer_id
        self.url = None
        self.credsEntered = False
        self.domain = None
        self.exception = ""
        self._connect()

    def _connect(self):
        for i in range(1, 3):
            try:
                self.connect()
                return
            except Exception as e:
                self.exception = e
                self.logger.exception('Got Exception while rest login: {}'.format(e))
                self.logger.warning('#Retry {} in {} seconds'.format(i, i * 10))
                time.sleep(i * 10)
                continue
        else:
            raise Exception('Unexpected Error while rest login')

    def _followUrl(self, response):
        """
        Internal api to follow the urls
        :param response: Basic Central URL response
        :return: Returns response after successful connection
        """
        html = lxml.html.fromstring(response.text)
        actionText = html.xpath('//form[@action]')
        if actionText:
            if actionText[0].attrib['action']:
                self.url = actionText[0].attrib['action']
                if ':443' in self.url:
                    self.url = re.sub(':443', "", self.url)
                if not self.url:
                    self.url = response.url + "/aruba/sso"
                if "startSSO.ping" in self.url:
                    self.url = response.url
                action = actionText[0].attrib['method']
                formInputs = html.xpath('//form//input')
                form = {}

                for formInput in formInputs:
                    if "name" not in list(formInput.attrib.keys()):
                        continue
                    else:
                        if formInput.attrib['type'] == "text":
                            form[formInput.attrib['name']] = self.user
                        elif formInput.attrib['type'] == "email":
                            form[formInput.attrib['name']] = self.user
                        elif formInput.attrib['type'] == "password":
                            if "Authentication Failed" not in str(self.exception):
                                self.credsEntered = False
                            if self.credsEntered:
                                self.logger.error("Login to Rest Failed...")
                                raise AuthenticationException()
                            form[formInput.attrib['name']] = self.password
                            self.credsEntered = True
                        else:
                            if formInput.attrib.get('value'):
                                form[formInput.attrib['name']] = formInput.attrib['value']
                            try:
                                if '/global_login/login/login/' in str(form['RelayState']):
                                    relay = re.sub('/global_login/login/login/', '/global_login/login/',
                                                   form['RelayState'])
                                    form['RelayState'] = relay
                                    self.logger.info("RelayState found in the form")
                            except:
                                self.logger.error("No RelayState in the form")
                if not self.portal_host and (
                        self.url.find("/platform/login/user") > -1 or self.url.find("/global_login/aaa_saml") > -1):
                    pl_url = self.url.rsplit('/', 1)[0]
                    self.portal_host = '{uri.scheme}://{uri.netloc}/'.format(uri=urlparse(pl_url))
                # prefix domain if required
                if action.lower() == "post":
                    if self.domain != None:
                        aaaurl = "https://" + self.domain + self.url
                        self.logger.debug("Action : %s, URL : %s" % (action, aaaurl))
                        r = self.session.post(aaaurl, data=form, timeout=60, verify=False)
                        self.logger.info('Cookie dict after POST action with domain: {}'
                                         .format(self.session.cookies.get_dict()))
                        self.domain = None
                    else:
                        self.logger.debug("Action : %s, URL : %s" % (action, self.url))
                        r = self.session.post(self.url, data=form, timeout=60, verify=False)
                        self.logger.info('Cookie dict after POST action without domain: {}'
                                         .format(self.session.cookies.get_dict()))

                    # Password policy handling
                    if r.text.find("Your Password will expire") > -1:
                        html = lxml.html.fromstring(r.text)
                        metaTag = html.xpath('//meta')
                        content = metaTag[0].attrib['content']
                        contUrl = content.split(";")[1].split("=")[1]
                        self.logger.warn("Password is going to expire..Continuing to login to '%s'" % (contUrl))
                        r = self.session.post(contUrl, data=None, timeout=60, verify=False)

                    if "Sorry! We didn't recognize the username or password \
                        you entered. Please try again" in r.text or "Authentication Failed" in r.text:
                        self.logger.error("Login to Rest Failed...")
                        raise AuthenticationException()
                    return (r)
            else:
                formInp = html.xpath('//form//input')
                csrftoken = formInp[0].attrib['value']
                form = {}
                form["csrf_token"] = csrftoken
                form["admin"] = self.user
                form["password"] = self.password
                self.logger.info("Action : %s, URL : %s" % ('post', response.url))
                r = self.session.post(response.url, data=form, verify=False)
                self.logger.info('Cookie dict post aruba sso action: {}'.format(self.session.cookies.get_dict()))
                return (r)
        else:
            finput = html.xpath('//form//input')
            if finput and finput[0].attrib["onkeyup"] == "validateAndSubmit(this, event);":
                form = {}
                form["pf.username"] = self.user
                email = email_split(self.user)
                if email.domain == "adfsaruba.com":
                    params = dict()
                    params['sso'] = "None"
                    params['target_url'] = response.url[
                                           :len(response.url) - 20] + "/global_login/login/aaa/post_saml_auth"
                    rurl = response.url[:len(response.url) - 20] + '/global_login'
                    self.domain = email.domain
                    temp_url = rurl + "/aaa_saml/" + email.domain
                    self.logger.info("Action : %s, URL : %s" % ('post', temp_url))
                    r = self.session.post(temp_url, params=params, verify=False)
                    html = lxml.html.fromstring(r.text)
                    actionText = html.xpath('//form[@action]')
                    redurl = "https://" + email.domain + actionText[0].attrib['action']
                    self.logger.info("Action : %s, URL : %s" % ('post', redurl))
                    ffrom = {}
                    ffrom['HomeRealmSelection'] = "AD AUTHORITY"
                    ffrom['Email'] = ""
                    r = self.session.post(redurl, data=ffrom, verify=False)
                else:
                    self.logger.info("Action : %s, URL : %s" % ('post', response.url))
                    if response.url.find("/platform/login/user") > -1:
                        pl_url = response.url.rsplit('/', 1)[0]
                        self.portal_host = '{uri.scheme}://{uri.netloc}/'.format(uri=urlparse(pl_url))
                        r = self.session.post(pl_url + "/aruba/sso", data=form, verify=False)
                    else:
                        r = self.session.post(response.url + "/aruba/sso", data=form, verify=False)
                    self.logger.info('Cookie dict post aruba sso action: {}'.format(self.session.cookies.get_dict()))
                return (r)

        self.finalHostUrl = response.url
        return None

    def connect(self):
        """
        Create a Central UI REST session
        :return: Returns True/False
        """
        count = 1
        response = self.session.get(self.host, timeout=60, verify=False)
        while response:
            response = self._followUrl(response)
            if response:
                self.logger.info('Response from followUrl {}'.format(response.status_code))
            if response == False or count > 19:
                return False
            count = count + 1
        cookieDict = self.session.cookies.get_dict()
        self.logger.info('Cookie Dict after getting session: {}'.format(cookieDict))

        if self.finalHostUrl.find("central_manager") > -1:
            if "session" not in cookieDict:
                self.logger.info("Login to Central_Manager Failed")
                return False
            self.loggedin = True
            # Update the host url
            expression = re.compile("(.*//.*/).*/.*")
            self.host = expression.match(self.finalHostUrl).group(1)
            self.logger.info("Login to Central_Manager Successful")
            return True
        if self.finalHostUrl.find("swagger") > -1:
            if "session" not in cookieDict:
                self.logger.info("Login to Swagger Failed")
                return False
            self.loggedin = True
            expression = re.compile("(.*//.*/).*/.*")
            self.host = expression.match(self.finalHostUrl).group(1)
            self.logger.info("Login to Swagger Successful")
            return True
        if "redirect" in self.finalHostUrl:
            temp_host = "{}://{}".format(urlparse(self.finalHostUrl).scheme, urlparse(self.finalHostUrl).netloc)
            response = self.session.get("{}/{}".format(temp_host, "platform/login/customers"))
            self.logger.info('Cookies after getting users_customers: {}'
                             .format(self.session.cookies.get_dict()))
            selectedCustomer = None
            custList = []
            for customer in response.json()["customers_list"]:
                custList.append(customer["id"])
                if isinstance(self.customer_id, int):
                    if int(customer["id"]) == self.customer_id or \
                            customer["id"] == self.customer_id:
                        selectedCustomer = {"cid": self.customer_id}
                        break
                else:
                    if customer["id"] == self.customer_id:
                        selectedCustomer = {"cid": self.customer_id}
                        break
            if not selectedCustomer:
                if self.customer_id != None:
                    errMsg = "Customer '%s' not found in customer list %s" % (
                        self.customer_id, pprint.pformat(custList))
                else:
                    errMsg = "More than one customer found %s, Please provide customer id..." % (
                        pprint.pformat(custList))
                self.logger.error(errMsg)
                raise CustomerNotFound(errMsg)
            else:
                self.logger.info('Cookie dict before select_services: {}'.format(self.session.cookies.get_dict()))
                response = self.session.post(
                    temp_host + "/platform/login/customers/selection",
                    data=json.dumps(selectedCustomer), headers={"Content-Type": "application/json"})
                response = self.session.post(response.json()["redirect_url"])
                self.finalHostUrl = response.url
            cookieDict = self.session.cookies.get_dict()
            self.csrfToken = cookieDict["csrftoken"]
        else:
            self.csrfToken = cookieDict.get("csrftoken")

        if "/platform" in self.finalHostUrl:
            response = self.session.get(self.portal_host + "/platform/login/apps/nms/launch")
            self.logger.info(response.url)
            self.finalHostUrl = response.url
            self.logger.info('Cookies after launching NMS app: {}'
                             .format(self.session.cookies.get_dict()))

        if not self.csrfToken:
            return False

        # Update the host url
        expression = re.compile("(.*//.*/).*/.*")
        self.central_host = expression.match(self.finalHostUrl).group(1)

        self.loggedin = True
        self.switch_to_app("nms")

        self.logger.info('Request Header: {}'.format(self.session.headers))
        self.logger.info('Request Cookies: {}'.format(self.session.cookies.get_dict()))
        self.logger.info("Login to Rest Successful")
        self.logger.info('Getting user details after login')
        # self.get("users/details")
        return True

    def switch_to_app(self, appname):
        '''
        appname: specified app session needed for user
        '''

        try:
            input_var = os.getenv('INPUT_JSON')
            cluster_type = json.loads(input_var)['cluster_type']
        except Exception as e:
            self.logger.exception('Got Exception while retrieving cluster type: {}'.format(e))
            self.logger.info('Retrieving Cluster type failed.Proceeding to central workflow')
            cluster_type = ''

        if cluster_type == 'aw10':
            if appname == "platform":
                self.logger.info("Returns Host url of platform in CoP")
                self.host = self.central_host
                url = 'platform/frontend'
                self.logger.info(self.host + url)
                self.session.get(self.host + url)
            elif appname == "nms":
                self.logger.info("Returns Host url of NMS in CoP")
                self.host = self.central_host
                url = '/frontend'
                self.logger.info(self.host + url)
                self.session.get(self.host + url)
                self.logger.info("Central Host : {}".format(self.host))
            else:
                self.logger.error("APP name given is Incorrect...!")
                return False
        else:
            if appname == "platform":
                self.logger.info("Returns Host url of platform")
                self.host = self.portal_host
            elif appname == "nms":
                self.logger.info("Returns Host url of NMS")
                self.host = self.central_host
                self.logger.info("Central Host : {}".format(self.host))
            else:
                self.logger.error("APP name given is Incorrect...!")
                return False

        self.session.headers = {
            "X-CSRF-Token": self.session.cookies.get("csrftoken", domain=urlparse(self.host).netloc),
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/json",
            "referer": self.host
        }
        return True

    def get_headers(self):
        return self.session.headers

    def get_cookies(self):
        return self.session.cookies.get_dict()

    def get(self, url, **kwargs):
        """
        Get wrapper to add on Central URL and print anomoly in the responses
        :param url: Request URL
        :param kwargs: Different params that requires to be passed in get call
        :return: Returns the response as it is
        """
        response = super(RestFrontEnd, self).get(urljoin(self.host, url), **kwargs)
        return response

    def delete(self, url, **kwargs):
        """
        Delete wrapper to add on Central URL and print anomoly in the responses
        :param url: Request URL
        :param kwargs: Different params that requires to be passed in delete call
        :return: Returns the response as it is
        """
        response = super(RestFrontEnd, self).delete(urljoin(self.host, url), **kwargs)
        return response

    def post(self, url, **kwargs):
        """
        Post wrapper to add on Central URL and print anomoly in the responses
        :param url: Request URL
        :param kwargs: Different params that requires to be passed in post call
        :return: Returns the response as it is
        """
        response = super(RestFrontEnd, self).post(urljoin(self.host, url), **kwargs)
        return response

    def put(self, url, **kwargs):
        """
        Put wrapper to add on Central URL and print anomoly in the responses
        :param url: Request URL
        :param kwargs: Different params that requires to be passed in put call
        :return: Returns the response as it is
        """
        response = super(RestFrontEnd, self).put(urljoin(self.host, url), **kwargs)
        return response

    def patch(self, url, **kwargs):
        """
        Patch wrapper to add on Central URL and print anomoly in the responses
        :param url: Request URL
        :param kwargs: Different params that requires to be passed in patch call
        :return: Returns the response as it is
        """
        response = super(RestFrontEnd, self).patch(urljoin(self.host, url), **kwargs)
        return response

    def disconnect(self):
        """
        Disconnects the rest session
        :return:
        """
        super(RestFrontEnd, self).disconnect()

#
# if __name__ == "__main__":
#     log.configure(logger.name, console=True, debug=True)
#     # sess = RestFrontEnd(host="https://malshi-central-ui.arubathena.com",
#     #                   user="cloud.putty+xxx_auto_zzz_102343321_14@gmail.com",
#     #                   password="Aruba@123", customer_id=30025398)
#
#     # sess = RestFrontEnd(host="https://app-yoda.arubathena.com",
#     #                   user="urlsanity.automation+yoda@gmail.com",
#     #                   password="Aruba@123", customer_id=201804170008)
#     # sess = RestFrontEnd(host="https://app-yoda.arubathena.com",
#     #                     user="test01@adfsaruba.com",
#     #                     password="Aruba@123", customer_id=201804170066)
#     # sess = RestFrontEnd(host="https://portal-yoda.arubathena.com",
#     #                   user="nbapi.automation+yoda@gmail.com",
#     #                   password="Aruba@12345", customer_id="a476938aad134767929e5b12a3c82204")
#     sess = RestFrontEnd(host="https://sol-thd-portal.arubathena.com",
#                         user="cloud.putty+sol_thd_auto_test@gmail.com",
#                         password="Aruba@123", customer_id="111952317")
#     # sess = RestFrontEnd(host="https://portal-yoda.arubathena.com",
#     #                   user="cloud.putty+xxx_auto_zzz_260720191132_14@gmail.com",
#     #                   password="Aruba@123", customer_id="11a24e48b4764aa790e4a342dadffaa1")
#     ##sess = RestFrontEnd(host="https://app-smoke2qa.arubathena.com",
#     #                    user="smoke.automation.central+smoke2qa_nonmsp@gmail.com",
#     #                    password="Aruba@123")
#     print(sess.get(
#         "/monitor/overview/counts?timeStamp=1517509291647").json())
