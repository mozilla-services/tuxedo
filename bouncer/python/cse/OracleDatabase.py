#!/usr/bin/python

import Database as D
import cx_Oracle

#class OracleConnection(D.Connection):
#
#  def __init__(self, db, dbConnection, name):
#    super(OracleConnection, self).__init__(db, dbConnection, name)


class OracleDatabase(D.Database):
  def __init__(self, hostName = '', userName = '', password = ''):
    super(OracleDatabase, self).__init__(MySQLdb, databaseName, hostName, userName, password)
    #self.connectionClass = MySQLConnection
  
  def makeConnection (self):
    return self.module.connect (dsn=self.hostName, user=self.userName, password=self.password )


if __name__ == "__main__":

  db = OracleDatabase("host=localhost dbname=unc")
  
  for x in ["fred", "sally", "edna"]:
    print "%s schema: %s" % (x, db.getTableSchema(x))
    print "%s primaryKeys: %s" % (x, db.getPrimaryKeys(x))
    print "%s foreignKeys: %s" % (x, db.getForeignKeys(x))
    print "%s foreignKeyReferences: %s" % (x, db.getForeignKeyReferences(x))
  
  #print db.getPrimaryKeys("sally")
  #print db.getPrimaryKeys("edna")
  
  #print db.getForeignKeys("sally")
  #print db.getForeignKeys("edna")
  
  #print db.getTableSchema("edna")
  
 

