# vim: ts=4 : sts=4 : sw=4 : et :

import survey
import sqlite3
import datetime, time
import tabulation

def adapt_datetime(ts):
    """For use with sqlite3.register_adapter so that datetime is used correctly."""
    return time.mktime(ts.timetuple())
sqlite3.register_adapter(datetime.datetime, adapt_datetime)


db_name = 'database.sqlite3'


def get_con():
    """Get connection to database."""
    con = sqlite3.connect('database.sqlite3')
    con.row_factory = sqlite3.Row
    return con


def drop_tables():
    """Drop all tables if they exist."""

    con = get_con()
    for t in [ 'surveys', 'wormholes', 'bodies', 'resources' ]:
        con.execute("drop table if exists %s" % t)
    con.commit()
    con.close()


def create_tables():
    """Create the tables in the database if needed."""

    con = get_con()

    con.execute("""create table if not exists surveys (
                    survey_date date,
                    stored_date date,
                    system_name text,
                    system_id   text,
                    sector_name text,
                    sector_id   text
                    )""")

    con.execute("""create table if not exists wormholes (
                    polarity    text,
                    source_id   text,
                    dest_id     text,
                    survey_id   integer
                    )""")

    con.execute("""create table if not exists bodies (
                    name        text,
                    body_kind   text,
                    star_type   text,
                    spectral_class  text,
                    star_size   text,
                    diameter    text,
                    orbits      text,
                    orbit_zone  text,
                    num_zones   integer,
                    survey_id   integer
                    )""")

    con.execute("""create table if not exists resources (
                    name        text,
                    quality     integer,
                    prevalence  integer,
                    tl          integer,
                    zone        integer,
                    body_id     integer,
                    survey_id   integer
                    )""")

    con.commit()
    con.close()


def save_survey(system):
    """Save a survey.system to the database."""

    con = get_con()
    cur = con.cursor()

    #find out if there is already an entry for this system
    cur.execute("""SELECT ROWID,
                          survey_date
                   FROM surveys
                   WHERE system_id = ?
                   """, (str(system.location.universal_coords),))
    rows = cur.fetchall()
    for row in rows:
        if system.date < datetime.datetime.fromtimestamp(row[1]):
            #the "new" survey is out of date, so skip it
            con.close()
            return
        else:
            #delete the old survey before we add the new one
            delete_survey(row[0])

    #add the survey
    cur.execute("insert into surveys values (?,?,?,?,?,?)", (
            system.date, datetime.datetime.now(),
            system.location.system_name, str(system.location.universal_coords),
            system.location.sector_name, str(system.location.sector_coords),
            ))
    survey_id = cur.lastrowid

    #add the wormholes
    for w in system.wormholes:
        cur.execute("insert into wormholes values (?,?,?,?)", (
                w.polarity,
                str(w.source.universal_coords),
                str(w.dest.universal_coords),
                survey_id
                ))

    #add the bodies
    for b in system.bodies:
        cur.execute("insert into bodies values (?,?,?,?,?,?,?,?,?,?)", (
                b.name,
                b.body_kind,
                b.star_type,
                b.spectral_class,
                b.star_size,
                b.diameter,
                b.orbits,
                b.orbit_zone,
                len(b.zones),
                survey_id
                ))
        body_id = cur.lastrowid

        #add the resources
        for z in range(len(b.zones)):
            for r in b.zones[z].resources:
                cur.execute("insert into resources values (?,?,?,?,?,?,?)", (
                        r.name,
                        r.quality,
                        r.prevalence,
                        r.tl,
                        z,
                        body_id,
                        survey_id
                        ))


    con.commit()
    con.close()


def delete_survey(survey_id):
    """Delete from the database a survey and all information associated with it."""

    con = get_con()
    cur = con.cursor()

    cur.execute("DELETE FROM surveys WHERE ROWID = ?", (
            survey_id,
            ))
    cur.execute("DELETE FROM wormholes WHERE survey_id = ?", (
            survey_id,
            ))
    cur.execute("DELETE FROM bodies WHERE survey_id = ?", (
            survey_id,
            ))
    cur.execute("DELETE FROM resources WHERE survey_id = ?", (
            survey_id,
            ))

    con.commit()
    con.close()


def is_number(x):
    """Check whether parameter is an integer."""
    try:
        _ = int(x)
    except TypeError:
        return False
    except ValueError:
        return False
    return True


def find_resources(name=None,mintl=None,planet=None,system=None):
    """Find resources matching parameters and return as list of dictionaries."""
    query = """SELECT resources.name,
                      resources.tl,
                      resources.quality,
                      resources.prevalence,
                      bodies.body_kind,
                      resources.zone,
                      surveys.system_name,
                      bodies.name
               FROM resources LEFT JOIN bodies,surveys ON (resources.body_id = bodies.ROWID AND resources.survey_id = surveys.ROWID)
               """
    conditions = []
    parameters = []
    if is_number(mintl):
        conditions.append("resources.tl >= ?")
        parameters.append(mintl)
    if name != None and name != '':
        name = "%%%s%%" % name
        conditions.append("resources.name like ?")
        parameters.append(name)
    if planet != None and planet != '':
        planet = "%%%s%%" % planet
        conditions.append("bodies.name like ?")
        parameters.append(planet)
    if system != None and system != '':
        system = "%%%s%%" % system
        conditions.append("surveys.system_name like ?")
        parameters.append(system)

    query += "WHERE " + " AND ".join(conditions) + " "

    orders = []
    orders.append('resources.name ASC')
    orders.append('resources.quality DESC')
    orders.append('resources.prevalence DESC')
    orders.append('surveys.system_name ASC')
    orders.append('bodies.name ASC')
    orders.append('resources.zone ASC')

    query += "ORDER BY " + ", ".join(orders)

    con = get_con()
    cur = con.cursor()
    cur.execute(query, parameters)
    rows = cur.fetchall()
    con.close()

    ret = format_as_assoc(rows, (
                'Resource',
                'TL',
                'Qual',
                'Freq',
                'Kind',
                'Zone',
                'System',
                'World',
                ))

    return(ret)


def format_as_assoc(rows, keys):
    """Format the list of lists sqlite3 returns into a list of dictionaries with provided keys."""
    ret = []
    for row in rows:
        temp_dict = {}
        for index,key in enumerate(keys):
            temp_dict[key] = row[index]
        ret.append(temp_dict)
    return ret


def decorate(rows):
    """Decorate query results by converting to string, adding % signs, etc."""
    for index,row in enumerate(rows):
        rows[index]['TL'] = 'TL'+str(row['TL'])
        rows[index]['Qual'] = 'Q'+str(row['Qual'])
        rows[index]['Freq'] = str(row['Freq'])+'%'
        rows[index]['Zone'] = str(row['Zone'])
    return rows


def format_as_dict(rows):
    """Format query results into a dictionary of tuples that ResultListCtrl can handle."""
    ret = {}
    for index,row in enumerate(decorate(rows)):
        ret[index] = (
                row['Resource'],
                row['TL'],
                row['Qual'],
                row['Freq'],
                row['Kind'],
                row['Zone'],
                row['System'],
                row['World'],
                )
    return ret


def display_rows(rows):
    """Print query results to console in a table"""

    tabulation.tabulate_dict(decorate(rows), (
                'Resource',
                'TL',
                'Qual',
                'Freq',
                'Kind',
                'Zone',
                'World',
                'System',
                ))

