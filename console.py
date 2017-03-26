#!/usr/bin/env python3
# coding=utf-8

"""Module to handle the command line and use 1&1 Email Manager API"""

import argparse
import csv
import sys

import oneandoneemailmanager

class Console(object):
    """Console client for the 1&1 Mail account Manager"""

    mail_api = None

    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description="Manage your 1and1 mail accounts")

        # Create the parser for the credentials
        parser_credential_group = self.parser.add_argument_group('Credentials')
        parser_credential_group.add_argument('--domain', type=str,
                                             help='Domain name to log'
                                             'in Control Panel', required=True)
        parser_credential_group.add_argument('--password', type=str,
                                             help='Password to log in'
                                             ' Control Panel', required=True)
        parser_credential_group.add_argument('--provider', type=str,
                                             help='Domain of the 1&1 Order page'
                                             ' used to create your Account '
                                             '(e.g: 1and1.fr or '
                                             '1and1.co.uk)', required=True)

        # Command parser
        subparsers = self.parser.add_subparsers(title='Commands',
                                                description='Valid commands',
                                                help='Choose what do you want'
                                                ' to do', dest='command')
        subparsers.required = True

        # create the parser for the "create" command
        parser_create = subparsers.add_parser('create', aliases=['c'],
                                              help='Create emails accounts')
        parser_create.add_argument('--input', type=argparse.FileType('r'),
                                   help='CSV file with list of email to be'
                                   ' created', required=True)
        parser_create.set_defaults(func=self.create)

        # create the parser for the "list" command
        parser_list = subparsers.add_parser('list', aliases=['l'],
                                            help='List emails accounts')
        parser_list.add_argument('--output', nargs=1,
                                 type=argparse.FileType('w'),
                                 help='File to write the list')
        parser_list.add_argument('--extended',
                                 help='Get extended information for every '
                                 'account. File Output format be used with the'
                                 ' \'create\' command if you add the password',
                                 action='store_true')
        parser_list.set_defaults(func=self.list)

        # create the parser for the "delete" command
        parser_delete = subparsers.add_parser('delete', aliases=['d'],
                                              help='Delete email account')
        parser_delete.add_argument('--input', type=argparse.FileType('r'),
                                   nargs='?')
        parser_delete.add_argument('email', nargs=argparse.REMAINDER)
        parser_delete.set_defaults(func=self.delete)


    def start(self):
        """Start the execution"""

        #Get the arguments passed to the console
        args = self.parser.parse_args()

        # Create the 1&1 API object and continue if the login worked
        self.mail_api = oneandoneemailmanager.EmailAccountManager(args.domain,
                                                                  args.password,
                                                                  args.provider
                                                                 )
        if self.mail_api.is_logged:
            args.func(args)
        else:
            self.mail_api.error('Error : authentification failed !\n')

    def create(self, args):
        """Create the emails using a CSV file as source"""
        reader = csv.reader(args.input)
        for line in reader:
            print(line)
            data = {
                'domainname': line[0],
                'emailusername': line[1],
                'emaildisplayname': line[2],
                'emailfirstname': line[3],
                'emaillastname': line[4],
                'emailpassword': line[5],
                'emailtype': line[6]}
            self.mail_api.create_account(data)

    def list(self, args):
        """List the emails in the desired format and output"""
        mail_list = self.mail_api.get_account_list()

        if args.output is not None:
            output = args.output[0]
            writer = csv.writer(args.output[0])
        else:
            writer = csv.writer(sys.stdout)

        for key, value in mail_list.items():
            if args.extended is True:
                detail = self.mail_api.get_account_details(value['id'])
                writer.writerow(self.detail_to_list(detail))
            else:
                if args.output is not None:
                    output.write(key + '\n')
                else:
                    print(key)

    def detail_to_list(self, detail):
        """Transform the dict returned bu the API in a list"""
        return [detail['domainname'],
                detail['emailusername'],
                detail['emaildisplayname'],
                detail['emailfirstname'],
                detail['emaillastname'],
                detail['emailpassword'],
                self.mail_api.get_account_type_name(detail['accounttype'])]

    def delete(self, args):
        """Delete the mails from the file or the command line"""
        if args.input is not None:
            emails = args.input.read().splitlines()
        else:
            emails = args.email
        for email in emails:
            self.mail_api.delete_account(email)

def main():
    """main function that starts tthe whole thing !"""
    console = Console()
    console.start()

if __name__ == "__main__":
    main()
