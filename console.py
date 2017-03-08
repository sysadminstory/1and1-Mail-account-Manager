#!/usr/bin/env python3
# coding=utf-8
import oneandoneemailmanager
import argparse
import csv
import sys


class Console(object):
    """Console client for the 1&1 Mail account Manager"""

    mailAPI = None

    def __init__(self):
        parser = argparse.ArgumentParser(
            description="Manage your 1and1 mail accounts")

        # Create the parser for the credentials
        parser_credential_group = parser.add_argument_group('Credentials')
        parser_credential_group.add_argument('--domain', type=str,
                                             help='Domain name to log'
                                             'in Control Panel', required=True)
        parser_credential_group.add_argument('--password', type=str,
                                             help='Password to log in'
                                             ' Control Panel', required=True)
        parser_credential_group.add_argument('--provider', type=str,
                                             help='Domain of the 1&1 Order page'
                                             'used to create yout Account '
                                             '(e.g: 1and1.fr or '
                                             '1and1.co.uk)', required=True)

        # Command parser
        subparsers = parser.add_subparsers(title='Commands',
                                           description='Valid commands',
                                           help='Choose what do you want'
                                           ' to do', dest='command')
        subparsers.required = True

        # create the parser for the "create" command
        parser_create = subparsers.add_parser('create', aliases=['c'],
                                              help='Create emails acounts')
        parser_create.add_argument('--input', type=argparse.FileType('r'),
                                   help='CSV file with list of email to be'
                                   ' created', required=True)
        parser_create.set_defaults(func=self.create)

        # create the parser for the "list" command
        parser_list = subparsers.add_parser('list', aliases=['l'],
                                            help='List emails acounts')
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

        args = parser.parse_args()

        # Create the 1&1 API object and continue if the login worked
        self.mailAPI = oneandoneemailmanager.EmailAccountManager(args.domain,
                                                                 args.password,
                                                                 args.provider
                                                                 )
        if self.mailAPI.isLogged:
            args.func(args)
        else:
            self.mailAPI.error('Error : authentification failed !\n')

    def create(self, args):
        """Create the emails using a CSV file as source"""
        reader = csv.reader(args.input)
        for line in reader:
            data = {
                'domainname': line[0],
                'emailusername': line[1],
                'emaildisplayname': line[2],
                'emailfirstname': line[3],
                'emaillastname': line[4],
                'emailpassword': line[5]}
            self.mailAPI.createAccount(data)

    def list(self, args):
        """List the emails in the desired format and output"""
        mailList = self.mailAPI.getAccountList()

        if args.output is not None:
            output = args.output[0]
            writer = csv.writer(args.output[0])
        else:
            writer = csv.writer(sys.stdout)

        for key, value in mailList.items():
            if args.extended is True:
                detail = self.mailAPI.getAccountDetails(value)
                writer.writerow(self.detailToList(detail))
            else:
                if args.output is not None:
                    output.write(key + '\n')
                else:
                    print(key)

    def detailToList(self, detail):
        """Transform the dict returned bu the API in a list"""
        return [detail['domainname'],
                detail['emailusername'],
                detail['emaildisplayname'],
                detail['emailfirstname'],
                detail['emaillastname'],
                detail['emailpassword'],
                detail['accounttype']]

    def delete(self, args):
        """Delete the mails from the file or the command line"""
        if args.input is not None:
            emails = args.input.read().splitlines()
        else:
            emails = args.email
        for email in emails:
            self.mailAPI.deleteAccount(email)

console = Console()
