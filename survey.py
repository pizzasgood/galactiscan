#!/usr/bin/python
# vim: ts=4 : sts=4 : sw=4 : et :
import math
import datetime
import StringIO
import re
import xml.etree.ElementTree as ET


class System:
    location = None

    def __init__(self):
        self.wormholes = []
        self.bodies = []

    def __str__(self):
        ret = str(self.location)
        for w in self.wormholes:
            ret += '\n' + str(w)
        for b in self.bodies:
            ret += '\n' + str(b)
        return ret

class Body:
    name = None
    body_kind = None
    star_type = None
    spectral_class = None
    star_size = None
    diameter = None
    orbits = None
    orbit_distance = None
    orbit_zone = None

    def __init__(self):
        self.satellites = []
        self.zones = []

    def __repr__(self):
        return "<Body name: %s>" % self.name
    def __str__(self):
        ret = "-------------\n"
        ret += "%s\n" % self.name
        ret += "  %s\n" % self.body_kind
        if self.body_kind == 'star':
            ret += "  %s\n" % self.star_type
            ret += "  %s\n" % self.spectral_class
            ret += "  %s\n" % self.star_size

        ret += "  %s\n" % self.diameter
        ret += "  %s\n" % self.orbits
        ret += "  %s\n" % self.orbit_distance

        for i in range(len(self.zones)):
            ret += "Zone %s:\n" % i
            ret += str(self.zones[i])

        return ret

    def set_zones(self, num):
        for i in range(num):
            self.zones.append(Zone())
    def add_global_resource(self, r):
        #warning: make sure all zones are created before this is used, or only zone 1 will be populated
        if len(self.zones) == 0:
            self.zones.append(Zone())
        for z in self.zones:
            z.add_resource(r)
    def add_zone_resource(self, z, r):
        #add zones as needed
        while len(self.zones) <= z:
            self.zones.append(Zone())
        self.zones[z].add_resource(r)


class Zone:
    def __init__(self):
        self.resources = []

    def __str__(self):
        ret = ''
        for r in self.resources:
            ret += str(r) + "\n"
        return ret

    def add_resource(self, r):
        self.resources.append(r)


class Resource:
    def __init__(self, name, quality, prevalence):
        self.name = name
        self.quality = int(quality)
        self.prevalence = int(prevalence)
        self.tl = self.quality/8+1

    def __repr__(self):
        return "<Resource name:%s quality:%s prevalence:%s tl:%s>" % (self.name, self.quality, self.prevalence, self.tl)

    def __str__(self):
        return "%s Q%s %s%% (TL%s)" % (self.name, self.quality, self.prevalence, self.tl)


class Wormhole:
    def __repr__(self):
        #return "<Wormhole %s from %s to %s>" % (self.polarity, self.source.system_name, self.dest.system_name)
        return "<Wormhole %s from %s to %s>" % (self.polarity, self.source, self.dest)

    def __str__(self):
        return "%s wormhole from %s to %s" % (self.polarity, self.source, self.dest)


class Location:
    """Contains names and coordinates of system and sector."""
    def __init__(self, sys_node, sec_node):
        self.universal_coords = Coords(sys_node) #pc
        self.sector_coords = Coords(sec_node) #deca-pc
        self.system_coords = LocalCoords(self.universal_coords, self.sector_coords) #pc rel sector center
        self.system_name = sys_node.get('name')
        self.sector_name = sec_node.get('name')

    def __repr__(self):
        return "<Location system_name: %s>" % (self.system_name)

    def __str__(self):
        return "%s (%s) in %s (%s)" % (self.system_name, self.system_coords, self.sector_name, self.sector_coords)


class LocalCoords:
    """Local coordinates in parsecs, relative to sector center."""
    def __init__(self, universal, sector):
        self.x = universal.x - sector.x*10
        self.y = universal.y - sector.y*10
        self.z = universal.z - sector.z*10

    def __repr__(self):
        return "<LocalCoords x:%s y:%s z:%s>" % (self.x, self.y, self.z)

    def __str__(self):
        return "%s %s %s" % (self.x, self.y, self.z)


class Coords:
    """Contains xyz coordinates."""
    def __init__(self, node):
        if 'x' in node.keys():
            self.x = float(node.get('x'))
            self.y = float(node.get('y'))
            self.z = float(node.get('z'))
        else:
            #wormholes are different
            self.x = float(node.get('destX'))
            self.y = float(node.get('destY'))
            self.z = float(node.get('destZ'))

    def __repr__(self):
        return "<Coords x:%s y:%s z:%s>" % (self.x, self.y, self.z)

    def __str__(self):
        return "%s %s %s" % (self.x, self.y, self.z)


def is_starmap_file(filename):
    """Return True if 'filename' is a starmap file."""
    if filename is not None:
        tree = ET.parse(filename)
        root = tree.getroot()
        if root.tag == 'starmap':
            return True
    return False

def process_starmap_file(filename):
    """Processes starmap file 'filename'."""
    if filename is not None:
        f = open(filename, 'rb')
        return process_starmap_fh(f)

def process_starmap_buffer(starmap):
    """Processes raw starmap buffer 'starmap'."""
    if starmap is not None:
        f = StringIO.StringIO(starmap)
        return process_starmap_fh(f)

def process_starmap_fh(f):
    """Processes starmap that file handler 'f' points at."""
    raw = f.read()
    f.close()
    root = ET.fromstring(raw)

    systems = []

    for galaxy in root.findall('galaxy'):
        #TODO: add galaxy support
        for sector in galaxy.findall('sector'):
            for system in sector.findall('system[@eod="Surveyed"]'):
                systems.append(System())
                systems[-1].location = Location(system, sector)
                for wormhole in system.findall('wormhole'):
                    systems[-1].wormholes.append(Wormhole())
                    systems[-1].wormholes[-1].polarity = wormhole.get('polarity')
                    systems[-1].wormholes[-1].source = systems[-1].location
                    systems[-1].wormholes[-1].dest = systems[-1].location
                for star in system.findall('star'):
                    systems[-1].bodies.append(Body())
                    systems[-1].bodies[-1].name = star.get('name')
                    systems[-1].bodies[-1].body_kind = 'star'
                    systems[-1].bodies[-1].star_type = star.get('name')[0]
                    systems[-1].bodies[-1].spectral_class = star.get('spectralClass')
                    systems[-1].bodies[-1].star_size = star.get('size')
                    systems[-1].bodies[-1].diameter = star.get('diameter').split()[0]
                    if 'orbit' in star.keys():
                        systems[-1].bodies[-1].orbits = star.get('orbit')
                    systems[-1].bodies[-1].set_zones(1)
                    for resource in star.findall('resource'):
                        systems[-1].bodies[-1].add_global_resource(Resource(resource.get('name'), resource.get('quality'), resource.get('abundance')))
                for planet in system.findall('planet'):
                    systems[-1].bodies.append(Body())
                    systems[-1].bodies[-1].name = planet.get('name')
                    systems[-1].bodies[-1].body_kind = planet.get('bodyType')
                    systems[-1].bodies[-1].orbits = planet.get('orbit')
                    systems[-1].bodies[-1].orbit_zone = planet.get('zone')
                    for geosphere in planet.findall('geosphere'):
                        systems[-1].bodies[-1].diameter = geosphere.get('diameter').split()[0]
                        num_zones = int(geosphere.get('resourceZones'))
                        for resource in geosphere.findall('resource'):
                            for z in range(1,num_zones+1):
                                systems[-1].bodies[-1].add_zone_resource(z-1, Resource(resource.get('name'), resource.get('qualityZone%s' % z), resource.get('abundanceZone%s' % z)))
                    for hydrosphere in planet.findall('hydrosphere'):
                        for resource in hydrosphere.findall('resource'):
                            systems[-1].bodies[-1].add_global_resource(Resource(resource.get('name'), resource.get('qualityZone1'), resource.get('abundanceZone1')))
                    for atmosphere in planet.findall('atmosphere'):
                        for resource in atmosphere.findall('resource'):
                            systems[-1].bodies[-1].add_global_resource(Resource(resource.get('name'), resource.get('qualityZone1'), resource.get('abundanceZone1')))
                    for biosphere in planet.findall('biosphere'):
                        for resource in biosphere.findall('resource'):
                            for z in range(1,num_zones+1):
                                systems[-1].bodies[-1].add_zone_resource(z-1, Resource(resource.get('name'), resource.get('qualityZone%s' % z), resource.get('abundanceZone%s' % z)))

    return systems


