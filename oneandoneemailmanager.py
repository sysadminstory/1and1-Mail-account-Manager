#!/usr/bin/env python3
# coding=utf-8
import urllib
import ssl
import http.cookiejar
import sys
from lxml import html


class EmailAccountManager(object):
    """Class to manipulate amil accounts on 1&1 Control Panel"""

    # 1&1 Control Panel URL
    loginURL = 'https://account.1and1.fr/'
    createEmailURL = 'https://clients.1and1.fr/create-basic-email'
    listEmailURL = 'https://clients.1and1.fr/CenterCommunication?'\
        '__render_href=txt/pages/CenterCommunication.xml&__render_part='\
        'table-component-body&__render_module=frontend-common&page.size='\
        '{size}&page.page={page}'
    pageCountURL = 'https://clients.1and1.fr/CenterCommunication?'\
        '__render_href=txt/pages/CenterCommunication.xml&__render_part='\
        'email-overview-pagination-content&__render_module='\
        'frontend-common&page.size={size}&page.page={page}&'\
        '__reuse=1488715767183.__renderinclude__'
    deleteURL = 'https://clients.1and1.fr/CenterCommunication?'\
        '__render_href=txt/pages/CenterCommunication.xml&__render_part='\
        'table-component-body&__render_module=frontend-common&'\
        '__sendingdata=1&__forcestop=true&__CMD%5B%5D%3ASUBWRP=delete&'\
        'delete.id={id}'
    accountDetailsURL = 'https://clients.1and1.fr/Email_Summary?id={id}'

    userAgent = 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:51.0)'\
        ' Gecko/20100101 Firefox/51.0'  # User agent used during HTTP request

    isLogged = False  # Store the login state
    accountList = None  # Store the account list when first used
    accountCached = False  # True if the account list has been cached

    def __init__(self, username, password):
        """Construstor used to init the config and authenticate"""
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
        self.isLogged = self.authenticate()

    def authenticate(self):
        """Authenticate to the 1&1 Control Panel"""
        # get cookie from login page
        request = urllib.request.Request(EmailAccountManager.loginURL)
        response = self.opener.open(request)

        loginformdata = {
            "__sendingdata": 1,
            "oaologin.password": self.onenandonepassword,
            "oaologin.username": self.oneandoneuser
        }

        data = urllib.parse.urlencode(loginformdata)
        data = data.encode()
        request = urllib.request.Request(EmailAccountManager.loginURL,
                                         data, self.headers)
        response = self.opener.open(request)
        responsebody = response.read().decode()

        # Check if we are really logged in
        if "/Logout" in responsebody:
            print('Authentication successfull !')
            result = True
        else:
            self.error('Authentication failed !\n')
            result = False
        return result

    def createAccount(self, data):
        """Create an email account using the parameters in data"""
        # Set the form data
        emaildomainname = data['domainname']
        emailusername = data['emailusername']
        emaildisplayname = data['emaildisplayname']
        emailfirstname = data['emailfirstname']
        emaillastname = data['emaillastname']
        emailpassword = data['emailpassword']
        emailaccount = "%s@%s" % (emailusername, emaildomainname)
        newAccountData = {"__lf": "create-basic-email-flow",
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
        strData = {'emailaccount': emailaccount}

        response = self.doRequest(EmailAccountManager.createEmailURL,
                                  None, newAccountData)
        responsebody = response['body']

        # Check if the email account has been created
        if emailaccount in responsebody:
            print('Account {emailaccount} created successfully'
                  .format(**strData))
        else:
            self.error('ERROR : Unable to create account {emailaccount}\n\t'
                       'Unknown Error\n'.format(**strData))

    def error(self, errorMessage):
        """Display an error message on the standard error output"""
        sys.stderr.write(errorMessage)

    def formatURL(self, URL, data):
        """Transform placeholder in predefined URL using the data content
        and return it as a string"""
        return URL.format(**data)

    def doRequest(self, URL, URLData, postData):
        """Do a request to the control center and return the response URL,
        content, and a reference to the whole response"""
        if postData is not None:
            data = urllib.parse.urlencode(postData).encode()
        else:
            data = None

        if URLData is not None:
            URL = self.formatURL(URL, URLData)

        request = urllib.request.Request(URL, data, self.headers)
        response = self.opener.open(request)
        return {'url': response.geturl(), 'body': response.read().decode(),
                'self': response}

    def getPageCount(self, URLData):
        """Count the number of pages of the account list"""
        response = self.doRequest(EmailAccountManager.pageCountURL,
                                  URLData, None)
        responsebody = response['body']
        # If the cast in int fails, then there is only one page
        try:
            tree = html.fromstring(responsebody)
            pageCount = tree.xpath(
                '//ul[@class="content-pagination pagination-a1"]'
                '/@data-total-pages')[0]
            return int(pageCount)
        except Exception:
            return 1

    def getAccountList(self):
        """Get the whole account list from the Control Panel
            The format is a dict with the email as key and the id as value :
            Example : {'email@domain.com':123456789}
        """

        # We only ask the Control Panel if we did not already get the
        # account list
        if self.accountCached is False:
            accountList = {}
            size = 100
            page = 1

            URLData = {'size': size, 'page': page}

            # Check the number of page to check, and add every page content
            # to the list
            pageCount = self.getPageCount(URLData)
            for page in range(1, pageCount + 1):
                URLData = {'size': size, 'page': page}
                response = self.doRequest(EmailAccountManager.listEmailURL,
                                          URLData, None)
                responsebody = response['body']

                # Get the mails name and associated id using xpath
                tree = html.fromstring(responsebody)
                mails = tree.xpath(
                    '//a[@class="email-address headline-c1"]/text()')
                ids = tree.xpath(
                    '//a[@class="email-address headline-c1"]/@href')

                for index in range(0, len(mails)):
                    accountList[mails[index]] = ids[index].split('=', 1)[1]
            self.accountList = accountList
            self.accountCached = True
        else:
            accountList = self.accountList

        return accountList

    def getAccountDetails(self, ID):
        """Get the account Details (First Name, Last Name, Full Name,
        Account Type, Password)
            Note: Password is not diplayed in the Control Panel, therefore
            the password is filled with stars"""

        URLData = {'id': ID}
        response = self.doRequest(EmailAccountManager.accountDetailsURL,
                                  URLData, None)
        responsebody = response['body']

        tree = html.fromstring(responsebody)

        # Find all the needed data using xpath
        email = self.arrayToString(
            tree.xpath('//*[@id="mamba-group-adresssummary"]/div[2]/table/'
                       'tbody/tr/td[2]/text()'))
        domainname = email.split('@')[1]
        emailusername = email.split('@')[0]
        accounttype = self.arrayToString(
            tree.xpath('/html/body/div[1]/div[3]/div/div/form/div/div[2]'
                       '/div[2]/div[2]/table[1]/tbody/table/tr[1]/td[1]/span'
                       '/text()'))
        # Get all the Names if this is not a redirect
        if accounttype != 'Redirection':
            emailfirstname = self.arrayToString(
                tree.xpath('/html/body/div[1]/div[3]/div/div/form/div/div[2]'
                           '/div[2]/div[2]/table/tbody/table/tr[2]/td/text()'))
            emaillastname = self.arrayToString(
                tree.xpath('/html/body/div[1]/div[3]/div/div/form/div/div[2]'
                           '/div[2]/div[2]/table/tbody/table/tr[3]/td/text()'))
            emaildisplayname = self.arrayToString(
                tree.xpath('/html/body/div[1]/div[3]/div/div/form/div/div[2]'
                           '/div[2]/div[2]/table/tbody/table/tr[4]/td/text()'))
            emailpassword = self.arrayToString(
                tree.xpath('/html/body/div[1]/div[3]/div/div/form/div/div[2]'
                           '/div[2]/div[2]/table/tbody/table/tr[6]/td[1]'
                           '/span/text()'))
        # Else we fill it with blanks
        else:
            emailfirstname = ''
            emaillastname = ''
            emaildisplayname = ''
            emailpassword = ''

        # return the data as a dict
        data = {
            'domainname': domainname,
            'emailusername': emailusername,
            'accounttype': accounttype,
            'emailfirstname': emailfirstname,
            'emaillastname': emaillastname,
            'emaildisplayname': emaildisplayname,
            'emailpassword': emailpassword}
        return data

    def arrayToString(self, element):
        """Transform an array with only one element to this element"""
        if not element:
            result = ''
        else:
            result = element[0]
        return result

    def listAccount(self):
        """Display all accounts"""
        accountList = self.getAccountList()
        for key, value in accountList.items():
            print(key)
        print(str(len(accountList)) + ' account(s)')

    def getAccountID(self, account):
        """Find the account UD using the email address"""
        try:
            accountList = self.getAccountList()
            return accountList[account]
        except KeyError:
            return None

    def deleteAccount(self, account):
        """Delete the email account using the email address"""
        strData = {'account': account}
        ID = self.getAccountID(account)
        if ID is not None:
            self.deleteAccountID(self.getAccountID(account))
            print('Account {account} deleted successfully'.format(**strData))
        else:
            self.error('ERROR : Unable to delete acccount {account}\n'
                       '\t{account} does not exist !\n'.format(**strData))

    def deleteAccountID(self, ID):
        """Delete the email account using the ID of this account"""
        URLData = {'id': ID}
        self.doRequest(EmailAccountManager.deleteURL, URLData, None)

if __name__ == "__main__":
    print("Module to create 1and1 email account")
