#!/usr/bin/env python
import MySQLdb

host = "";
dbname = "";
dbuser = "";
dbpass = "";

print "Content-type: text/csv; charset=utf-8"
print
print "# mirror_id, mirror_name, mirror_baseurl, mirror_rating, mirror_active"

con = MySQLdb.connect(host, dbuser, dbpass, dbname)

cursor = con.cursor()
cursor.execute('select mirror_id, mirror_name, mirror_baseurl, mirror_rating, mirror_active from mirror_mirrors order by mirror_id;')
for each in cursor.fetchall():
	print(",".join([str(x) for x in each]))
