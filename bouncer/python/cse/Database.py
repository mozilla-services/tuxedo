#!/usr/bin/python
#
# Copyright 2004 by Centaur Software Engineering, Inc.
#
#
#    This file is part of The CSE Python Library.
#
#    The CSE Python Library is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    The CSE Python Library is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with The CSE Python Library; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

import TabularData as TD

version = "1.2"

#======================================================
# T r a n s i e n t Q u e r y D a t a C o n t a i n e r
#======================================================
class TransientQueryDataContainer(object):
  """This class is simple wrapper around an SQL string and connection providing 
  lazy fetching of schema and data.  

  This class is most efficient if there will be only one pass through the data.
  Each time an iterator is requested from this object, the query is submitted
  to the server using a new cursor.  The cursor is wrapped in a generator to 
  make it work like an iterator.
  """

  #----------------
  # _ _ i n i t _ _
  #----------------
  def __init__(self, dbConnection, sql):
    self.connection = dbConnection
    self.sql = sql
    self.cachedCursor = None
    self.cachedDescription = None
  
  #--------------------------
  # g e t D e c r i p t i o n
  #--------------------------
  def getDescription (self):
    if self.cachedDescription is None:
      self.cachedCursor = self.connection.cursor()
      self.cachedCursor.execute(self.sql)
      self.cachedDescription = self.cachedCursor.description
    return self.cachedDescription
  
  #----------------------
  # d e s c r i p t i o n
  #----------------------
  description = property(getDescription)
  
  #------------------
  # g e t S c h e m a
  #------------------
  def getSchema (self):
    """Return a proxy for the schema that implements lazy instantiation.
    """
    return TransientQuerySchemaContainer(self)
  
  #------------
  # s c h e m a
  #------------
  schema = property(getSchema)
  
  #----------------
  # _ _ i t e r _ _
  #----------------
  def __iter__(self):
    if self.cachedCursor is None:
      aCursor = self.connection.cursor()
      aCursor.execute(self.sql)
      self.cachedDescription = aCursor.description
    else:
      aCursor = self.cachedCursor
      self.cachedCursor = None   
    try:
      while True:
        result = aCursor.fetchone() 
        #if a cursor returns no results, then it throws an
        #exception derived from "Error"
        if result is None:
          break
        yield result
    except Error:
      pass

#==========================================================
# T r a n s i e n t Q u e r y S c h e m a C o n t a i n e r
#==========================================================
class TransientQuerySchemaContainer(object):
  """This class is helper companion for TransientQueryDataContainer
  providing lazy instantiation for a query's schema object.
  
  Normally, when a schema object is requested (through the 'description' property) 
  from a TransientQueryDataContainer,   the query must be submitted immediately.  
  This object serves as a proxy for a schema.  The actual schema is not instantiated 
  until the schema object is actually used.
  """
  #----------------
  # _ _ i n i t _ _
  #----------------
  def __init__(self, aTransientQueryDataContainer):
    self.theTransientQueryDataContainer = aTransientQueryDataContainer
  
  #----------------
  # _ _ i t e r _ _
  #----------------
  def __iter__(self):
    return self.theTransientQueryDataContainer.description.__iter__()



#====================
# C o n n e c t i o n
#====================
class Connection(object):
  """This class represents a wrapper object for a connection to a datbase
  """

  #----------------
  # _ _ i n i t _ _
  #----------------
  def __init__(self, db, dbConnection, name):
    """Wrap a database, connection and a name
    
    Typically, this the Database object is used as a  factory for these objects
    so this contructor is not called by the public.
    """
    super(Connection, self).__init__()
    self.db = db
    self.dbConnection = dbConnection
    self.name = name
    self.isOpen = True
    
  #--------------
  # _ _ d e l _ _
  #--------------
  def __del__ (self):
    """make sure the database is closed properly when this object 
    is finally garbage collected
    """
    try:
      self.close()
    except:
      pass  # skip error if this connection has already closed
  
  #----------
  # c l o s e
  #----------
  def close (self):
    """close this connection to the database
    """
    if self.isOpen:
      self.dbConnection.close()
  
  #------------
  # c o m m i t
  #------------
  def commit (self):
    """forwards a commit call to a database connection
    """
    self.dbConnection.commit()
  
  #----------------
  # r o l l b a c k
  #----------------
  def rollback (self):
    """forwards a rollback call to a database connection
    """
    self.dbConnection.rollback()
  
  #------------
  # c u r s o r
  #------------
  def cursor (self, aCursor=None):
    """get a new cursor associated with this connection
    """
    if aCursor is None:
      return self.dbConnection.cursor()
    return aCursor
  
  #----------------------------
  # e x e c u t e M a n y S q l
  #----------------------------
  def executeManySql (self, sql, boundContents, aCursor = None):
    """execute an SQL statement with bound contents
    """
    self.cursor(aCursor).executemany(sql, boundContents)
  
  #------------------------------
  # e x e c u t e S q l Q u e r y
  #------------------------------
  def executeSqlQuery (self, sql):
    """execute an SQL statement returning the cursor for the result
    """
    return TransientQueryDataContainer (self, sql)
    
  #--------------------
  # e x e c u t e S q l
  #--------------------
  def executeSql (self, sql, aCursor = None):
    """execute an SQL statement returning any results as an instance of TabularData
    """
    aCursor = self.cursor(aCursor)
    aCursor.execute(sql)
    try:
      all = aCursor.fetchall()
    except Exception, e:
      return
    return TD.TabularData((aCursor.description, all))

  #----------------------------
  # s i n g l e V a l u e S q l
  #----------------------------
  def singleValueSql(self, sql, aCursor = None):
    """return a single value from an SQL statement
    """
    aCursor = self.cursor(aCursor)
    for x in self.executeSql(sql, aCursor).nakedRowIter():
      return x[0]

  #----------------------------
  # g e t P r i m a r y K e y s
  #----------------------------
  def getPrimaryKeys (self, tableName):
    """return a list of primary keys.
    
    This function is meant to be overridden in a subclass since the methods of
    discovering key information varies vary widely between databases
    """
    return None

  #----------------------------
  # g e t F o r e i g n K e y s
  #----------------------------
  def getForeignKeys (self, tableName):
    """return a list of foreign keys.
    
    This function is meant to be overridden in a subclass since the methods of
    discovering key information varies vary widely between databases
    """
    return None

  #----------------------------------------------
  # g e t F o r e i g n K e y R e f e r e n c e s
  #----------------------------------------------
  def getForeignKeyReferences (self, tableName):
    """get a list of tables and columns that refer to this table
    
    This function is meant to be overridden in a subclass since the methods of
    discovering key information varies vary widely between databases
    """
    return None

  #----------------------------
  # g e t T a b l e S c h e m a
  #----------------------------
  def getTableSchema (self, tableName):
    """Return a list of the schema elements of a table.
    """
    dummySQL = "select * from %s where 1=0" % tableName
    return [x for x in SQLTabularData(dummySQL, self).columnIter()]

#================
# D a t a b a s e
#================
class Database(object):
  """a wapper for DBAPI 2 database objects
  
  Sometimes, for simple database operations, you don't want to mess about with connections
  and cursors.  For those cases, this class echos much of the connection interface.  This allows
  a database object to execute SQL statements, transparently using a default connection and cursor.
  """
  
  #----------------
  # _ _ i n i t _ _
  #----------------
  def __init__ (self, databaseModule, databaseName, hostName = '', userName = '', password = ''):
    """initialize the the appropriate parameters
    
    Arguments:
    databaseModule -- the module implementing the DBAPI 2 for the database to be used. ex: psycopg, MySQLdb, mx.mxODBC
    databaseName -- the name of the database.  Some databases might prefer the entire connect string in this position
    hostName -- what machine has the database
    userName -- who's trying to use the database
    password -- what's the user's authentication
    """
    super(Database, self).__init__()
    self.module = databaseModule
    self.name = databaseName
    self.hostName = hostName
    self.userName = userName
    self.password = password
    self.nextConnectionName = 0
    self.connectionClass = Connection
    self.connections = {}

  #--------------
  # _ _ d e l _ _
  #--------------
  def __del__ (self):
    """make sure the database is closed properly when this object 
    is finally garbage collected
    """
    self.close()
  #----------
  # c l o s e
  #----------
  def close (self):
    """close this connection to the database
    """
    for aConnection in self.connections.itervalues():
      try:
        aConnection.close()
      except:  #skip error if closing a connection that is already closed.
        pass
    self.connections.clear()
  
  #------------
  # c o m m i t
  #------------
  def commit (self):
    """ forward a 'commit' call to the default connection
    """
    self.connection("default").commit()
  
  #----------------
  # r o l l b a c k
  #----------------
  def rollback (self):
    """ forward a 'rollback' call to the default connection
    """
    self.connection("default").rollback()
  
  #----------------------------
  # m a k e C o n n e c t i o n
  #----------------------------
  def makeConnection (self):
    """get the underlying DBAPI 2 module to make one of its own connection object.
    
    If the method doing this is different for a given database, this function should be
    overridden in a derived class.
    """
    return self.module.connect (self.name, self.userName, self.password)
  
  #--------------------
  # c o n n e c t i o n
  #--------------------
  def connection (self, name=None):
    """return a new or cached connection.
    
    Arguments:
    name -- the optional name of a preexisting connection.  If no name is given, then a new
      connection is created with a default name.  If a name is given, and no cached connection
      already uses that name, a new one is created with that name.  Finally, if a name is given
      and a cached connection with that name is found, that connection is returned.
    """
    if name is not None:
      try:
        return self.connections[name]
      except KeyError:
        pass
    else:
      name = `self.nextConnectionName`
      self.nextConnectionName += 1
    aConnection = self.connectionClass(self, self.makeConnection(), name)
    self.connections[name] = aConnection
    return aConnection
  
  #----------------------------
  # e x e c u t e M a n y S q l
  #----------------------------
  def executeManySql (self, sql, boundContents):
    """execute an SQL statement with bound parameters using the default connection.
    """
    self.connection("default").executeManySql(sql, boundContents)
    
  #--------------------
  # e x e c u t e S q l
  #--------------------
  def executeSql (self, sql):
    """Execute and SQL statement using the default connection.
    """
    return self.connection("default").executeSql(sql)

  #------------------------------
  # e x e c u t e S q l Q u e r y
  #------------------------------
  def executeSqlQuery (self, sql):
    """Execute and SQL statement using the default connection.
    """
    return TransientQueryDataContainer(self.connection("default"), sql)

  #----------------------------
  # s i n g l e V a l u e S q l
  #----------------------------
  def singleValueSql (self, sql):
    """return a single value from an SQL statement using the default connection
    """
    return self.connection("default").singleValueSql(sql)
  
  #----------------------------
  # g e t P r i m a r y K e y s
  #----------------------------
  def getPrimaryKeys (self, tableName):
    """return a list of primary keys using the default connection.
    """
    return self.connection("default").getPrimaryKeys(tableName)

  #----------------------------
  # g e t F o r e i g n K e y s
  #----------------------------
  def getForeignKeys (self, tableName):
    """return a list of foreign keys using the default connection.
    """
    return self.connection("default").getForeignKeys(tableName)

  #----------------------------------------------
  # g e t F o r e i g n K e y R e f e r e n c e s
  #----------------------------------------------
  def getForeignKeyReferences (self, tableName):
    """get a list of tables and columns that refer to this table using the default connection
    """
    return self.connection("default").getForeignKeyReferences(tableName)

  #----------------------------
  # g e t T a b l e S c h e m a
  #----------------------------
  def getTableSchema (self, tableName):
    """Return a list of the schema elements of a table using the default connection.
    """
    return self.connection("default").getTableSchema(tableName)

#============================
# S Q L T a b u l a r D a t a
#============================
class SQLTabularData(TD.TabularData):
  """This allows the direct creation of a TabularData using a database or connection and an SQL statement
  """
  
  #----------------
  # _ _ i n i t _ _
  #----------------
  def __init__ (self, sql, databaseOrConnection):
    """create a new TabularData object
      
    Arguments:
    sql -- an SQL statement
    databaseOrConnection -- a database or connection object
    """
    transientQueryData = databaseOrConnection.executeSqlQuery(sql)
    super(SQLTabularData, self).__init__((transientQueryData.schema, transientQueryData))
    self.sql = sql
    self.db = databaseOrConnection

#================
# S Q L T a b l e
#================
class SQLTable(SQLTabularData):
  """This allows the direct creation of a TabularData using a database or connection and the name of a table
  """
  def __init__ (self, tableName, databaseOrConnection):
    """create a new TabularData object
      
    Arguments:
    tableName -- the name of table
    databaseOrConnection -- a database or connection object
    """
    transientQueryData = databaseOrConnection.executeSqlQuery("select * from %s" % tableName)
    super(SQLTabularData, self).__init__((transientQueryData.schema, transientQueryData))
    self.tableName = tableName


#****************
# _ _ m a i n _ _
#****************
# Test & Playground    
if __name__ == "__main__":

  import psycopg
  
  db = Database(psycopg, "host=localhost dbname=unc")
  
  #inv = SQLTabularData("select * from inventory where id < '0200'", db)
  #for x in inv.columnIter():
  #  print x.name, x.typecode
  
  
  arsColors = SQLTabularData("select * from arscolors", db)
  arsColors.printByRow()
  
  for x in arsColors.schemaNameIter():
    print x
    
  for x in arsColors.nakedRowIter():
    print x
  
  for x in arsColors.columnIter():
    for y in x:
      print y,
    print

