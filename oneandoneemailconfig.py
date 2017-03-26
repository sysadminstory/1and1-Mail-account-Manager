#!/usr/bin/env python3
# coding=utf-8

"""Module to handle all the 1&1 Email Manager Config to make it usable for
every country where 1&1 provides his services"""

class OneAndOneConfig(object):
    """Config Class of 1&1 Email Accoutn Manager : it defines all the URL
        used by  the manager"""

    # 1&1 Control Panel URL
    baseURL = {
        'loginURL' : 'https://{loginDom}/',
        'createEmailURL': 'https://{CPDom}/create-basic-email',
        'listEmailURL': 'https://{CPDom}/CenterCommunication?'\
        '__render_href=txt/pages/CenterCommunication.xml&__render_part='\
        'table-component-body&__render_module=frontend-common&page.size='\
        '{size}&page.page={page}',
        'pageCountURL': 'https://{CPDom}/CenterCommunication?'\
        '__render_href=txt/pages/CenterCommunication.xml&__render_part='\
        'email-overview-pagination-content&__render_module='\
        'frontend-common&page.size={size}&page.page={page}&'\
        '__reuse=1488715767183.__renderinclude__',
        'deleteURL' : 'https://{CPDom}/CenterCommunication?'\
        '__render_href=txt/pages/CenterCommunication.xml&__render_part='\
        'table-component-body&__render_module=frontend-common&'\
        '__sendingdata=1&__forcestop=true&__CMD%5B%5D%3ASUBWRP=delete&'\
        'delete.id={id}',
        'accountDetailsURL': 'https://{CPDom}/Email_Summary?id={id}',
        'exchangeDetailsURL': 'https://{CPDom}/MsexchangeUpdate?id={id}'
        }

    domainConfig = {
        '1and1.fr': {'loginDom': 'account.1and1.fr',
                     'CPDom': 'clients.1and1.fr'},
        '1and1.co.uk': {'loginDom': 'account.1and1.co.uk',
                        'CPDom': 'my.1and1.co.uk'}
        }
    domain = None

    def __init__(self, domain):
        """Construstor used to generate the config"""
        # Lower the domain and remove the 'www.' to prevent user issues
        self.domain = domain.lower().replace('www.', '')

    def get_provider(self):
        """Return the current 1and1 provider domain"""
        return self.domain


    def get_config(self):
        """Get the whole config"""

        domain_list = self.domainConfig[self.domain]
        config = {}
        # get cookie from login page
        for key, value in self.baseURL.items():
            config[key] = value.format_map(StringFormatter(domain_list))
        return config

class StringFormatter(dict):
    """Class used to format the URL as wanted : replace only the domain, but
        keep the other placeholder"""
    def __missing__(self, key):
        """In case of a placeholder missing a replacement, returns the
        placeholder itself"""
        return '{' + key + '}'

if __name__ == "__main__":
    print("Module used to config the 1and1-Mail-account-Manager")
