#!/usr/bin/env python

""" 
    uptake.py

    This prints out the mirror uptake value for a given product.

    @author Frederic Wenzel <fwenzel@mozilla.com>

"""
import cse
import cse.Database
import cse.MySQLDatabase

import sys
import traceback

version="0.1"
standardError = sys.stderr

#---------------------------------------------------------------------------------------------------
# Database Class
#---------------------------------------------------------------------------------------------------
class Database:

    def __init__(self):
        self.bouncer_db = cse.MySQLDatabase.MySQLDatabase(conf["DatabaseName"],
            conf["ServerName"], conf["UserName"],
            conf["Password"])

    def commit(self):
        self.bouncer_db.commit()

    def close(self):
        self.bouncer_db.close()

    def quote(self,s):
          return self.bouncer_db.module.escape_string(s)

    def getMirrorUptake(self):
        query = """
            SELECT 
            p.product_name as productname,
            o.os_name as osname,
            SUM( m.mirror_rating ) as available,
            (
                SELECT SUM( mirror_rating )
                FROM mirror_mirrors
                WHERE mirror_active = '1' 
            ) as total,
            (   100 * SUM( m.mirror_rating )/
                (
                    SELECT SUM( mirror_rating )
                    FROM mirror_mirrors
                    WHERE mirror_active = '1' 
                )
            ) as percentage
            FROM mirror_mirrors m
            JOIN mirror_location_mirror_map lmm ON lmm.mirror_id = m.mirror_id
            JOIN mirror_locations l ON l.location_id = lmm.location_id
            JOIN mirror_products p ON p.product_id = l.product_id
            JOIN mirror_os o ON o.os_id = l.os_id
            WHERE lmm.location_active = '1'
            AND p.product_name LIKE '%%%s%%'
            AND o.os_name LIKE '%%%s%%'
            GROUP BY lmm.location_id
            """ % (self.quote(conf['product']), self.quote(conf['os']))
        result = self.bouncer_db.executeSql(query)
        return result


#===========================================================================================================
# indent
# (Source: ASPN Python cookbook: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/267662,
#   Licensed in the public domain ("Python Cookbook code is freely available for use and review."), 
#   see: http://aspn.activestate.com/ASPN/Cookbook/Python)
#===========================================================================================================
import cStringIO,operator
def indent(rows, hasHeader=False, headerChar='-', delim=' | ', justify='left',
           separateRows=False, prefix='', postfix='', wrapfunc=lambda x:x):
    """Indents a table by column.
       - rows: A sequence of sequences of items, one sequence per row.
                - hasHeader: True if the first row consists of the columns' names.
                         - headerChar: Character to be used for the row separator line
                                    (if hasHeader==True or separateRows==True).
       - delim: The column delimiter.
                - justify: Determines how are data justified in their column. 
                           Valid values are 'left','right' and 'center'.
       - separateRows: True if rows are to be separated by a line
                  of 'headerChar's.
       - prefix: A string prepended to each printed row.
       - postfix: A string appended to each printed row.
       - wrapfunc: A function f(text) for wrapping text; each element in
                the table is first wrapped by this function."""
    # closure for breaking logical rows to physical, using wrapfunc
    def rowWrapper(row):
        newRows = [wrapfunc(item).split('\n') for item in row]
        return [[substr or '' for substr in item] for item in map(None,*newRows)]
    # break each logical row into one or more physical ones
    logicalRows = [rowWrapper(row) for row in rows]
    # columns of physical rows
    columns = map(None,*reduce(operator.add,logicalRows))
    # get the maximum of each column by the string length of its items
    maxWidths = [max([len(str(item)) for item in column]) for column in columns]
    rowSeparator = headerChar * (len(prefix) + len(postfix) + sum(maxWidths) + \
    len(delim)*(len(maxWidths)-1))
    # select the appropriate justify method
    justify = {'center':str.center, 'right':str.rjust, 'left':str.ljust}[justify.lower()]
    output=cStringIO.StringIO()
    if separateRows: print >> output, rowSeparator
    for physicalRows in logicalRows:
        for row in physicalRows:
            print >> output, \
                prefix \
                + delim.join([justify(str(item),width) for (item,width) in zip(row,maxWidths)]) \
                + postfix
        if separateRows or hasHeader: print >> output, rowSeparator; hasHeader=False
    return output.getvalue()

#===========================================================================================================
# printResultText
#===========================================================================================================
def printResultText(result):
    """Print result set in plain text format"""
    labels = ['Product', 'OS', 'Available', 'Total', 'Percentage']
    # formatting columns
    formats = ( "%s", "%s", "%d", "%d", "%.4f" )
    applyformat = lambda (pos,data): formats[pos] % data
    print indent([labels] + [ [ applyformat(item) for item in enumerate(data) ] for data in result.content ], hasHeader=True)

#===========================================================================================================
# printResultXML
#===========================================================================================================
def printResultXML(result):
    """Print result set in xml format"""

    from xml.sax import saxutils

    print '<?xml version="1.0" encoding="ISO-8859-1"?>'
    # print a little DTD
    print "<!DOCTYPE mirror_uptake [\n" \
        "\t<!ELEMENT mirror_uptake (item*)>\n" \
        "\t<!ELEMENT item (product, os, available, total, percentage)>\n" \
        "\t<!ELEMENT product (#PCDATA)>\n" \
        "\t<!ELEMENT os (#PCDATA)>\n" \
        "\t<!ELEMENT available (#PCDATA)>\n" \
        "\t<!ELEMENT total (#PCDATA)>\n" \
        "\t<!ELEMENT percentage (#PCDATA)>\n" \
        "]>"

    print "<mirror_uptake>"
    # formatting and encoding columns
    formats = ( "%s", "%s", "%d", "%d", "%.4f" )
    applyformat = lambda (pos,data): saxutils.escape(formats[pos] % data)
    xmldata = [ [ applyformat(item) for item in enumerate(data) ] for data in result.content ]
    
    for item in xmldata:
        print "\t<item>"
        print "\t\t<product>%s</product>\n" \
            "\t\t<os>%s</os>\n" \
            "\t\t<available>%s</available>\n" \
            "\t\t<total>%s</total>\n" \
            "\t\t<percentage>%s</percentage>" % tuple(item)
        print "\t</item>"

    print "</mirror_uptake>"

#===========================================================================================================
# main
#===========================================================================================================
if __name__ == "__main__":

    import cse.ConfigurationManager
    
    try:
        
        options = [ ('?',  'help', False, None, 'print this message'), 
                    ('c',  'config', True, './bouncer.conf', 'specify the location and name of the config file'),
                    (None, 'DatabaseName', True, "", 'the name of the database within the server'),
                    (None, 'ServerName', True, "", 'the name of the database server'),
                    (None, 'UserName', True, "", 'the name of the user in the database'),
                    (None, 'Password', True, "", 'the password for the user in the database'),
                    ('p', 'product', True, '', '(part of) the product name to display the uptake for'),
                    (None, 'os', True, '', '(part of) the os/platform name to display the uptake for'),
                    ('f', 'format', True, 'text', 'output format: text or xml')
                    ]
        
        conf = cse.ConfigurationManager.ConfigurationManager(options)
    
    except cse.ConfigurationManager.ConfigurationManagerNotAnOption, x:
        print >>standardError, "%s %s\n%s\nFor usage, try --help" % (sys.argv[0], version, x)
        sys.exit()
    
    # show help
    if conf.has_key("help"): 
        conf.outputCommandSummary()
        sys.exit()

    try:
        # Load our database
        db = Database()

        # fetch uptake from db
        uptake = db.getMirrorUptake()

    except Exception, x:
        print >>standardError, x
        traceback.print_exc(file=standardError)
        sys.exit(1)

    printformats = { 'text': printResultText, 'xml': printResultXML }
    try:
        printformats[conf['format']](uptake)
    except KeyError, x:
        print >>standardError, "Invalid output format: %s" % (conf['format'])
        sys.exit(1)
