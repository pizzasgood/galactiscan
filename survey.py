#!/usr/bin/python
# vim: ts=4 : sts=4 : sw=4 : et :
import math
import datetime
import StringIO
import re


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
        self.sector_name = sec_str[0:sec_str.rfind('(')].strip()
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


def process_survey(survey):
    """Processes survey text 'survey'."""
    if survey is not None:
        s = StringIO.StringIO(survey)
        return process_survey_fh(s)

def process_survey_file(filename):
    """Processes survey file 'filename'."""
    if filename is not None:
        s = open(filename, 'r')
        return process_survey_fh(s)


def get_resource_name_from_line(line):
    n1 = line.split(' Q')[0].strip()
    n2 = line.split(' None')[0].strip()
    if len(n1) < len(n2):
        resource_name = n1
    else:
        resource_name = n2
    return resource_name

def process_survey_fh(s):
    """Processes survey file that file handler 's' points at."""

    systems = []

    # Celestial bodies
    mode = 'name'
    #for line in s.readlines():
    lines = s.readlines()
    lines_iter = lines.__iter__()
    for line in lines_iter:
        if re.match('\d+/\d+/\d+\s+\d+:\d+\s+[AP]M', line):
            systems.append(System())

            # Header
            systems[-1].date = datetime.datetime.strptime(line.strip(), '%m/%d/%y %I:%M %p')
            line = lines_iter.next() #whitespace
            line = lines_iter.next() #officer
            line = lines_iter.next() #activity
            line = lines_iter.next() #location etc.

            buff = []
            buff.insert(0, lines_iter.next())
            buff.insert(0, lines_iter.next())

            #find the next empty line, then send the previous two lines to Location
            #this is because there is an optional line preceding them if the ship is orbiting something
            while True:
                buff.insert(0, lines_iter.next())
                if buff[0][0] == "\r" or buff[0][0] == "\n":
                    systems[-1].location = Location(buff[-1], buff[-2])
                    break
                else:
                    buff.pop()

            lines_iter.next()
            lines_iter.next()

            # Wormholes
            lines_iter.next()
            line = lines_iter.next()
            while line:
                if line[0] == "\r" or line[0] == "\n":
                    break
                w = Wormhole()
                w.polarity = lines_iter.next().split()[0]
                w.source = systems[-1].location
                w.dest = Location(lines_iter.next(), lines_iter.next())
                systems[-1].wormholes.append(w)
                lines_iter.next()
                line = lines_iter.next()
            mode = 'name'
            continue
        

        if line[0] == "\r" or line[0] == "\n":
            # body definition finished, move on
            mode = 'name'
            continue
        elif mode == 'name':
            # new body
            systems[-1].bodies.append(Body())
            systems[-1].bodies[-1].name = line.strip()
            mode = None
            continue

        # if found new section, update mode
        if line[0] != ' ':
            first_word = line.split()[0]
            if first_word == 'Primary':
                mode = 'Orbiting'
            elif first_word == 'Orbiting':
                #systems[-1].bodies[-1].orbits = line.strip()
                #UTF issues, so skip the degrees
                systems[-1].bodies[-1].orbits = ' '.join(line.split()[0:-1])
                mode = first_word
            else:
                mode = first_word
            continue
            
        # process the section
        words = line.split()
        if mode == 'Orbiting':
            if words[0] == 'Type':
                systems[-1].bodies[-1].body_kind = 'star'
                systems[-1].bodies[-1].set_zones(1)
                systems[-1].bodies[-1].star_type = ' '.join(words[1:])
            elif words[0] == 'Spectral':
                systems[-1].bodies[-1].spectral_class = words[2]
            elif words[0] == 'Size':
                systems[-1].bodies[-1].star_size = ' '.join(words[1:])
            elif systems[-1].bodies[-1].body_kind != 'star':
                systems[-1].bodies[-1].orbit_zone = line.strip()
        elif mode == 'Photosphere':
            if words[-1] == 'Diameter':
                systems[-1].bodies[-1].diameter = words[-2]
            elif words[0] == 'Type':
                systems[-1].bodies[-1].add_global_resource(Resource(' '.join(words[0:3]), words[3], words[4]))
            else:
                resource_name = get_resource_name_from_line(line)
                if words[-1] != 'None':
                    systems[-1].bodies[-1].add_global_resource(Resource(resource_name, words[-2], words[-1]))
        elif mode == 'Geosphere':
            if words[-1] == 'Diameter':
                systems[-1].bodies[-1].diameter = words[-2]
                systems[-1].bodies[-1].body_kind = line.split(', ')[0].strip()
            elif words[-1] == 'Radius':
                systems[-1].bodies[-1].diameter = str(int(words[-2].strip('m'))*2)+'m'
                systems[-1].bodies[-1].body_kind = line.split(', ')[0].strip()
            else:
                resource_name = get_resource_name_from_line(line)
                zones = line.split(', ')
                num_zones = len(zones)
                for z in range(num_zones):
                    a = zones[z].split()
                    if a[-1] != 'None':
                        systems[-1].bodies[-1].add_zone_resource(z, Resource(resource_name, a[-2], a[-1]))
        elif mode == 'Hydrosphere' or mode == 'Atmosphere':
            if words[0] == 'No' or words[0][-1] == '%' or words[-1] == 'Density':
                pass
            else:
                resource_name = get_resource_name_from_line(line)
                if words[-1] != 'None':
                    systems[-1].bodies[-1].add_global_resource(Resource(resource_name, words[-2], words[-1]))
        elif mode == 'Biosphere':
            resource_name = get_resource_name_from_line(line)
            zones = line.split(', ')
            num_zones = len(zones)
            for z in range(num_zones):
                a = zones[z].split()
                if a[-1] != 'None':
                    systems[-1].bodies[-1].add_zone_resource(z, Resource(resource_name, a[-1], '100%'))

    s.close()

    return systems

