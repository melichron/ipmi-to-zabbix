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
from collections import OrderedDict
from yattag import Doc, indent
import sys
import os

doc, tag, text = Doc().tagtext()

sensors = ["Fan", "Temperature", "Voltage"]
templates = {}
ipmidata = {}
itemdefaults = OrderedDict()
itemdefaults['type'] = '12'
itemdefaults['snmp_community'] = None
itemdefaults['snmp_oid'] = None
itemdefaults['delay'] = '240'
itemdefaults['history'] = '90d'
itemdefaults['trends'] = '365d'
itemdefaults['status'] = '0'
itemdefaults['value_type'] = '0'
itemdefaults['allowed_hosts'] = None
itemdefaults['snmpv3_contextname'] = None
itemdefaults['snmpv3_securityname'] = None
itemdefaults['snmpv3_securitylevel'] = '0'
itemdefaults['snmpv3_authprotocol'] = '0'
itemdefaults['snmpv3_authpassphrase'] = None
itemdefaults['snmpv3_privprotocol'] = '0'
itemdefaults['snmpv3_privpassphrase'] = None
#itemdefaults['snmpv3_passphrase'] = None
#itemdefaults['formula'] = '1'
#itemdefaults['delay_flex'] = None
itemdefaults['params'] = None
itemdefaults['authtype'] = '0'
itemdefaults['username'] = None
itemdefaults['password'] = None
itemdefaults['publickey'] = None
itemdefaults['privatekey'] = None
itemdefaults['port'] = None
itemdefaults['description'] = None
itemdefaults['inventory_link'] = '0'
itemdefaults['valuemap'] = None
itemdefaults['logtimefmt'] = None
itemdefaults['preprocessing'] = None
itemdefaults['jmx_endpoint'] = None
itemdefaults['timeout'] = '3s'
itemdefaults['url'] = None
itemdefaults['query_fields'] = None
itemdefaults['posts'] = None
itemdefaults['status_codes'] = '200'
itemdefaults['follow_redirects'] = '1'
itemdefaults['post_type'] = '0'
itemdefaults['http_proxy'] = None
itemdefaults['headers'] = None
itemdefaults['retrieve_mode'] = '0'
itemdefaults['request_method'] = '0'
itemdefaults['output_format'] = '0'
itemdefaults['allow_traps'] = '0'
itemdefaults['ssl_cert_file'] = None
itemdefaults['ssl_key_file'] = None
itemdefaults['ssl_key_password'] = None
itemdefaults['verify_peer'] = '0'
itemdefaults['verify_host'] = '0'
itemdefaults['master_item'] = None


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
            text("4.0")
        with tag('date'):
            text(datetime.now().replace(microsecond=0).isoformat()+'Z')
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
                                for itemkey, itemdefault in itemdefaults.items():
                                    if itemdefault is None:
                                            doc.stag(itemkey)
                                    else:
                                        with tag(itemkey):
                                            text(itemdefault)
                                    if itemkey is 'snmp_oid':
                                        with tag('key'):
                                            keydata = ipmidata[key].type + '.' + key.replace(' ', '_')
                                            keydata = keydata.replace('+','plus')
                                            if args.namespace is not None:
                                                keydata = args.namespace + '.' + keydata
                                            text('ipmi.sensor.' + keydata.lower())
                                    if itemkey is 'allowed_hosts':
                                            with tag('units'):
                                                text(ipmidata[key].units.replace('\xc2\xb0', ''))
                                    if itemkey is 'params':
                                        with tag('ipmi_sensor'):
                                            text(ipmidata[key].name)
                                    if itemkey is 'inventory_link':
                                        with tag('applications'):
                                            with tag('application'):
                                                with tag('name'):
                                                    text(ipmidata[key].type)
                             
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
