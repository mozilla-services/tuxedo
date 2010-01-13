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

# The classes in this file were created to make reading database data easier.  However,
# they are useful in other contexts as well.  They offer both column and row iteration.

version = "1.1"

#======
# R o w
#======
class Row(object):
  """This class represents one row of data from a database.  
  
  It keeps a schema of the original column specification as well as introducing each column 
  name into the attributes dictionary so that the values can be accessed as attributes
  """
  
  #----------------
  # _ _ i n i t _ _
  #----------------
  def __init__ (self, aSchema, aRowTuple):
    """initialize by saving the schema and copying the columns names and values into the 
    dictionary as attributes
    """
    self.originalSchema = aSchema
    for propertySchema, value in zip(aSchema, aRowTuple):
      self.__dict__[propertySchema[0]] = value
  
  #----------------------------------
  # n a m e D a t a T u p l e I t e r
  #----------------------------------
  """return an iterator that gives out tuples in the form: (attributeName, value)
  """
  def nameDataTupleIter(self):
    for x in self.originalSchema:
      yield (x[0], self.__getattribute__(x[0]))
  
  #------------------------
  # b a r e D a t a I t e r
  #------------------------
  """return an iterator that gives out the attribute values in the original schema order
  """
  def bareDataIter(self):
    for x in self.originalSchema:
      yield self.__getattribute__(x[0])
  
  #----------------
  # _ _ i t e r _ _
  #----------------
  def __iter__ (self):
    """return the default iterator type
    """
    return self.bareDataIter()
  
  #--------------
  # _ _ s t r _ _
  #--------------
  def __str__ (self):
    aString = ""
    for x in self.nameDataTupleIter():
      aString += ("%s: %s; " % x)
    return aString


#==========================
# S c h e m a E l e m e n t
#==========================
class SchemaElement(Row):
  """This is a convenience that treats one Python DBAPI 2 schema column description as an object.
  In addition, it can hold a reference to tabular data for which this column is a part.  From that,
  it offers an iterator that sequences through one column of data.
  """
  
  #----------------
  # _ _ i n i t _ _
  #----------------
  def __init__ (self, aDBAPI2SchemaElement, tabularData=None):
    """set up the object with one tuple from a DBAPI 2 schema and optionally
    tabular data
    """
    super(SchemaElement, self).__init__((("name",), ("typecode",), ("displaysize",), ("internalsize",), ("precision",), ("scale",), ("nullable",)), aDBAPI2SchemaElement)
    self.tabularData = tabularData
  
  #--------------
  # _ _ s t r _ _
  #--------------
  def __str__ (self):
    return "%s: %d" % (self.name, self.typecode)
  
  #----------------
  # _ _ r e p r _ _
  #----------------
  def __repr__ (self):
    return "%s: %d" % (self.name, self.typecode)
  
  #----------------
  # _ _ i t e r _ _
  #----------------
  def __iter__ (self):
    """default iterator for iterating over one column of data
    """
    theSchema = [ x for x in self.tabularData.schema ]
    for i, j in zip(range(len(theSchema)), theSchema):
      if self.name == j[0]:
        break
    for x in self.tabularData.nakedRowIter():
      yield x[i]

#======================
# T a b u l a r D a t a
#======================
class TabularData(object):
  """this class represents the data returned from an SQL query in a convenient package
  """
  
  #----------------
  # _ _ i n i t _ _
  #----------------
  def __init__ (self, data=(None, None)):
    """set up a new table of data by passing in a DBAPI 2 schema/contents tuple
    """
    super(TabularData, self).__init__()
    self.setContents(data)
  
  #----------------------
  # g e t C o n t e n t s
  #----------------------
  def getContents (self):
    """get the original schema/contents tuple 
    """
    return (self.schema, self.content)
  
  #----------------------
  # s e t C o n t e n t s
  #----------------------
  def setContents (self, contents):
    self.schema, self.content = contents
  
  #----------------
  # c o n t e n t s
  #----------------
  contents = property(getContents, setContents)
  
  #----------------------------
  # s c h e m a N a m e I t e r
  #----------------------------
  def schemaNameIter (self):
    """iterator for column names
    """
    for x in self.schema:
      yield x[0]
  
  #--------------------
  # c o l u m n I t e r
  #--------------------
  def columnIter (self):
    """an iterator returning a sequence of SchemaElement object.
    Each of these may then return an iterator for iterating over columns.
    """
    for x in self.schema:
      yield SchemaElement(x, self)
  
  #--------------
  # r o w I t e r
  #--------------
  def rowIter (self):
    """an iterator that returns rows wrapped in Row objects
    """
    for x in self.content:
      yield Row(self.schema, x)
  
  #------------------------
  # n a k e d R o w I t e r
  #------------------------
  def nakedRowIter (self):
    """an iterator over the bare default row tuples
    """
    for x in self.content:
      yield x
  
  #----------------
  # _ _ i t e r _ _
  #----------------
  def __iter__ (self):
    """the default iterator
    """
    return self.rowIter()
  
  #--------------
  # _ _ s t r _ _
  #--------------
  def __str__ (self):
    return "schema: %s; content: %s" % (self.schema, self.content)
    
  #--------------------
  # p r i n t B y R o w
  #--------------------
  def printByRow (self):
    """print a table, with column labels in a somewhat neat and tidy manner
    """
    for x in self.schemaNameIter():
      print x,
    print
    
    for x in self.rowIter():
      for y in x:
        print "%s;" % y,
      print
    
  #--------------------------
  # p r i n t B y C o l u m n
  #--------------------------
  def printByColumn (self):
    """print the table in column order
    """
    for x in self.columnIter():
      print "%s: " % x.name,
      for y in x:
        print "%s;" % y,
      print
      

#****************
# _ _ m a i n _ _
#****************
# Test & Playground     
if __name__ == "__main__":

  td = TabularData(((('a', 1, 2, 3, 4, 5, 6), ('b', 7, 8, 9, 10, 11, 12), ('c', 13, 14, 15, 16, 17, 18)), [(1, 2, 3), (4, 5, 6), (7, 8, 9)]))
  
  #td.printByRow()
  #td.printByColumn()
  
  for x in td.columnIter():
    print x.name, x.typecode, x.displaysize, x.internalsize, x.precision, x.nullable, x.scale
    #print (x.name, [y for y in x])
  
  print type(TabularData)
  print type(td)
  print isinstance(td, TabularData)
  
  
    
