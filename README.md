# IPMI to Zabbix Template
This tool is designed to query a device IPMI interface and look for available items to monitor. Then using this information it creates an XML template for Zabbix to monitor these items.

## Initial Setup
This Python script requires Python 2.6 or higher.

This script has some external requirements to operate correctly. To install them use the pip installer.

`pip install -r requirements.txt`

## How to Use the Script

`./ipmiToZabbixTemplate.py -H 192.168.1.10 -u username -p password --name "Dell R430 IPMI Template" --write ./templates/dell-r430-template.xml --namespace DellR430`

This will connect to the IPMI interface on IP address 192.168.1.10 with the username and password supplied. It will create a template named "Dell R430 IPMI Template" and store that in the folder "./templates/dell-r430-template.xml" with the name space of "dellr430". You can see the output in the templates folder already.

## Documentation

### Required Command Line Options
* `-H` or `--host` - This is the host that we will be connecting to. This should be the IP address of the IPMI interface.
* `-u` or `--user` - This is the user to use to authenticate to the IPMI interface.
* `-p` or `--password` - This is the password to use to authenticate to the IPMI interface.

### Optional Command Line Options
* `-t` or `--type` - This is the IPMI interface type to use. Options are:
    * `lan` - IPMI 1.5
    * `lanplus` - IPMI 2.0
* `--name` - This is the name of the template. This is what the template will be called in Zabbix once it is imported.
* `--write` - This is the file to write the template to. If you want to just dump the XML to screen, then just leave this option off.
* `--namespace` - This is the namespace of the key. To avoid conflicts with other IPMI keys in Zabbix you might want to use a name space to keep them separate. Otherwise you might end up with duplicate keys in Zabbix and Zabbix will complain.

The script only looks for IPMI values that are of type "Fan", "Temperature", and "Voltage". There might be other IPMI values that we can include, but those seem to be the only values available through Zabbix.

### Examples

#### Dump to Screen
`./ipmiToZabbixTemplate.py -H 192.168.1.10 -u user -p password --name "Dell R430 IPMI Template" --namespace dellr430`

#### Write to a File
`./ipmiToZabbixTemplate.py -H 192.168.1.10 -u user -p password --name "Dell R420 IPMI Template" --write ./templates/dell-r420-template.xml --namespace DellR420`

## Contributing
Take a look at the currently available templates in the templates directory. These are some of the servers we have access to currently and their respective IPMI templates. If you would like to add to the list, please download this repo, create a branch, and then run the command to generate other templates. Then submit a pull request and we will get them added.