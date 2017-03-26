#!/usr/bin/env python3
# coding=utf-8

"""Module to handle operation on the 1&1 Control Panel"""

import urllib
import ssl
import http.cookiejar
import sys

from lxml import html

import oneandoneemailconfig

class EmailAccountManager(object):
    """Class to manipulate amil accounts on 1&1 Control Panel"""

    userAgent = 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:51.0)'\
        ' Gecko/20100101 Firefox/51.0'  # User agent used during HTTP request

    isLogged = False  # Store the login state
    account_list = None  # Store the account list when first used
    accountCached = False  # True if the account list has been cached

    # Define the mail account types
    MAIL = 1
    REDIRECT = 2
    MAILBUSINESS = 3
    RESOURCE = 4
    MAILINGLIST = 5
    EXCHANGE = 6
    TYPES = ['None', 'MAIL', 'REDIRECT', 'MAILBUSINESS', 'RESOURCE', 'MAILINGLIST', 'EXCHANGE']

    def __init__(self, username, password, provider):
        """Construstor used to init the config and authenticate"""
        self.config = oneandoneemailconfig.OneAndOneConfig(provider)
        self.url = self.config.get_config()
        self.account_cached = False

        self.oneandoneuser = username
        self.onenandonepassword = password
        self.headers = {'User-Agent': EmailAccountManager.userAgent}
        self.cookies = http.cookiejar.LWPCookieJar()
        handlers = [
            urllib.request.HTTPHandler(),
            urllib.request.HTTPSHandler(),
            urllib.request.HTTPCookieProcessor(self.cookies)
        ]
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPSHandler(context=ctx), *handlers)
        self.is_logged = self.authenticate()

    def authenticate(self):
        """Authenticate to the 1&1 Control Panel"""
        # get cookie from login page
        self.do_request(self.url['loginURL'], None, None)

        loginformdata = {
            "__sendingdata": 1,
            "oaologin.password": self.onenandonepassword,
            "oaologin.username": self.oneandoneuser
        }

        response = self.do_request(self.url['loginURL'], None, loginformdata)
        responsebody = response['body']

        # Check if we are really logged in
        if "/Logout" in responsebody:
            print('Authentication successfull !')
            result = True
        else:
            self.error('Authentication failed !\n')
            result = False
        return result

    def create_account(self, data):
        """Create an email account using the parameters in data"""
        # Set the form data
        emaildomainname = data['domainname']
        emailusername = data['emailusername']
        emaildisplayname = data['emaildisplayname']
        emailfirstname = data['emailfirstname']
        emaillastname = data['emaillastname']
        emailpassword = data['emailpassword']
        emailtype = data['emailtype']
        emailaccount = "%s@%s" % (emailusername, emaildomainname)

        if self.get_account_type_id(emailtype) == self.MAIL:
            new_account_data = {"__lf": "create-basic-email-flow",
                                "create-basic.type": "MAILACCOUNT_STANDARD",
                                "create-basic.isOrderRequired": "false",
                                "create-basic.email": emailusername,
                                "create-basic.domain": emaildomainname,
                                "create-basic.firstName": emailfirstname,
                                "create-basic.lastName": emaillastname,
                                "create-basic.password": emailpassword,
                                "create-basic.repeatPassword": emailpassword,
                                "__sendingdata": 1,
                                "__SBMT:d0e8796d2:": ""}

            # Set the message data
            str_data = {'emailaccount': emailaccount}

            response = self.do_request(self.url['createEmailURL'],
                                       None, new_account_data)
            responsebody = response['body']

            # Check if the email account has been created
            if emailaccount in responsebody:
                print('Account {emailaccount} created successfully'
                      .format(**str_data))
            else:
                self.error('ERROR : Unable to create account {emailaccount}\n\t'
                           'Unknown Error\n'.format(**str_data))
        else:
            str_data = {'emailaccount': emailaccount}
            self.error('ERROR : sorry but only Mail accounts are supported '
                       'yet !\n\t{emailaccount} will not be created !\n'
                       .format(**str_data))

    @classmethod
    def error(cls, error_message):
        """Display an error message on the standard error output"""
        sys.stderr.write(error_message)

    @classmethod
    def format_url(cls, url, data):
        """Transform placeholder in predefined URL using the data content
        and return it as a string"""
        return url.format(**data)

    def do_request(self, url, url_data, post_data):
        """Do a request to an url, using the content of url_data to replace the
            URL placeholder and create a POST request if post_data is present.
            It return the response URL, content, and a reference to the whole
            response"""
        # Encode the POST parameters if needed
        if post_data is not None:
            data = urllib.parse.urlencode(post_data).encode()
        else:
            data = None

        # Replace the placeholder in the URL if needed
        if url_data is not None:
            url = self.format_url(url, url_data)

        # Do the request
        request = urllib.request.Request(url, data, self.headers)
        response = self.opener.open(request)
        return {'url': response.geturl(), 'body': response.read().decode(),
                'self': response}

    def get_page_count(self, url_data):
        """Count the number of pages of the account list"""
        response = self.do_request(self.url['pageCountURL'],
                                   url_data, None)
        responsebody = response['body']
        # If the cast in int fails, then there is only one page
        try:
            tree = html.fromstring(responsebody)
            page_count = tree.xpath(
                '//ul[@class="content-pagination pagination-a1"]'
                '/@data-total-pages')[0]
            return int(page_count)
        except Exception:
            return 1

    def get_account_list(self):
        """Get the whole account list from the Control Panel as a dict
            The format is a dict with the email as key and a list with the
            identifier and the account type as value :
            Example : {'email@domain.com': {'id': 123456789, 'type': 1}}
        """

        # We only ask the Control Panel if we did not already get the
        # account list
        if self.accountCached is False:
            account_list = {}
            size = 100
            page = 1

            url_data = {'size': size, 'page': page}

            # Check the number of page to check, and add every page content
            # to the list
            page_count = self.get_page_count(url_data)
            for page in range(1, page_count + 1):
                url_data = {'size': size, 'page': page}
                response = self.do_request(self.url['listEmailURL'],
                                           url_data, None)
                responsebody = response['body']

                # Get the mails name and associated id using xpath
                tree = html.fromstring(responsebody)
                mails = tree.xpath(
                    '//a[@class="email-address headline-c1"]/text()')
                ids = tree.xpath(
                    '//a[@class="email-address headline-c1"]/@href')
                types = tree.xpath(
                    '//tr/td[2]/span[contains(@class, "markup-before")]/@class')
                #print(types)
                #print(ids)

                for index in range(0, len(mails)):
                    page_name = ids[index].split('?', 1)[0]

                    if page_name == '/Email_Summary':
                        sub_type = types[index]
                        if 'forward' in sub_type:
                            account_type = self.REDIRECT
                        elif 'webmail' in sub_type:
                            account_type = self.MAIL
                        elif 'mailxchange' in sub_type:
                            account_type = self.MAILBUSINESS
                    elif page_name == '/OxResourceEdit':
                        account_type = self.RESOURCE
                    elif page_name == '/MailinglistNGMemberShow':
                        account_type = self.MAILINGLIST
                    elif page_name == '/MsexchangeUpdate':
                        account_type = self.EXCHANGE
                    account_list[mails[index]] = {
                        'id' : ids[index].split('=', 1)[1],
                        'type' : account_type}

            self.account_list = account_list
            self.account_cached = True
        else:
            account_list = self.account_list

        return account_list

    def get_account_type_by_id(self, ident):
        """Return the Account Type using the account ID"""
        accounts = self.get_account_list()
        email = self.get_email_by_id(ident)
        account_type = accounts[email]['type']
        return account_type


    def get_email_by_id(self, ident):
        """Returns the email using the ID"""
        accounts = self.get_account_list()
        for key, value in accounts.items():
            if value['id'] == ident:
                email = key

        return email

    @classmethod
    def get_email_domain(cls, email):
        """Return the domain of an email"""
        return email.split('@')[1]

    @classmethod
    def get_email_user(cls, email):
        """Return the user of an email"""
        return email.split('@')[0]


    def get_account_details(self, ident):
        """Get the account Details (First Name, Last Name, Full Name,
        Account Type, Password)
            Note: Password is not diplayed in the Control Panel, therefore
            the password is filled with stars"""

        account_type = self.get_account_type_by_id(ident)

        # Gather infos from basic mails
        if account_type in {self.MAIL, self.MAILBUSINESS, self.REDIRECT}:


            url_data = {'id': ident}
            response = self.do_request(self.url['accountDetailsURL'],
                                       url_data, None)
            responsebody = response['body']

            tree = html.fromstring(responsebody)

            # Find all the needed data using xpath
            email = self.array_to_string(
                tree.xpath('//*[@id="mamba-group-adresssummary"]/div[2]/table/'
                           'tbody/tr/td[2]/text()'))
            domainname = self.get_email_domain(email)
            emailusername = self.get_email_user(email)
            #accounttype = self.array_to_string(
            #    tree.xpath('/html/body/div[1]/div[3]/div/div/form/div/div[2]'
            #               '/div[2]/div[2]/table[1]/tbody/table/tr[1]/td[1]/span'
            #               '/text()'))

            # Get all the names if this is not a redirect
            if account_type != self.REDIRECT:
                emailfirstname = self.array_to_string(
                    tree.xpath('/html/body/div[1]/div[3]/div/div/form/div/div[2]'
                               '/div[2]/div[2]/table/tbody/table/tr[2]/td/text()'))
                emaillastname = self.array_to_string(
                    tree.xpath('/html/body/div[1]/div[3]/div/div/form/div/div[2]'
                               '/div[2]/div[2]/table/tbody/table/tr[3]/td/text()'))
                emaildisplayname = self.array_to_string(
                    tree.xpath('/html/body/div[1]/div[3]/div/div/form/div/div[2]'
                               '/div[2]/div[2]/table/tbody/table/tr[4]/td/text()'))
                emailpassword = self.array_to_string(
                    tree.xpath('/html/body/div[1]/div[3]/div/div/form/div/div[2]'
                               '/div[2]/div[2]/table/tbody/table/tr[6]/td[1]'
                               '/span/text()'))
            # Else we fill them with blanks
            else:
                emailfirstname = ''
                emaillastname = ''
                emaildisplayname = ''
                emailpassword = ''

            # return the data as a dict
            data = {
                'domainname': domainname,
                'emailusername': emailusername,
                'accounttype': account_type,
                'emailfirstname': emailfirstname,
                'emaillastname': emaillastname,
                'emaildisplayname': emaildisplayname,
                'emailpassword': emailpassword}

        # If the accout is a Mailing List or Ressource account, we only get the account
        # adress info
        elif account_type in {self.MAILINGLIST, self.RESOURCE}:
            email = self.get_email_by_id(ident)

            data = {
                'domainname': self.get_email_domain(email),
                'emailusername': self.get_email_user(email),
                'accounttype': account_type,
                'emailfirstname': '',
                'emaillastname': '',
                'emaildisplayname': '',
                'emailpassword': ''}

        # If the accout is an Exchange account, we gather info from the corresponding page
        elif account_type == self.EXCHANGE:
            email = self.get_email_by_id(ident)


            url_data = {'id': ident}
            response = self.do_request(self.url['exchangeDetailsURL'],
                                       url_data, None)
            responsebody = response['body']

            tree = html.fromstring(responsebody)
            emailfirstname = tree.xpath('//input[@id="msexchangeModifyExt.FirstName"]/@value')[0]
            emaillastname = tree.xpath('//input[@id="msexchangeModifyExt.LastName"]/@value')[0]

            data = {
                'domainname': self.get_email_domain(email),
                'emailusername': self.get_email_user(email),
                'accounttype': self.EXCHANGE,
                'emailfirstname': emailfirstname,
                'emaillastname': emaillastname,
                'emaildisplayname': '',
                'emailpassword': '********'}

        return data

    @classmethod
    def array_to_string(cls, element):
        """Transform an array with only one element to this element"""
        if not element:
            result = ''
        else:
            result = element[0]
        return result

    def list_account(self):
        """Display all accounts"""
        account_list = self.get_account_list()
        for key in account_list.items():
            print(key)
        print(str(len(account_list)) + ' account(s)')

    def get_account_id(self, account):
        """Find the account ID using the email address"""
        try:
            account_list = self.get_account_list()
            return account_list[account]['id']
        except KeyError:
            return None

    def delete_account(self, account):
        """Delete the email account using the email address"""
        str_data = {'account': account}
        ident = self.get_account_id(account)
        if ident is not None:
            if self.delete_account_by_id(self.get_account_id(account)):
                print('Account {account} deleted successfully'.format(**str_data))
        else:
            self.error('ERROR : Unable to delete acccount {account}\n'
                       '\t{account} does not exist !\n'.format(**str_data))

    def delete_account_by_id(self, ident):
        """Delete the email account using the ID of this account"""
        url_data = {'id': ident}
        emailtype = self.get_account_type_by_id(ident)
        email = self.get_email_by_id(ident)
        str_data = {'email': email}

        if emailtype in (self.MAIL, self.MAILBUSINESS, self.REDIRECT):
            self.do_request(self.url['deleteURL'], url_data, None)
            print('Account {account} deleted successfully'.format(**str_data))
            success = True
        else:
            self.error('ERROR : sorry but only Mail, Business Mail and '
                       'Redirect accounts deletion is supported yet !\n\t'
                       '{emailaccount} will not be deleted !\n'
                       .format(**str_data))
            success = False
        return success



    @classmethod
    def get_account_type_name(cls, typeid):
        """Return the name of the typeid account type"""
        return cls.TYPES[typeid]

    @classmethod
    def get_account_type_id(cls, typename):
        """Return the index of the account type name"""
        return cls.TYPES.index(typename)


if __name__ == "__main__":
    print("Module to manage 1and1 email account")
