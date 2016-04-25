#!/usr/bin/python

from __future__ import print_function

import argparse
import sys
import json
import xml.dom.minidom as MD

# ext commons.h
#/* state tree flags */
ST_FLAG_RW = 0x0001
ST_FLAG_STRING = 0x0002
ST_FLAG_IMMUTABLE = 0x0004

# snmp-ups.h
SU_FLAG_OK = (1 << 0)	        #/* show element to upsd - internal to snmp driver */
SU_FLAG_STATIC = (1 << 1)	#/* retrieve info only once. */
SU_FLAG_ABSENT = (1 << 2)	#/* data is absent in the device,
				# * use default value. */
SU_FLAG_STALE = (1 << 3)	#/* data stale, don't try too often - internal to snmp driver */
SU_FLAG_NEGINVALID = (1 << 4)	#/* Invalid if negative value */
SU_FLAG_UNIQUE = (1 << 5)	#/* There can be only be one
				# * provider of this info,
				# * disable the other providers */
SU_FLAG_SETINT = (1 << 6)	#/* save value */
SU_OUTLET = (1 << 7)	        #/* outlet template definition */
SU_CMD_OFFSET = (1 << 8)	#/* Add +1 to the OID index */

SU_STATUS_PWR = (0 << 8)	#/* indicates power status element */
SU_STATUS_BATT = (1 << 8)	#/* indicates battery status element */
SU_STATUS_CAL = (2 << 8)        #/* indicates calibration status element */
SU_STATUS_RB = (3 << 8)	        #/* indicates replace battery status element */
SU_STATUS_NUM_ELEM = 4
SU_OUTLET_GROUP = (1 << 10)     #/* outlet group template definition */

#/* Phase specific data */
SU_PHASES = (0x3F << 12)
SU_INPHASES = (0x3 << 12)
SU_INPUT_1 = (1 << 12)	#/* only if 1 input phase */
SU_INPUT_3 = (1 << 13)	#/* only if 3 input phases */
SU_OUTPHASES = (0x3 << 14)
SU_OUTPUT_1 = (1 << 14)	#/* only if 1 output phase */
SU_OUTPUT_3 = (1 << 15)	#/* only if 3 output phases */
SU_BYPPHASES = (0x3 << 16)
SU_BYPASS_1 = (1 << 16)	#/* only if 1 bypass phase */
SU_BYPASS_3 = (1 << 17)	#/* only if 3 bypass phases */

#/* hints for su_ups_set, applicable only to rw vars */
SU_TYPE_INT = (0 << 18)	    #/* cast to int when setting value */
SU_TYPE_STRING = (1 << 18)  #/* cast to string. FIXME: redundant with ST_FLAG_STRING */
SU_TYPE_TIME = (2 << 18)    #/* cast to int */
SU_TYPE_CMD = (3 << 18)	    #/* instant command */

def die (msg):
    print ("E: " + msg, file=sys.stderr)
    sys.exit (1)

def warn (msg):
    print ("W: " + msg, file=sys.stderr)

def mkElement (_element, **attrs):
    el = MD.Element (_element)
    for name, value in attrs.items ():
        el.setAttribute (name, str(value))
    return el

def mk_lookup (inp, root):
    if not "INFO" in inp:
        return

    for name, lookup in inp ["INFO"].items ():
        lookup_el = mkElement ("lookup", name=name)
        for oid, value in lookup:
            info_el = mkElement ("lookup_info", oid=oid, value=value)
            lookup_el.appendChild (info_el)
        root.appendChild (lookup_el)

def mk_alarms (inp, root):
    if not "ALARMS-INFO" in inp:
        return
    for name, lookup in inp ["ALARMS-INFO"].items ():
        lookup_el = mkElement ("alarm", name=name)
        for info in lookup:
            info_el = mkElement ("info_alarm", oid=info ["OID"], status=info ["status_value"], alarm=info ["alarm_value"])
            lookup_el.appendChild (info_el)
        root.appendChild (lookup_el)

def mk_snmp (inp, root):
    if not "SNMP-INFO" in inp:
        return
    for name, lookup in inp ["SNMP-INFO"].items ():
        lookup_el = mkElement ("snmp", name=name)
        for info in lookup:

            kwargs = dict (name=info ["info_type"], oid=info ["OID"])

            for name, opt in (("default", info.get ("dfl")),
                             ("lookup", info.get ("oid2info"))):
                if opt is None:
                    continue
                kwargs [name] = opt

            ### process info_flags
            # multiplier is only for !string things
            if not ST_FLAG_STRING in info ["info_flags"]:
                kwargs ["multiplier"] = info ["info_len"]

            # ignore info_flags not relevant to XML generations
            for info_flag in (ST_FLAG_STRING, ST_FLAG_RW, 0):
                if info_flag in info ["info_flags"]:
                    info ["info_flags"].remove (info_flag)

            # This is a assert - if there are info_flags we do not cover, fail here!!!
            if len (info ["info_flags"]) > 0:
                die ("There are unprocessed items in info_flags in '%s'" % (info, ))

            ### process flags
            for name, flag in (("static", SU_FLAG_STATIC), ):
                if not flag in info ["flags"]:
                    continue
                kwargs [name] = "yes"
                info ["flags"].remove (flag)

            # ignore flags not relevant to XML generations
            for flag in (SU_FLAG_OK, ):
                if flag in info ["flags"]:
                    info ["flags"].remove (flag)

            # This is a assert - if there are info_flags we do not cover, fail here!!!
            if len (info ["flags"]) > 0:
                warn ("There are unprocessed items in flags in '%s'" % (info, ))

            info_el = mkElement ("snmp_info", **kwargs)
            lookup_el.appendChild (info_el)
        root.appendChild (lookup_el)

def s_mkparser ():
    p = argparse.ArgumentParser ()
    p.add_argument ("json", help="json input file (default stdin)", default='-', nargs='?')
    return p

## MAIN
p = s_mkparser ()
args = p.parse_args (sys.argv[1:])

impl = MD.getDOMImplementation ()
doc = impl.createDocument (None, "nut", None)
root = doc.documentElement

inp = None
if args.json == '-':
    inp = json.load (sys.stdin)
else:
    with open (args.json, "rt") as fp:
        inp = json.load (fp)

mk_lookup (inp, root)
mk_alarms (inp, root)
mk_snmp (inp, root)
print (doc.toprettyxml ())