# -*- coding: utf-8 -*-
#
# Output status info to text files for use with streaming software such as Open Broadcaster Software, GameShow, XSplit, etc.
# https://obsproject.com/wiki/Sources-Guide#text-gdi
# https://telestream.force.com/kb2/articles/Knowledge_Article/Gameshow-Add-Text
# https://www.xsplit.com/broadcaster/getting-started/adding-text
#

from os.path import join
import sys

from config import config
from companion import ship_map
from l10n import Locale

VERSION = '0.10'

this = sys.modules[__name__]	# For holding module globals
this.outdir = config.get('outdir')

# Info recorded, with initial placeholder values
this.system = 'System'
this.station = 'Station'
this.starpos = (0,0,0)
this.body = 'Body'
this.latlon = (0,0)
this.stationorbody = 'Station or Body'
this.stationorbodyorsystem = 'Station or Body or System'
this.shiptype = 'Ship type'
this.shipname = 'Ship name'


# write out all files
def write_all():
    write_file('EDMC System.txt', this.system)
    write_file('EDMC StarPos.txt', '%s %s %s' % (
        Locale.stringFromNumber(this.starpos[0], 5).encode('utf-8'),
        Locale.stringFromNumber(this.starpos[1], 5).encode('utf-8'),
        Locale.stringFromNumber(this.starpos[2], 5).encode('utf-8')))
    write_file('EDMC Station.txt', this.station)
    write_file('EDMC Body.txt', this.body)
    write_file('EDMC LatLon.txt', '%s %s' % (
        Locale.stringFromNumber(this.latlon[0], 6).encode('utf-8'),
        Locale.stringFromNumber(this.latlon[1], 6).encode('utf-8')))
    write_file('EDMC Station or Body.txt', this.stationorbody)
    write_file('EDMC Station or Body or System.txt', this.stationorbodyorsystem)
    write_file('EDMC ShipType.txt', this.shiptype)
    write_file('EDMC ShipName.txt', this.shipname)


# write one file
def write_file(name, text=None):
    # File needs to be closed for the streaming software to notice its been updated.
    with open(join(this.outdir, name), 'wt') as h:
        h.write('%s\n' % (text or ''))
        h.close()


# Write placeholder values for positioning
def plugin_start():
    write_all()


# Write all files in new location if output directory changed
def prefs_changed(cmdr, is_beta):
    if this.outdir != config.get('outdir'):
        this.outdir = config.get('outdir')
        write_all()


# Write any files with changed data
def journal_entry(cmdr, is_beta, system, station, entry, state):

    if this.system != system:
        this.system = system
        write_file('EDMC System.txt', this.system)

    if 'StarPos' in entry and this.starpos != tuple(entry['StarPos']):
        this.starpos = tuple(entry['StarPos'])
        write_file('EDMC StarPos.txt', '%s %s %s' % (
            Locale.stringFromNumber(this.starpos[0], 5).encode('utf-8'),
            Locale.stringFromNumber(this.starpos[1], 5).encode('utf-8'),
            Locale.stringFromNumber(this.starpos[2], 5).encode('utf-8')))

    if this.station != station:
        this.station = station
        write_file('EDMC Station.txt', this.station)

    if 'Body' in entry and entry.get('BodyType') != 'Station' and this.body != entry['Body']:
        this.body = entry['Body']
        write_file('EDMC Body.txt', this.body)
    elif entry['event'] in ['StartUp', 'Location', 'LeaveBody', 'SupercruiseEntry']:
        this.body = None
        write_file('EDMC Body.txt')

    if this.stationorbody != (this.station or this.body):
        this.stationorbody = (this.station or this.body)
        write_file('EDMC Station or Body.txt', this.stationorbody)

    if this.stationorbodyorsystem != (this.station or this.body or this.system):
        this.stationorbodyorsystem = (this.station or this.body or this.system)
        write_file('EDMC Station or Body or System.txt', this.stationorbodyorsystem)

    if this.shiptype != state['ShipType']:
        this.shiptype = state['ShipType']
        write_file('EDMC ShipType.txt', ship_map.get(this.shiptype, this.shiptype))

    if this.shipname != (state['ShipName'] or this.shiptype):
        this.shipname = (state['ShipName'] or this.shiptype)
        write_file('EDMC ShipName.txt', state['ShipName'] and state['ShipName'].encode('utf-8') or ship_map.get(this.shiptype, this.shiptype))


# Write any files with changed data
def dashboard_entry(cmdr, is_beta, entry):
    if 'Latitude' in entry and 'Longitude' in entry:
        if this.latlon != (entry['Latitude'], entry['Longitude']):
            this.latlon = (entry['Latitude'], entry['Longitude'])
            write_file('EDMC LatLon.txt', '%s %s' % (
                Locale.stringFromNumber(this.latlon[0], 6).encode('utf-8'),
                Locale.stringFromNumber(this.latlon[1], 6).encode('utf-8')))
    elif this.latlon:
        this.latlon = None
        write_file('EDMC LatLon.txt')
