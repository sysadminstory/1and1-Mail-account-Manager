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
	  --provider PROVIDER   Domain of the 1&1 Order pageused to create yout
				Account (e.g: 1and1.fr or 1and1.co.uk)

	Commands:
	  Valid commands

	  {create,c,list,l,delete,d}
				Choose what do you want to do
	    create (c)          Create emails acounts
	    list (l)            List emails acounts
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

If --output is used, the list of the mails account will be written to the specified file.
If --extended is used, the output (regardless if the output is a file or not) will be in a CSV format.
The CSV format will be the the same as in the CSV File Format Section but with an additional column at the end showing the account type.

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

Creation of emails are only done using CSV files.

The format of this file is the following :

Domain Name, Email Username, Display Name, First Name, Last Name, Password

Example :
domain.com, contact, John Smith, John, Smith,V3ryC0o1Passw0rd!

## Limitation
Currently only supporting those 1&1 contries :
*   France
*   United Kingdom

You must use a domain name to log in : customer number are not supported

## Contributing
1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request :D

## History
2017-03-07 : Initial release
2017-03-09 : Release that supports more than one 
## Credits
The intial work for the control panel login was done here :
https://github.com/devilcius/1and1EmailCreator
## License
This code is released under the GNU GENERAL PUBLIC LICENSE v3. See the LICENCE file for more information.




