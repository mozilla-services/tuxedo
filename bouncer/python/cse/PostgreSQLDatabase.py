#!/usr/bin/python

import Database as D
import psycopg

class PostgreSQLConnection(D.Connection):

  def __init__(self, db, dbConnection, name):
    super(PostgreSQLConnection, self).__init__(db, dbConnection, name)

  def getPrimaryKeys (self, tableName):
    constraintKeySQL = "select con.conkey from pg_constraint con, pg_class t where t.relname = '%s' and t.relfilenode = con.conrelid and con.contype = 'p'"  % tableName
    primaryKeyColumnNumbers = self.singleValueSql(constraintKeySQL).replace('{','').replace('}','')
    getColumnNamesSQL = "select att.attname from pg_attribute att, pg_class t where t.relname = '%s' and t.relfilenode = attrelid and att.attnum in (%s)" % (tableName, primaryKeyColumnNumbers)
    return [x for x in D.SQLTabularData(getColumnNamesSQL, self).columnIter().next()]

  def getForeignKeys (self, tableName):
    constraintKeySQL = "select con.confrelid, con.confkey, con.conkey from pg_constraint con, pg_class t where t.relname = '%s' and t.relfilenode = con.conrelid and con.contype = 'f'""" % tableName
    foreignKeys = {}
    for x in D.SQLTabularData(constraintKeySQL, self):
      referredTableNameSQL = "select t.relname from pg_class t where t.relfilenode = %d" % x.confrelid
      referredTableName = self.singleValueSql(referredTableNameSQL)
      foreignKeyColumnNumbersInCurrentTable = x.conkey.replace('{','').replace('}','') 
      foreignKeyColumnNumbersInReferedTable = x.confkey.replace('{','').replace('}','')
      getColumnNamesSQL = "select att.attname from pg_attribute att, pg_class t where t.relname = '%s' and t.relfilenode = attrelid and att.attnum in (%s)"
      for currentTableColumnName, foreignTableColumnName in zip(D.SQLTabularData(getColumnNamesSQL % (tableName, foreignKeyColumnNumbersInCurrentTable), self),
                   D.SQLTabularData(getColumnNamesSQL % (referredTableName, foreignKeyColumnNumbersInReferedTable), self)):
        if referredTableName not in foreignKeys:
          #foreignKeys[currentTableColumnName.attname] = [ (referredTableName, foreignTableColumnName.attname) ]
          foreignKeys[referredTableName] = [ (currentTableColumnName.attname, foreignTableColumnName.attname) ]
        else:
          #foreignKeys[currentTableColumnName.attname].append( (referredTableName, foreignTableColumnName.attname) )
          foreignKeys[referredTableName].append( (currentTableColumnName.attname, foreignTableColumnName.attname) )
    return foreignKeys

  def getForeignKeyReferences (self, tableName):
    constraintKeySQL = "select con.conrelid, con.confkey, con.conkey from pg_constraint con, pg_class t where t.relname = '%s' and t.relfilenode = con.confrelid and con.contype = 'f'""" % tableName
    foreignKeys = {}
    for x in D.SQLTabularData(constraintKeySQL, self):
      referringTableNameSQL = "select t.relname from pg_class t where t.relfilenode = %d" % x.conrelid
      referringTableName = self.singleValueSql(referringTableNameSQL)
      foreignKeyColumnNumbersInCurrentTable = x.confkey.replace('{','').replace('}','') #column numbers from tableName
      foreignKeyColumnNumbersInReferringTable = x.conkey.replace('{','').replace('}','') #column numbers from the table referencing tableName
      getColumnNamesSQL = "select att.attname from pg_attribute att, pg_class t where t.relname = '%s' and t.relfilenode = attrelid and att.attnum in (%s)"
      for currentTableColumnName, foreignTableColumnName in zip(D.SQLTabularData(getColumnNamesSQL % (tableName, foreignKeyColumnNumbersInCurrentTable), self),
                   D.SQLTabularData(getColumnNamesSQL % (referringTableName, foreignKeyColumnNumbersInReferringTable), self)):
        if currentTableColumnName.attname not in foreignKeys:
          #foreignKeys[currentTableColumnName.attname] = [ (referringTableName, foreignTableColumnName.attname) ]
          foreignKeys[referringTableName] = [ (currentTableColumnName.attname, foreignTableColumnName.attname) ]
        else:
          #foreignKeys[currentTableColumnName.attname].append( (referringTableName, foreignTableColumnName.attname) )
          foreignKeys[referringTableName].append( (currentTableColumnName.attname, foreignTableColumnName.attname) )
    return foreignKeys

class PostgreSQLDatabase(D.Database):
  def __init__(self, databaseName, hostName = '', userName = '', password = ''):
    super(PostgreSQLDatabase, self).__init__(psycopg, databaseName, hostName, userName, password)
    self.connectionClass = PostgreSQLConnection

attributeTypeToSQLTypeMapping = { 1043: "VARCHAR", 25: "VARCHAR", 23: "INT", 1082: "DATE", 1083: "DATE", 1114: "DATE", 1184: "DATE", 1700: "DECIMAL", 21: "INT" }
attributeTypeToPythonTypeMapping = { 1043: "str", 25: "str", 23: "int", 1082: "mx.DateTime", 1083: "mx.DateTime", 1114: "mx.DateTime", 1184: "mx.DateTime", 1700: "decimal", 21: "int" }
attributeTypeToJavaTypeMapping = { 1043: "String", 25: "String", 23: "int", 1082: "java.sql.Date", 1083: "java.sql.Date", 1114: "java.sql.Date", 1184: "java.sql.Date", 1700: "java.math.BigDecimal", 21: "int" }

if __name__ == "__main__":

  import psycopg
  
  db = PostgreSQLDatabase("host=localhost dbname=unc")
  
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
  
 

