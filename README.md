# 1&1 Mail account Manager ##
This tool allows to create, list and delete email accounts on the Hosting provider 1&1.

## Installation ##
To install this tool, simply clone this GIT repository :

    git clone https://github.com/sysadminstory/1and1-Mail-account-Manager.git

## Usage

### Main Help
	usage: console.py [-h] --domain DOMAIN --password PASSWORD --provider PROVIDER
			  {create,c,list,l,delete,d} ...

	Manage your 1and1 mail accounts

	optional arguments:
	  -h, --help            show this help message and exit

	Credentials:
	  --domain DOMAIN       Domain name to login Control Panel
	  --password PASSWORD   Password to log in Control Panel
	  --provider PROVIDER   Domain of the 1&1 Order page used to create your
				Account (e.g: 1and1.fr or 1and1.co.uk)

	Commands:
	  Valid commands

	  {create,c,list,l,delete,d}
				Choose what do you want to do
	    create (c)          Create emails accounts
	    list (l)            List emails accounts
	    delete (d)          Delete email account

Each command has his own help.

### Create Help
	usage: console.py create [-h] --input INPUT

	optional arguments:
	  -h, --help     show this help message and exit
	  --input INPUT  CSV file with list of email to be created

The email accounts you want to create can only be specified using a CSV file passed as a parameter to --input
The format is defined in the CSV File Format Section.

### List Help
	usage: console.py list [-h] [--output OUTPUT] [--extended]

	optional arguments:
	  -h, --help       show this help message and exit
	  --output OUTPUT  File to write the list
	  --extended       Get extended information for every account. File Output
			   format be used with the 'create' command if you add the
			   password

If --output is used, the list of the mail accounts will be written to the specified file.
If --extended is used, the output (regardless if the output is a file or not) will be in a CSV format.
The CSV format is described in the CSV File Format Section.

### Delete Help
	usage: console.py delete [-h] [--input [INPUT]] ...

	positional arguments:
	  email

	optional arguments:
	  -h, --help       show this help message and exit
	  --input [INPUT]

To delete one or more email accounts, you can specify them as a list of accounts on the command line, or pass a file to the --input option.

If a file is used, you must place one email account per line.

### CSV File format

Creation of emails are only done using CSV files. You can list emails using the CSV format too

The format of this file or output is the following :

Domain Name, Email Username, Display Name, First Name, Last Name, Password,Type

Type could be one of :
* MAIL : the classic email account
* REDIRECT : an email redirect
* MAILBUSINESS : a "Business / Groupware" email
* RESOURCE : a "Resource" for the Groupware function (like rooms, hardware, ...)
* MAILINGLIST : a Mailing List
* EXCHANGE : an Exchange account

Creation is only supported for the MAIL type.
Deletion is only supported for MAIL, REDIRECT and MAILBUSINESS type.
Other type are used by the email list command.


Example :
domain.com, contact, John Smith, John, Smith,V3ryC0o1Passw0rd!,MAIL

## Limitation
Currently only supporting those 1&1 countries :
*  France
*  United Kingdom

You must use a domain name to log in : customer number are not supported.

## Contributing
1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request :D

## History
* 2017-03-07
  * Initial release
* 2017-03-09 :
  * Release that supports more than one provider
* 2017-03-26 :
  * Fixed detailed listing emails when there were Exchange, Mailing List or Resource accounts
  * More PEP8 conformance
  * We don't rely on "textual" content to determine the account type
  * Add support of Extended details on Exchange account
  * Limit the deletion tries to the supported types
  * Fixed many typos
* 2017-08-15 :
  * API and Config updated to support the new version of the 1&1 Control Panel
  * Added a 'version' command to get the version of the console, API and config (valid credentials are actually required)

## Credits
The initial work for the control panel login was done here :
https://github.com/devilcius/1and1EmailCreator
## License
This code is released under the GNU GENERAL PUBLIC LICENSE v3. See the LICENCE file for more information.




