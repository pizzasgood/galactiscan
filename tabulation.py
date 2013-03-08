# vim: ts=4 : sts=4 : sw=4 : et :
"""
Contains functions for tabulating lists of data.

Currently supports lists of lists and lists of dicts.
"""


#List of lists functions
def tabulate_list(data, header=False):
    """
        Print data as a pretty and aligned table.
        
        The data parameter should be a list of lists.
        If header is True, use data[0] as the headers.

        >>> tabulate_list([
        ...                ['Resource', 'TL',   'Quality'],
        ...                ['Ore',      'TL32', ' 249'],
        ...                ['Minerals', 'TL1',  ' 1']
        ...               ])
        +----------+------+---------+
        | Resource |   TL | Quality |
        |      Ore | TL32 |     249 |
        | Minerals |  TL1 |       1 |
        +----------+------+---------+

        >>> tabulate_list([
        ...                ['Resource', 'TL',   'Quality'],
        ...                ['Ore',      'TL32', ' 249'],
        ...                ['Minerals', 'TL1',  ' 1']
        ...               ], True)
        +----------+------+---------+
        | Resource |   TL | Quality |
        +----------+------+---------+
        |      Ore | TL32 |     249 |
        | Minerals |  TL1 |       1 |
        +----------+------+---------+
    """
    if len(data) == 0:
        return

    #initialize maximum width array
    widths = []
    for v in data[0]:
        widths.append(len(str(v)))

    #determine maximum widths
    for row in data:
        for i,v in enumerate(row):
            widths[i] = max(widths[i], len(str(v)))

    #construct separator
    separator = '+'
    for width in widths:
        separator += (width+2) * '-' + '+'

    #print the header
    if header:
        print(separator)
        print_row(data[0], widths)
        data = data[1:]

    #print data
    print(separator)
    for row in data:
        print_row(row, widths)
    print(separator)


def print_row(row, widths):
    """
        Print a single row of tabulated data.

        >>> print_row(['Ore','TL32','249'], [8,4,7])
        |      Ore | TL32 |     249 |
    """
    line = '|'
    for i,v in enumerate(row):
        line += (widths[i]-len(str(v))+1)*' ' + v + ' |'
    print(line)


#List of dicts functions
def tabulate_dict(data, order=None, header=False):
    """
        Print data as a pretty and aligned table.
        
        The data parameter should be a list of dicts.
        The order parameter is an optional list of keys.
        If header is True, use data[0] as the headers.

        >>> tabulate_dict([
        ...                {'Resource':'Res',      'TL':'Tech Level', 'Quality':'Qual'},
        ...                {'Resource':'Ore',      'TL':'TL32',       'Quality':'249'},
        ...                {'Resource':'Minerals', 'TL':'TL1',        'Quality':'1'}
        ...               ], ['Resource','TL','Quality'], True)
        +----------+------------+------+
        |      Res | Tech Level | Qual |
        +----------+------------+------+
        |      Ore |       TL32 |  249 |
        | Minerals |        TL1 |    1 |
        +----------+------------+------+

        >>> tabulate_dict([
        ...                {'Resource':'Ore',      'TL':'TL32', 'Quality':'249'},
        ...                {'Resource':'Minerals', 'TL':'TL1',  'Quality':'1'}
        ...               ], ['Resource','TL','Quality'])
        +----------+------+---------+
        | Resource |   TL | Quality |
        +----------+------+---------+
        |      Ore | TL32 |     249 |
        | Minerals |  TL1 |       1 |
        +----------+------+---------+
    """

    if len(data) == 0:
        return

    #get the order if none provided
    if order == None:
        order = data[0].keys()
    
    #set the header from the order if no header provided
    if header == False:
        head={}
        for key in order:
            head[key]=key
        data.insert(0, head)
    
    #initialize maximum width array
    widths = {}
    for key in order:
        widths[key] = len(str(data[0][key]))

    #determine maximum widths
    for row in data:
        for key in order:
            widths[key] = max(widths[key], len(str(row[key])))

    #construct separator
    separator = '+'
    for key in order:
        separator += (widths[key]+2) * '-' + '+'

    #print the header
    print(separator)
    print_row_dict(data[0], widths, order)
    data = data[1:]

    #print data
    print(separator)
    for row in data:
        print_row_dict(row, widths, order)
    print(separator)


def print_row_dict(row, widths, order=None):
    """
        Print a single row of tabulated data.

        The row should be a dictionary.
        The widths should be a dictionary of the widths.
        The order parameter is an optional list of keys.

        >>> print_row_dict({'Resource':'Ore','TL':'TL32','Quality':'249'},
        ...                {'Resource':8,'TL':4,'Quality':7},
        ...                ['Resource','TL','Quality'])
        |      Ore | TL32 |     249 |
    """

    if order == None:
        order = row.keys()
    
    line = '|'
    for key in order:
        line += (widths[key]-len(str(row[key]))+1)*' ' + row[key] + ' |'
    print(line)




if __name__ == "__main__":
    import doctest
    doctest.testmod()

