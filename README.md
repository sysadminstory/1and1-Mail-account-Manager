# 1&1 Mail account Manager ##
This tool allows to create, list and delete email accounts on the Hosting provider 1&1.

## Installation ##
To install this tool, simply clone this GIT repository :

    git clone https://github.com/sysadminstory/1and1-Mail-account-Manager.git

## Usage

    usage: console.py [-h] --domain DOMAIN --password PASSWORD
                      {create,c,list,l,delete,d} ...
    
    Manage your 1and1 mail accounts
    
    optional arguments:
      -h, --help            show this help message and exit
    
    Credentials:
      --domain DOMAIN       Domain name to log in Control Panel
      --password PASSWORD   Password to log in Control Panel
    
    Commands:
      Valid commands
    
      {create,c,list,l,delete,d}
                            Choose what do you want to do
        create (c)          Create emails acounts
        list (l)            List emails acounts
        delete (d)          Delete email account

Each command has his own help.

###CSV File format

Creation of emails are only done using CSV files.

The format of this file is the following :
Domain Name, Email Username, Display Name, First Name, Last Name, Password

Example :
domain.com, contact, John Smith, John, Smith,V3ryC0o1Passw0rd!

## Limitation
Currently, only the French (1and1.fr) accounts are supported.
You must use a domain name to log in : customer number are not supported

## Contributing
1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request :D

## History
2017-03-07 : Initial release
## Credits
The intial work for the control panel login was done here :
https://github.com/devilcius/1and1EmailCreator
## License
This code is released under the GNU GENERAL PUBLIC LICENSE v3. See the LICENCE file for more information.




