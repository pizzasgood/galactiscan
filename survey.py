#!/usr/bin/python
# vim: ts=4 : sts=4 : sw=4 : et :
import math
import datetime
import StringIO
import re
from HTMLParser import HTMLParser


class System:
    location = None

    def __init__(self):
        self.wormholes = []
        self.bodies = []

    def __str__(self):
        ret = str(self.location)
        ret += '\nScanned on: '+self.date.strftime('%m/%d/%y %I:%M %p')
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
        #warning: make sure all zones are created before this is used
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
        self.quality = int(quality.strip('Q'))
        self.prevalence = int(prevalence.strip('%'))
        self.tl = self.quality/8+1

    def __repr__(self):
        return "<Resource name:%s quality:%s prevalence:%s tl:%s>" % (self.name, self.quality, self.prevalence, self.tl)

    def __str__(self):
        return "%s Q%s %s%% (TL%s)" % (self.name, self.quality, self.prevalence, self.tl)


class Wormhole:
    def __repr__(self):
        return "<Wormhole %s from %s to %s>" % (self.polarity, self.source.system_name, self.dest.system_name)

    def __str__(self):
        return "%s wormhole from %s to %s" % (self.polarity, self.source, self.dest)


class Location:
    """Contains names and coordinates of system and sector."""
    def __init__(self, sys_str, sec_str):
        self.system_coords = Coords(sys_str)
        self.sector_coords = Coords(sec_str)
        self.system_name = sys_str[0:sys_str.rfind('(')].strip()
        words = self.system_name.split()
        if words[-1] == 'System':
            self.system_name = self.system_name[0:self.system_name.rfind('S')].strip()
        self.sector_name = sec_str[0:sec_str.rfind('S')].strip()
        if len(self.sector_name) == 0:
            self.sector_name = sec_str.strip()
        self.universal_coords = UniversalCoords(self.system_coords, self.sector_coords)

    def __repr__(self):
        return "<Location system_name: %s>" % (self.system_name)

    def __str__(self):
        return "%s (%s) in %s (%s)" % (self.system_name, self.system_coords, self.sector_name, self.sector_coords)


class UniversalCoords:
    """Universal coordinates in parsecs."""
    def __init__(self, system, sector):
        self.x = system.x + sector.x*10
        self.y = system.y + sector.y*10
        self.z = system.z + sector.z*10

    def __repr__(self):
        return "<UniversalCoords x:%s y:%s z:%s>" % (self.x, self.y, self.z)

    def __str__(self):
        return "%s %s %s" % (self.x, self.y, self.z)


class Coords:
    """Contains xyz coordinates."""
    def __init__(self, s):
        c = self.get_coord_part_of_string(s).split(', ')
        self.x = float(c[0])
        self.y = float(c[1])
        self.z = float(c[2])

    def __repr__(self):
        return "<Coords x:%s y:%s z:%s>" % (self.x, self.y, self.z)

    def __str__(self):
        return "%s %s %s" % (self.x, self.y, self.z)

    def get_coord_part_of_string(self, s):
        """Return the coordinate portion of a string, assuming the coordinates were enclosed in parens."""
        lparen = s.rfind('(')
        rparen = s.rfind(')')
        if rparen < 0:
            rparen = None
        return s[lparen+1 : rparen]


def process_survey_file(filename):
    """Processes survey file 'filename'."""
    if filename is not None:
        #extract the body of the mail
        encoding = 'utf_16_be'
        f = open(filename, 'rb')
        unknown1 = f.read(18)
        sender_size = int(f.read(1).encode('hex'), 16)
        sender = f.read(sender_size).decode(encoding)
        unknown2 = f.read(13)
        title_size = int(f.read(1).encode('hex'), 16)
        title = f.read(title_size).decode(encoding)
        body_size = int(f.read(4).encode('hex'), 16)
        body = f.read(body_size).decode(encoding)
        f.close()

        #verify that this is in fact a System Survey
        #TODO:  support planet surveys too
        if not re.match('^System Survey', title):
            return ([])

        #parse it
        parser = SurveyHTMLParser()
        parser.feed(body)
        parser.close()
        return ([parser.system])


def get_resource_name_from_line(line):
    n1 = line.split(' Q')[0].strip()
    n2 = line.split(' None')[0].strip()
    if len(n1) < len(n2):
        resource_name = n1
    else:
        resource_name = n2
    return resource_name


class SurveyHTMLParser(HTMLParser):
    """Processes survey html. """

    system = None
    section = 'init'
    section_header = ''
    header = ''
    entering_section_header = False
    entering_header = False

    tmp_system = None
    tmp_sector = None

    def handle_starttag(self, tag, attrs):
        if tag == 'big':
            self.entering_section_header = True
        if tag == 'b':
            self.entering_header = True

    def handle_endtag(self, tag):
        if tag == 'big':
            self.entering_section_header = False
        if tag == 'b':
            self.entering_header = False

    def handle_data(self, data):
        data = data.strip()
        if self.entering_section_header:
            self.section_header = data
            if data == 'Wormholes':
                self.section = 'wormholes'
            else:
                self.section = 'body'
                self.system.bodies.append(Body())
                self.system.bodies[-1].name = data
        elif self.entering_header:
            self.header = data
            if self.section == 'wormholes':
                #a new wormhole
                self.system.wormholes.append(Wormhole())
                self.system.wormholes[-1].source = self.system.location
            elif self.section == 'body':
                if self.header == 'Primary':
                    pass
                if self.header.split()[0] == 'Orbiting':
                    #self.system.bodies[-1].orbits = data
                    #unicode issues, so skip the degrees
                    self.system.bodies[-1].orbits = ' '.join(data.split()[0:-1])
        else:
            #here is where we process the raw non-header content
            if self.section == 'init':
                #just started processing the file, will encounter timestamp and officer babble
                if re.match('^UTC:[0-9a-fA-F]+$', data):
                    self.system = System()
                    self.system.date = datetime.datetime.fromtimestamp(int(data[4:], 16))
                elif re.match('.*\([0-9,. \-]+\)', data) and self.tmp_system == None:
                    self.tmp_system = data
                elif re.match('.*\([0-9,. \-]+\)$', data) and self.tmp_sector == None:
                    self.tmp_sector = data
                    self.system.location = Location(self.tmp_system, self.tmp_sector)
                    self.tmp_system = None
                    self.tmp_sector = None
            if self.section == 'wormholes':
                #we're inside the list of wormholes
                #figure out which line this is
                #TODO:  Potential issue if somebody names their empire like 'Charted by (1, 2, 3)' or so
                if re.match('^(Positive|Negative) Wormhole$', data):
                    self.system.wormholes[-1].polarity = data.split()[0]
                elif re.match('.*\([0-9,. \-]+\)$', data) and self.tmp_system == None:
                    self.tmp_system = data
                elif re.match('.*\([0-9,. \-]+\)$', data) and self.tmp_sector == None:
                    self.tmp_sector = data
                    self.system.wormholes[-1].dest = Location(self.tmp_system, self.tmp_sector)
                    self.tmp_system = None
                    self.tmp_sector = None
                else:
                    #don't give a flip who charted it
                    pass
            if self.section == 'body':
                words = data.split()

                if self.header == 'Primary' or self.header.split()[0] == 'Orbiting':
                    if words[0] == 'Type':
                        self.system.bodies[-1].body_kind = 'star'
                        self.system.bodies[-1].set_zones(1)
                        self.system.bodies[-1].star_type = ' '.join(words[1:])
                    elif words[0] == 'Spectral':
                        self.system.bodies[-1].spectral_class = words[2]
                    elif words[0] == 'Size':
                        self.system.bodies[-1].star_size = ' '.join(words[1:])
                    elif self.system.bodies[-1].body_kind != 'star':
                        self.system.bodies[-1].orbit_zone = data

                if self.header == 'Photosphere':
                    if words[-1] == 'Diameter':
                        self.system.bodies[-1].diameter = words[-2]
                    elif words[0] == 'Type':
                        self.system.bodies[-1].add_global_resource(Resource(' '.join(words[0:3]), words[3], words[4]))
                    else:
                        resource_name = get_resource_name_from_line(data)
                        if words[-1] != 'None':
                            self.system.bodies[-1].add_global_resource(Resource(resource_name, words[-2], words[-1]))
                elif self.header == 'Geosphere':
                    if words[-1] == 'Diameter':
                        self.system.bodies[-1].diameter = words[-2]
                        self.system.bodies[-1].body_kind = data.split(', ')[0].strip()
                    elif words[-1] == 'Radius':
                        self.system.bodies[-1].diameter = str(int(words[-2].strip('Lm').replace(',',''))*2)+'m'
                        self.system.bodies[-1].body_kind = data.split(', ')[0].strip()
                    else:
                        resource_name = get_resource_name_from_line(data)
                        zones = data.split(', ')
                        num_zones = len(zones)
                        for z in range(num_zones):
                            a = zones[z].split()
                            if a[-1] != 'None':
                                self.system.bodies[-1].add_zone_resource(z, Resource(resource_name, a[-2], a[-1]))
                elif self.header == 'Hydrosphere' or self.header == 'Atmosphere':
                    if words[0] == 'No' or words[0][-1] == '%' or words[-1] == 'Density':
                        pass
                    else:
                        resource_name = get_resource_name_from_line(data)
                        if words[-1] != 'None':
                            self.system.bodies[-1].add_global_resource(Resource(resource_name, words[-2], words[-1]))
                elif self.header == 'Biosphere':
                    resource_name = get_resource_name_from_line(data)
                    zones = data.split(', ')
                    num_zones = len(zones)
                    for z in range(num_zones):
                        a = zones[z].split()
                        if a[-1] != 'None':
                            self.system.bodies[-1].add_zone_resource(z, Resource(resource_name, a[-1], '100%'))

