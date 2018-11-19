#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
'''
Takes the output of ipmitool and creates a Zabbix template from it.
'''

__author__ = "Tom Walsh"
__version__ = "0.1.0"
__license__ = "MIT"

import argparse
from pyghmi import exceptions, ipmi
from logzero import logger
from datetime import datetime
from yattag import Doc, indent
import sys
import os

doc, tag, text = Doc().tagtext()

sensors = ["Fan", "Temperature", "Voltage"]
templates = {}
ipmidata = {}
itemdefaults = {
    'type': '12',
    'snmp_community': None,
    'snmp_oid': None,
    'delay': '240',
    'history': '7d',
    'trends': '90d',
    'status': '0',
    'allowed_hosts': None,
    'snmpv3_contextname': None,
    'snmpv3_securityname': None,
    'snmpv3_securitylevel': '0',
    'snmpv3_authprotocol': '0',
    'snmpv3_authpassphrase': None,
    'snmpv3_privprotocol': '0',
    'snmpv3_passphrase': None,
    'params': None,
    'authtype': '0',
    'username': None,
    'password': None,
    'publickey': None,
    'privatekey': None,
    'port': None,
    'description': None,
    'inventory_link': '0',
    'valuemap': None,
    'logtimefmt': None,
    'preprocessing': None,
    'jmx_endpoint': None,
    'timeout': '3s',
    'url': None,
    'query_fields': None,
    'posts': None,
    'status_codes': '200',
    'follow_redirects': '1',
    'post_type': '0',
    'http_proxy': None,
    'headers': None,
    'retrieve_mode': '0',
    'request_method': '1',
    'output_format': '0',
    'allow_traps': '0',
    'ssl_cert_file': None,
    'ssl_key_file': None,
    'ssl_key_password': None,
    'verify_peer': '0',
    'verify_host': '0',
    'master_itme': None
}

def main(args):
    import pyghmi.ipmi.command
    import pyghmi.ipmi.sdr
    import pyghmi.exceptions
    try:
        logger.info(args)
        connect = pyghmi.ipmi.command.Command(bmc=args.host, userid=args.user, password=args.password, onlogon=None, kg=None)
    except pyghmi.exceptions.IpmiException as error_name:
        logger.error("Can't connect to IPMI: " + str(error_name))
    except:
        logger.error("Unexpected exception")
        exit(1)

    sdr = pyghmi.ipmi.sdr.SDR(connect)
    for number in sdr.get_sensor_numbers():
        rsp = connect.raw_command(command=0x2d, netfn=4, data=(number,))
        if 'error' in rsp:
            continue
        reading = sdr.sensors[number].decode_sensor_reading(rsp['data'])
        if reading is not None:
            ipmidata[reading.name.lower()] = reading
            if reading.type.lower() not in templates.keys() and reading.type in sensors:
                templates[reading.type.lower()] = reading.type

    with tag('zabbix_export'):
        with tag('version'):
            text("3.4")
        with tag('date'):
            text(datetime.now().replace(microsecond=0).isoformat())
        with tag('groups'):
            with tag('group'):
                with tag('name'):
                    text('Templates')
        with tag('templates'):
            with tag('template'):
                with tag('template'):
                    text(args.name)
                with tag('name'):
                    text(args.name)
                with tag('description'):
                    pass
                with tag('groups'):
                    with tag('group'):
                        with tag('name'):
                            text('Templates')
                with tag('applications'):
                    for key, value in templates.iteritems():
                        with tag('application'):
                            with tag('name'):
                                text(value)
                with tag('items'):
                    for key in sorted(ipmidata.iterkeys()):
                        if ipmidata[key].type in sensors:
                            with tag('item'):
                                with tag('name'):
                                    text(ipmidata[key].name)
                                with tag('key'):
                                    keydata = ipmidata[key].type + '.' + key.replace(' ', '_')
                                    if args.namespace is not None:
                                        keydata = args.namespace + '.' + keydata
                                    text('ipmi.sensor.' + keydata.lower())
                                with tag('units'):
                                    text(ipmidata[key].units.replace('\xc2\xb0', ''))
                                with tag('applications'):
                                    with tag('application'):
                                        with tag('name'):
                                            text(ipmidata[key].type)
                                for itemkey, itemdefault in itemdefaults.iteritems():
                                    with tag(itemkey):
                                        if itemdefault is None:
                                            pass
                                        else:
                                            text(itemdefault)
                with tag('discovery_rules'):
                    pass
                with tag('httptests'):
                    pass
                with tag('macros'):
                    pass
                with tag('templates'):
                    pass
                with tag('screens'):
                    pass

    result = indent(
        doc.getvalue(),
        indentation = ' '*4,
        newline = '\n'
    )

    result = '<?xml version="1.0" encoding="UTF-8"?>' + os.linesep + result

    if args.write is not None:
        tf = open(args.write, "w") 
        tf.write(result)
        tf.close()
    else:
        print(result)


if __name__ == "__main__":
    """ This is executed when run from the command line """
    parser = argparse.ArgumentParser(description="Parses ipmitool output and generates Zabbix XML templates")

    parser.add_argument("-H", "--host", action="store", dest="host", help="IPMI host to query", required=True)
    parser.add_argument("-u", "--user", action="store", dest="user", help="IPMI user to login", required=True)
    parser.add_argument("-p", "--password", action="store", dest="password", help="IPMI password to login", required=True)
    parser.add_argument("-t", "--type", action="store", dest="type", default="lanplus", help="IPMI interface type")
    parser.add_argument("--name", action="store", dest="name", default="IPMI Template", help="Name of the IPMI template")
    parser.add_argument("--write", action="store", dest="write", default=None, help="Write XML output to this file")
    parser.add_argument("--namespace", action="store", dest="namespace", default=None, help="The namespace for the item in Zabbix")
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Verbosity (-v, -vv, etc)")

    # Specify output of "--version"
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version="%(prog)s (version {version})".format(version=__version__))

    args = parser.parse_args()
    main(args)
