#!/usr/bin/python

import Database as D
import MySQLdb

#class MySQLConnection(D.Connection):
#
#  def __init__(self, db, dbConnection, name):
#    super(PostgreSQLConnection, self).__init__(db, dbConnection, name)


class MySQLDatabase(D.Database):
  def __init__(self, databaseName, hostName = '', userName = '', password = ''):
    super(MySQLDatabase, self).__init__(MySQLdb, databaseName, hostName, userName, password)
    #self.connectionClass = MySQLConnection
  
  def makeConnection (self):
    return self.module.connect (host=self.hostName, db=self.name, user=self.userName, passwd=self.password )


