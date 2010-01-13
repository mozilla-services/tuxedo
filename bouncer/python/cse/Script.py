#!/usr/bin/python
#
# Copyright 2001 - 2005 by Centaur Software Engineering, Inc.
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

import TabularData

import mx.DateTime
import string
import time
import os
import re

def version():
  return 'Script 1.4 - 12/29/04'

#----------------------------------------------------------------------------------------------------------
#  c o n v e r t T o S t r i n g
#----------------------------------------------------------------------------------------------------------
def convertToString (value):
  if type(value) != str:
    return `value`
  return value
  
#----------------------------------------------------------------------------------------------------------
#  n o C o n v e r s i o n
#----------------------------------------------------------------------------------------------------------
def noConversion (value):
  return value

#============================================================================================================
#
#  D i c t i o n a r y
#
#============================================================================================================
class Dictionary (dict):
  #----------------------------------------------------------------------------------------------------------
  #  _ _ i n i t _ _
  #----------------------------------------------------------------------------------------------------------
  def __init__ (self):
    pass

  #----------------------------------------------------------------------------------------------------------
  #  l o o k u p
  #----------------------------------------------------------------------------------------------------------
  def lookup (self, key, loopControllers, returnTypeConversionFunction=convertToString):
    try:
      value = self[key]
      for c in loopControllers.current()[1:]:
        if type(value) == list:
          try:
            value = value[c]
          except IndexError:
            try:
              value = value[c % len(value)]
            except:
              value = ''
        else:
          break
      return returnTypeConversionFunction(value)
    except KeyError:
      return key

  #----------------------------------------------------------------------------------------------------------
  #  c o n t a i n s
  #----------------------------------------------------------------------------------------------------------
  def contains (self, key, value):
    # key = key.lower()()
    try:
      return self.searchLists(self.data[key], value)
    except KeyError:
      return 0

  #----------------------------------------------------------------------------------------------------------
  #  s e a r c h L i s t s
  #----------------------------------------------------------------------------------------------------------
  def searchLists (self, theList, value):
    if (type(theList) == list):
      for x in theList:
        if (self.searchLists(x, value) == 1):
          return 1
      return 0
    else:
      return theList == value
    
  #----------------------------------------------------------------------------------------------------------
  #  c o n t a i n s A l l
  #----------------------------------------------------------------------------------------------------------
  def containsAll (self, key, value):
    # key = key.lower()()
    try:
      return self.searchListsAll(self.data[key], value)
    except KeyError:
      return 0
      
  #----------------------------------------------------------------------------------------------------------
  #  s e a r c h L i s t s A l l
  #----------------------------------------------------------------------------------------------------------
  def searchListsAll (self, theList, value):
    if (type(theList) == list):
      for x in theList:
        if (self.searchLists(x, value) == 0):
          return 0
      return 1
    else:
      return theList == value
    
  #----------------------------------------------------------------------------------------------------------
  #  l o o k u p N u m b e r O f E n t r i e s
  #----------------------------------------------------------------------------------------------------------
  def lookupNumberOfEntries (self, key, loopControllers=None):
    # key = key.lower()()
    try:
      if loopControllers:
          value = self[key]
          for x in loopControllers.current()[1:]:
            if type(value) == list:
              try:
                value = value[x]
              except IndexError:
                value = value[x % len(value)]
            else:
              return 1
          if type(value) == list:
            return len(value)
          else:
            return 1
      else:
        value = self.data[key]
        if type(value) == list:
          return len(value)
        else:
          return 1
    except KeyError:
      return 0
    
  #----------------------------------------------------------------------------------------------------------
  #  l o o k u p P r e v i o u s
  #----------------------------------------------------------------------------------------------------------
  def lookupPrevious (self, key, loopControllers, returnTypeConversionFunction=convertToString):
    try:
      value = self[key]
      for x in loopControllers.current()[1:-1]:
        if type(value) == list:
          value = value[x]
        else:
          return 1
      if type(value) == list:
        previous = loopControllers.current()[-1] - 1
        if previous < 0:
          return ''
        return returnTypeConversionFunction(value[previous])
      else:
        return ''
    except KeyError:
      return key

  #----------------------------------------------------------------------------------------------------------
  #  l o o k u p N e x t
  #----------------------------------------------------------------------------------------------------------
  def lookupNext (self, key, loopControllers, returnTypeConversionFunction=convertToString):
    try:
      value = self[key]
      for x in loopControllers.current()[1:-1]:
        if type(value) == list:
          value = value[x]
        else:
          return 1
      if type(value) == list:
        next = loopControllers.current()[-1] + 1
        if next >= len(value):
          return ''
        return returnTypeConversionFunction(value[next])
      else:
        return ''
    except KeyError:
      return key


  #----------------------------------------------------------------------------------------------------------
  #  r e p l a c e
  #----------------------------------------------------------------------------------------------------------
  def replace (self, key, value):
    # key = key.lower()()
    self[key] = value

  #----------------------------------------------------------------------------------------------------------
  #  i n s e r t N o t N o n e
  #----------------------------------------------------------------------------------------------------------
  def insertNotNone (self, key, value):
    if value != None:
      self.insert (key, value)
      
  #----------------------------------------------------------------------------------------------------------
  #  i n s e r t
  #----------------------------------------------------------------------------------------------------------
  def insert (self, key, value):
    # key = key.lower()()
    try:
      existingValue = self[key]
      if (type(existingValue) == list):
        existingValue.append(value)
      else:
        self[key] = [ existingValue, value ]
    except KeyError:
      self[key] = value

  #----------------------------------------------------------------------------------------------------------
  #  i n s e r t A t B e g i n n i n g
  #----------------------------------------------------------------------------------------------------------
  def insertAtBeginning(self, key, value):
    try:
      existingValue = self[key]
      if (type(existingValue) == list):
        existingValue.insert(-1, value)
      else:
        self[key] = [ value, existingValue ]
    except KeyError:
      self[key] = value

  #----------------------------------------------------------------------------------------------------------
  #  i n s e r t m x D a t e T i m e
  #----------------------------------------------------------------------------------------------------------
  def insertmxDateTime (self, keyPrefix, value):
    self.insert(keyPrefix + "-Year", `value.year`)
    self.insert(keyPrefix + "-Month", `value.month`)
    self.insert(keyPrefix + "-MonthName", value.strftime("%B"))
    self.insert(keyPrefix + "-Day", `value.day`)
    self.insert(keyPrefix + "-WeekDayName", value.strftime("%A"))
    self.insert(keyPrefix + "-Hour", `value.hour`)
    hour = value.hour
    if (hour == 0):
      hour = 12
    elif (hour > 12):
      hour -= 12
    self.insert(keyPrefix + "-12Hour",`hour`)
    self.insert(keyPrefix + "-AMPM", value.strftime("%p"))
    self.insert(keyPrefix + "-Minute", `value.minute`)
    self.insert(keyPrefix + "-Second", `value.second`)

  #----------------------------------------------------------------------------------------------------------
  #  i n s e r t D a t e T u p l e
  #----------------------------------------------------------------------------------------------------------
  def insertDateTuple (self, keyPrefix, value):
    self.insert(keyPrefix + "-Year", time.strftime("%Y", value))
    self.insert(keyPrefix + "-Month", time.strftime("%m", value))
    self.insert(keyPrefix + "-MonthName", time.strftime("%B", value))
    self.insert(keyPrefix + "-Day", time.strftime("%d", value))
    self.insert(keyPrefix + "-WeekDayName", time.strftime("%A", value))
    self.insert(keyPrefix + "-Hour", time.strftime("%H", value))
    hour = value[3]
    if (hour == 0):
      hour = 12
    elif (hour > 12):
      hour -= 12
    self.insert(keyPrefix + "-12Hour",`hour`)
    self.insert(keyPrefix + "-AMPM", time.strftime("%p", value))
    self.insert(keyPrefix + "-Minute", time.strftime("%M", value))
    self.insert(keyPrefix + "-Second", time.strftime("%U", value))
    
  #----------------------------------------------------------------------------------------------------------
  #  i n s e r t D i c t i o n a r y
  #----------------------------------------------------------------------------------------------------------
  def insertDictionary (self, aDictionary):
    if (self != aDictionary):
      for x in aDictionary.keys():
        self.insert(x, aDictionary[x])

  #----------------------------------------------------------------------------------------------------------
  #  i n s e r t D i c t i o n a r y F r o m F i l e
  #----------------------------------------------------------------------------------------------------------
  def insertDictionaryFromFile (self, aFileName):
    lines = [ x.strip().replace('\t', ' ').split(' ', 1) for x in open(aFileName).readlines() ]
    for x in lines:
      if (x[0] != ''):
        if (len(x) == 1):
          self.insert(x[0], '')
        else:
          self.insert(x[0], x[1])

  #----------------------------------------------------------------------------------------------------------
  #  i n s e r t E n v i r o n m e n t
  #----------------------------------------------------------------------------------------------------------
  def insertEnvironment(self):
    self.insertDictionary(os.environ)

  #----------------------------------------------------------------------------------------------------------
  #  i n s e r t T a b u l a r D a t a
  #----------------------------------------------------------------------------------------------------------
  def insertTabularData(self, tabularData):
    for x in tabularData.columnIter():
      self.insert(x.name, [y for y in x])

  #----------------------------------------------------------------------------------------------------------
  #  i n s e r t N e s t e d T a b u l a r D a t a
  #----------------------------------------------------------------------------------------------------------
  def insertNestedTabularData(self, tabularData):
    for x in tabularData.columnIter():
      existingValue = self.get(x.name)
      if existingValue is None:
        self.insert(x.name, [[y for y in x]])
      else:
        self.insert(x.name, [y for y in x])

  #----------------------------------------------------------------------------------------------------------
  #  i n s e r t Q u e r y S t r i n g
  #----------------------------------------------------------------------------------------------------------
  #def insertQueryString(self, queryString):

  #----------------------------------------------------------------------------------------------------------
  #  r e m o v e
  #----------------------------------------------------------------------------------------------------------
  def remove (self, key):
    # key = key.lower()()
    del self[key]

  #----------------------------------------------------------------------------------------------------------
  #  i n s e r t N e s t e d D i c t i o n a r y
  #----------------------------------------------------------------------------------------------------------
  def insertNestedDictionary (self, aDictionary):
    if (self != aDictionary):
      for x in aDictionary.keys():
        try:
          existingValue = self[x]
          self.insert(x, aDictionary[x])
        except KeyError:
          self.insert(x, [aDictionary[x]])


#============================================================================================================
#
#  L o o p C o n t r o l l e r E l e m e n t
#
#============================================================================================================
class LoopControllerElement:
  id = 0
  
  #----------------------------------------------------------------------------------------------------------
  #  _ _ i n i t _ _
  #----------------------------------------------------------------------------------------------------------
  def __init__ (self, maximum, increment = 1, jumpBackLocation = 0):
    self.maximumValue = maximum
    self.currentValue = 0
    self.incrementValue = increment
    self.jumpBackLocation = jumpBackLocation
    LoopControllerElement.id += 1
    self.id = LoopControllerElement.id

  #----------------------------------------------------------------------------------------------------------
  #  i n c r e m e n t
  #----------------------------------------------------------------------------------------------------------
  def increment (self):
    try:
      self.currentValue = (self.currentValue + self.incrementValue) % self.maximumValue
      return not self.currentValue
    except ZeroDivisionError:
      return 0

  #----------------------------------------------------------------------------------------------------------
  #  c u r r e n t
  #----------------------------------------------------------------------------------------------------------
  def current (self):
    return self.currentValue

  #----------------------------------------------------------------------------------------------------------
  #  l a s t V a l u e
  #----------------------------------------------------------------------------------------------------------
  def lastValue (self):
    return self.maximumValue - 1

  #----------------------------------------------------------------------------------------------------------
  #  i s L a s t
  #----------------------------------------------------------------------------------------------------------
  def isLast (self):
    return self.current() >= self.lastValue()

  #----------------------------------------------------------------------------------------------------------
  #  j u m p
  #----------------------------------------------------------------------------------------------------------
  def jump (self):
    return self.jumpBackLocation

  #----------------------------------------------------------------------------------------------------------
  #  _ _  r e p r _ _
  #----------------------------------------------------------------------------------------------------------
  def __repr__ (self):
    return "(id: %d, curr: %d, max: %d, inc: %d, jump: %d)" % (self.id, self.currentValue, self.maximumValue, self.incrementValue, self.jumpBackLocation)



#============================================================================================================
#
#  L o o p C o n t r o l l e r 
#
#============================================================================================================
class LoopController(list):
  #----------------------------------------------------------------------------------------------------------
  #  _ _ i n i t _ _
  #----------------------------------------------------------------------------------------------------------
  def __init__(self):
    self.newLoop(0, 0, 0)

  #----------------------------------------------------------------------------------------------------------
  #  i n c r e m e n t
  #----------------------------------------------------------------------------------------------------------
  def increment (self):
    if self[-1].increment():
      self.pop()
      return 1
    return 0

  #----------------------------------------------------------------------------------------------------------
  #  n e w L o o p
  #----------------------------------------------------------------------------------------------------------
  def newLoop (self, maximum, increment, jump):
    self.append(LoopControllerElement(maximum, increment, jump))

  #----------------------------------------------------------------------------------------------------------
  #  c u r r e n t
  #----------------------------------------------------------------------------------------------------------
  def current (self):
    return [x.current() for x in self]

  #----------------------------------------------------------------------------------------------------------
  #  j u m p
  #----------------------------------------------------------------------------------------------------------
  def jump (self):
    return self[-1].jumpBackLocation

  #----------------------------------------------------------------------------------------------------------
  #  p r i n t m e
  #----------------------------------------------------------------------------------------------------------
  def printme (self):
    for x in self:
      print x.current(), 
    print

#============================================================================================================
#
#  S u b s t i t u t i o n D i s p a t c h e r
#
#============================================================================================================
class SubstitutionDispatcher:

  #----------------------------------------------------------------------------------------------------------
  #  _ _ i n i t _ _
  #----------------------------------------------------------------------------------------------------------
  def __init__(self, dictionary, loopController):
    self.dictionary = dictionary
    self.loopController = loopController
    self.lineRepeatIndex = 0
    self.activeSequences = {}
    SubstitutionDispatcher.fieldModifiers = [x for x in SubstitutionDispatcher.__dict__.keys() if x.startswith('fieldModifier')]

  #----------------------------------------------------------------------------------------------------------
  #  s e t L i n e R e p e a t I n d e x
  #----------------------------------------------------------------------------------------------------------
  def setLineRepeatIndex(self, i):
    self.lineRepeatIndex = i

  #----------------------------------------------------------------------------------------------------------
  #  a c t
  #----------------------------------------------------------------------------------------------------------
  def act(self, parameterList):
    reversedList = parameterList[:]
    reversedList.reverse()
    self.stack = []
    self.oldKeysStack = []
    for currentToken in reversedList:
      self.oldKeysStack.append(currentToken)
      tokenAfterSubstitution = self.dictionary.lookup(currentToken, self.loopController)
      if (self.isfieldModifier(tokenAfterSubstitution)):
        tokenAfterSubstitution = self.dispatch (tokenAfterSubstitution)
      self.stack.append(tokenAfterSubstitution)
    if (self.stack == []):
      print "Something BAD happened"
      return None
    else:
      return self.stack.pop()

  #----------------------------------------------------------------------------------------------------------
  #  d i s p a t c h
  #----------------------------------------------------------------------------------------------------------
  def dispatch (self, modifier):
    if (self.isfieldModifier(modifier)):
      return SubstitutionDispatcher.__dict__['fieldModifier' + modifier](self)
    else:
      return None

  #----------------------------------------------------------------------------------------------------------
  #  i s f i e l d M o d i f i e r
  #----------------------------------------------------------------------------------------------------------
  def isfieldModifier (self, testString):
    testString = 'fieldModifier' + testString
    return testString in SubstitutionDispatcher.fieldModifiers

  #----------------------------------------------------------------------------------------------------------
  #  f i e l d M o d i f i e r V E R S I O N
  #----------------------------------------------------------------------------------------------------------
  def fieldModifierVERSION(self):
    return version

  #----------------------------------------------------------------------------------------------------------
  #  f i e l d M o d i f i e r U P P E R
  #----------------------------------------------------------------------------------------------------------
  def fieldModifierUPPER(self):
    aString = self.stack.pop()
    return aString.upper()

  #----------------------------------------------------------------------------------------------------------
  #  f i e l d M o d i f i e r L O W E R
  #----------------------------------------------------------------------------------------------------------
  def fieldModifierLOWER(self):
    aString = self.stack.pop()
    return aString.lower()

  #----------------------------------------------------------------------------------------------------------
  #  f i e l d M o d i f i e r T R U N C
  #----------------------------------------------------------------------------------------------------------
  def fieldModifierTRUNC(self):
    aNumberAsAString = self.stack.pop()
    aNumber = int(aNumberAsAString)
    aString = self.stack.pop()
    return aString[:aNumber]

  #----------------------------------------------------------------------------------------------------------
  #  f i e l d M o d i f i e r S T R I P
  #----------------------------------------------------------------------------------------------------------
  def fieldModifierSTRIP(self):
    aString = self.stack.pop()
    return aString.rstrip()
    #return '------------'

  #----------------------------------------------------------------------------------------------------------
  #  f i e l d M o d i f i e r L E F T S T R I P S P A C E S
  #----------------------------------------------------------------------------------------------------------
  def fieldModifierLEFTSTRIPSPACES(self):
    aString = self.stack.pop()
    return aString.lstrip()
    #return '------------'

  #----------------------------------------------------------------------------------------------------------
  #  f i e l d M o d i f i e r L E F T S T R I P
  #----------------------------------------------------------------------------------------------------------
  def fieldModifierLEFTSTRIP(self):
    valueToStrip = self.stack.pop()
    aString = self.stack.pop()
    return aString.lstrip(valueToStrip)
    #return '------------'

  #----------------------------------------------------------------------------------------------------------
  #  f i e l d M o d i f i e r N O T F I R S T
  #----------------------------------------------------------------------------------------------------------
  def fieldModifierNOTFIRST(self):
    value = self.stack.pop()
    if (self.loopController.current()[-1] == 0):
      return ''
    else:
      return value

  #----------------------------------------------------------------------------------------------------------
  #  f i e l d M o d i f i e r F I R S T O N L Y
  #----------------------------------------------------------------------------------------------------------
  def fieldModifierFIRSTONLY(self):
    value = self.stack.pop()
    if (self.loopController.current()[-1] == 0):
      return value
    else:
      return ''

  #----------------------------------------------------------------------------------------------------------
  #  f i e l d M o d i f i e r N O T L A S T
  #----------------------------------------------------------------------------------------------------------
  def fieldModifierNOTLAST(self):
    value = self.stack.pop()
    if (self.loopController[-1].isLast()):
      return ''
    else:
      return value

  #----------------------------------------------------------------------------------------------------------
  #  f i e l d M o d i f i e r L A S T O N L Y
  #----------------------------------------------------------------------------------------------------------
  def fieldModifierLASTONLY(self):
    value = self.stack.pop()
    if (self.loopController[-1].isLast()):
      return value
    else:
      return ''

  #----------------------------------------------------------------------------------------------------------
  #  f i e l d M o d i f i e r P R E V I O U S
  #----------------------------------------------------------------------------------------------------------
  def fieldModifierPREVIOUS(self):
    value = self.stack.pop()
    value = self.oldKeysStack[0]
    return self.dictionary.lookupPrevious(value, self.loopController)

  #----------------------------------------------------------------------------------------------------------
  #  f i e l d M o d i f i e r N E X T
  #----------------------------------------------------------------------------------------------------------
  def fieldModifierNEXT(self):
    value = self.stack.pop()
    value = self.oldKeysStack[0]
    return self.dictionary.lookupNext(value, self.loopController)

  #----------------------------------------------------------------------------------------------------------
  #  f i e l d M o d i f i e r S P A C E O U T
  #----------------------------------------------------------------------------------------------------------
  def fieldModifierSPACEOUT(self):
    value = self.stack.pop()
    newValue = ''
    for x in value:
      newValue = newValue + x + ' '
    return newValue.rstrip()
   
  #----------------------------------------------------------------------------------------------------------
  #  f i e l d M o d i f i e r S P A C E S A S L O N G A S
  #----------------------------------------------------------------------------------------------------------
  def fieldModifierSPACESASLONGAS(self):
    return ' ' * len(self.stack.pop())
    
  #----------------------------------------------------------------------------------------------------------
  #  f i e l d M o d i f i e r C H A R A C T E R S A S L O N G A S
  #----------------------------------------------------------------------------------------------------------
  def fieldModifierCHARACTERSASLONGAS(self):
    value = self.stack.pop()
    return value * len(self.stack.pop())
    
  #----------------------------------------------------------------------------------------------------------
  #  f i e l d M o d i f i e r 1 C A P
  #----------------------------------------------------------------------------------------------------------
  def fieldModifier1CAP(self):
    value = self.stack.pop()
    try:
      return value[0].upper() + value[1:]
    except IndexError:
      try:
        return value[0].upper()
      except IndexError:
        return value
   
  #----------------------------------------------------------------------------------------------------------
  #  f i e l d M o d i f i e r N O V O W E L
  #----------------------------------------------------------------------------------------------------------
  def fieldModifierNOVOWEL(self):
    value = self.stack.pop()
    vowels = 'aeiouAEIOU'
    newValue = ''
    for x in value:
      if (x not in vowels):
        newValue += x
    return newValue
    
  #----------------------------------------------------------------------------------------------------------
  #  f i e l d M o d i f i e r N O P U N C T
  #----------------------------------------------------------------------------------------------------------
  def fieldModifierNOPUNCT(self):
    value = self.stack.pop()
    newValue = ''
    for x in value:
      if (x not in string.punctuation):
        newValue += x
    return newValue
    
  #----------------------------------------------------------------------------------------------------------
  #  f i e l d M o d i f i e r N O C O M M A
  #----------------------------------------------------------------------------------------------------------
  def fieldModifierNOCOMMA(self):
    value = self.stack.pop()
    newValue = ''
    for x in value:
      if (x != ','):
        newValue += x
    return newValue
    
  #----------------------------------------------------------------------------------------------------------
  #  f i e l d M o d i f i e r N O W H I T E S P A C E
  #----------------------------------------------------------------------------------------------------------
  def fieldModifierNOWHITESPACE(self):
    value = self.stack.pop()
    newValue = ''
    for x in value:
      if (x not in string.whitespace):
        newValue += x
    return newValue
    
  #----------------------------------------------------------------------------------------------------------
  #  f i e l d M o d i f i e r D O U B L E D O U B L E Q U O T E
  #----------------------------------------------------------------------------------------------------------
  def fieldModifierDOUBLEDOUBLEQUOTE(self):
    value = self.stack.pop()
    newValue = ''
    for x in value:
      if (x == '"'):
        newValue += '""'
      else:
        newValue += x
    return newValue
    
  #----------------------------------------------------------------------------------------------------------
  #  f i e l d M o d i f i e r A C S I I
  #----------------------------------------------------------------------------------------------------------
  def fieldModifierACSII(self):
    value = self.stack.pop()
    newValue = ''
    for x in value:
      if (x not in string.printable):
        newValue += x
    return newValue
    
  #----------------------------------------------------------------------------------------------------------
  #  f i e l d M o d i f i e r N U M B E R O F E N T R I E S
  #----------------------------------------------------------------------------------------------------------
  def fieldModifierNUMBEROFENTRIES(self):
    value = self.stack.pop()
    value = self.oldKeysStack[0]
    return self.dictionary.lookupNumberOfEntries(value, self.loopController)
    
  #----------------------------------------------------------------------------------------------------------
  #  f i e l d M o d i f i e r F I L E
  #----------------------------------------------------------------------------------------------------------
  def fieldModifierFILE(self):
    fileName = self.stack.pop()
    return open(fileName).read()
    
  #----------------------------------------------------------------------------------------------------------
  #  f i e l d M o d i f i e r S E Q
  #----------------------------------------------------------------------------------------------------------
  def fieldModifierSEQ(self):
    sequenceName = self.stack.pop()
    if sequenceName[0] == '#':
      try:
        sequenceValue = self.activeSequences[sequenceName] + 1
      except:
        sequenceValue = 1
      self.activeSequences[sequenceName] = sequenceValue
    else:
      try:
        sequenceValue = `string.atoi(open(sequenceName).read()) + 1`
      except IOError:
        sequenceValue = '1'
      open(sequenceName, 'w+').write(sequenceValue)
    return sequenceValue
      
    
  #----------------------------------------------------------------------------------------------------------
  #  f i e l d M o d i f i e r S E Q F I L L
  #
  #  %%SEQFILL 3 seq%% does the same as %%LEFTFILL 0 3 SEQ seq%%
  #----------------------------------------------------------------------------------------------------------
  def fieldModifierSEQFILL(self):
    leftpadding = self.stack.pop()
    self.stack.append(self.fieldModifierSEQ()) 
    self.stack.append(leftpadding)
    self.stack.append('0')
    return self.fieldModifierLEFTFILL()  
    
  #----------------------------------------------------------------------------------------------------------
  #  f i e l d M o d i f i e r 1 0 0 0 Z E R O F I L L
  #----------------------------------------------------------------------------------------------------------
  def fieldModifier1000ZEROFILL(self):
    value = self.stack.pop()
    newValue = string.zfill(value, 4)
    return newValue
    
  #----------------------------------------------------------------------------------------------------------
  #  f i e l d M o d i f i e r 2 D I G I T Z E R O F I L L
  #----------------------------------------------------------------------------------------------------------
  def fieldModifier2DIGITZEROFILL(self):
    value = self.stack.pop()
    newValue = string.zfill(value, 2)
    return newValue
    
  #----------------------------------------------------------------------------------------------------------
  #  f i e l d M o d i f i e r 6 S P A C E B L A N K F I L L
  #----------------------------------------------------------------------------------------------------------
  def fieldModifier6SPACEBLANKFILL(self):
    value = self.stack.pop()
    newValue = value.rjust(6)
    return newValue
    
  #----------------------------------------------------------------------------------------------------------
  #  f i e l d M o d i f i e r 3 0 S P A C E R I G H T B L A N K F I L L
  #----------------------------------------------------------------------------------------------------------
  def fieldModifier30SPACERIGHTBLANKFILL(self):
    value = self.stack.pop()[0:30]
    newValue = value.ljust(30)
    return newValue
    
  #----------------------------------------------------------------------------------------------------------
  #  f i e l d M o d i f i e r R O U N D 1 D E C I M A L
  #----------------------------------------------------------------------------------------------------------
  def fieldModifierROUND1DECIMAL(self):
    try:
      value = string.atof(self.stack.pop())
      newValue = "%3.1f" % value
      return newValue
    except ValueError:
      return ""
    
  #----------------------------------------------------------------------------------------------------------
  #  f i e l d M o d i f i e r D I G I T T O T E X T
  #----------------------------------------------------------------------------------------------------------
  def fieldModifierDIGITTOTEXT(self):
    value = string.atoi(self.stack.pop())
    try:
      newValue = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"][value]
    except IndexError:
      newValue = ("%20d" % value).lstrip()
    return newValue
    
  #----------------------------------------------------------------------------------------------------------
  #  f i e l d M o d i f i e r M O N E Y
  #----------------------------------------------------------------------------------------------------------
  def fieldModifierMONEY(self):
    try:
      temp = self.stack.pop()
      # print "---INFO--- [fieldModifierMONEY]:", temp
      value = string.atof(temp)
      newValue = ("%20.2f" % value).lstrip()
    except IndexError:
      newValue = 'MONEY'
    except ValueError:
      newValue = temp
    return newValue
    
  #----------------------------------------------------------------------------------------------------------
  #  f i e l d M o d i f i e r I N T
  #----------------------------------------------------------------------------------------------------------
  def fieldModifierINT(self):
    try:
      temp = self.stack.pop()
      value = string.atof(temp)
      newValue = ("%20d" % int(value)).lstrip()
    except IndexError:
      newValue = 'INTEGER'
    except ValueError:
      newValue = temp
    return newValue
    
  #----------------------------------------------------------------------------------------------------------
  #  f i e l d M o d i f i e r L E F T C R O P
  #----------------------------------------------------------------------------------------------------------
  def fieldModifierLEFTCROP(self):
    cropSize = string.atoi(self.stack.pop())
    value = self.stack.pop()
    newValue = value[cropSize:]
    return newValue

  #----------------------------------------------------------------------------------------------------------
  #  f i e l d M o d i f i e r G R O U P
  #----------------------------------------------------------------------------------------------------------
  def fieldModifierGROUP(self):
    groupSize = string.atoi(self.stack.pop())
    value = self.stack.pop()
    newValue = ""
    for i in range(len(value)):
      newValue += value[i]
      if ((i + 1) % groupSize == 0):
        newValue += " "
    return newValue

  #----------------------------------------------------------------------------------------------------------
  #  f i e l d M o d i f i e r L E F T
  #----------------------------------------------------------------------------------------------------------
  def fieldModifierLEFT(self):
    fieldSize = string.atoi(self.stack.pop())
    value = self.stack.pop()
    newValue = value.ljust(fieldSize)
    return newValue

  #----------------------------------------------------------------------------------------------------------
  #  f i e l d M o d i f i e r L E F T F I L L
  #----------------------------------------------------------------------------------------------------------
  def fieldModifierLEFTFILL(self):
    fillCharacter = self.stack.pop()
    fieldSize = string.atoi(self.stack.pop())
    value = fillCharacter * fieldSize + self.stack.pop()
    newValue = value[-fieldSize:]
    return newValue

  #----------------------------------------------------------------------------------------------------------
  #  f i e l d M o d i f i e r R I G H T
  #----------------------------------------------------------------------------------------------------------
  def fieldModifierRIGHT(self):
    fieldSize = string.atoi(self.stack.pop())
    value = self.stack.pop()
    newValue = value.rjust(fieldSize)
    return newValue

  #----------------------------------------------------------------------------------------------------------
  #  f i e l d M o d i f i e r R I G H T F I L L
  #----------------------------------------------------------------------------------------------------------
  def fieldModifierRIGHTFILL(self):
    fillCharacter = self.stack.pop()
    fieldSize = string.atoi(self.stack.pop())
    value = self.stack.pop() + fillCharacter * fieldSize
    newValue = value[:fieldSize]
    return newValue

  #----------------------------------------------------------------------------------------------------------
  #  f i e l d M o d i f i e r A B S
  #----------------------------------------------------------------------------------------------------------
  def fieldModifierABS(self):
    rawValue = self.stack.pop()
    try:
      value = abs(string.atof(rawValue))
      return "%f" % value
    except ValueError:
      value = abs(string.atoi(rawValue))
    return "%d" % value

  #----------------------------------------------------------------------------------------------------------
  #  f i e l d M o d i f i e r C E N T E R
  #----------------------------------------------------------------------------------------------------------
  def fieldModifierCENTER(self):
    fieldSize = string.atoi(self.stack.pop())
    value = self.stack.pop()
    return value.center(fieldSize)

  #----------------------------------------------------------------------------------------------------------
  #  f i e l d M o d i f i e r C E N T E R F I L L
  #----------------------------------------------------------------------------------------------------------
  def fieldModifierCENTERFILL(self):
    fillCharacter = self.stack.pop()
    fieldSize = string.atoi(self.stack.pop())
    halfSize = fieldSize / 2
    value = self.stack.pop()
    newValue = fillCharacter * halfSize + value
    newValue = newValue[-(halfSize + len(value) / 2):]
    newValue = newValue + fillCharacter * halfSize
    newValue = newValue[0:fieldSize]
    return newValue

  #----------------------------------------------------------------------------------------------------------
  #  f i e l d M o d i f i e r L I N E W I T H W O R D W R A P
  #----------------------------------------------------------------------------------------------------------
  def fieldModifierLINEWITHWORDWRAP(self):
    # UNFINISHED
    lineWidth = string.atoi(self.stack.pop())
    originalLine = self.stack.pop()
    allLines = []
    aLine = ''
    for x in originalLine.split():
      if (len(aLine + x + ' ') < lineWidth):
        aLine += ' '
        aLine += x
      else:
        allLines.append(aLine)
        aLine = x
    allLines.append(aLine)
    return allLines[self.lineRepeatIndex]

  #----------------------------------------------------------------------------------------------------------
  #  f i e l d M o d i f i e r N U M B E R O F E N T R I E S I N L I N E W I T H W O R D W R A P
  #----------------------------------------------------------------------------------------------------------
  def fieldModifierNUMBEROFENTRIESINLINEWITHWORDWRAP(self):
    # UNFINISHED
    lineWidth = string.atoi(self.stack.pop())
    originalLine = self.stack.pop()
    allLines = []
    aLine = ''
    for x in originalLine.split():
      if (len(aLine + x + ' ') < lineWidth):
        aLine += ' '
        aLine += x
      else:
        allLines.append(aLine)
        aLine = x
    allLines.append(aLine)
    return "%d" % len(allLines)

  #----------------------------------------------------------------------------------------------------------
  #  f i e l d M o d i f i e r T E X E S C A P E
  #----------------------------------------------------------------------------------------------------------
  def fieldModifierTEXESCAPE(self):
    "escape special TEX characters"
    newValue = self.stack.pop()
    newValue = newValue.replace('\\', '\\\\')
    newValue = newValue.replace('$', '\\$')
    newValue = newValue.replace('&', '\\&')
    newValue = newValue.replace('%', '\\%')
    newValue = newValue.replace('#', '\\#')
    newValue = newValue.replace('_', '\\_')
    newValue = newValue.replace('{', '\\{')
    newValue = newValue.replace('}', '\\}')
    return newValue

  #----------------------------------------------------------------------------------------------------------
  #  f i e l d M o d i f i e r N O H T M L
  #----------------------------------------------------------------------------------------------------------
  def fieldModifierNOHTML(self):
    "strip all HTML out"
    newValue = self.stack.pop()
    return newValue

  #----------------------------------------------------------------------------------------------------------
  #  f i e l d M o d i f i e r H T M L N B S P
  #----------------------------------------------------------------------------------------------------------
  def fieldModifierHTMLNBSP(self):
    value = self.stack.pop()
    newValue = value.replace(' ', '&nbsp;')
    return newValue

  #----------------------------------------------------------------------------------------------------------
  #  f i e l d M o d i f i e r H T M L P A R A G R A P H B R E A K
  #----------------------------------------------------------------------------------------------------------
  def fieldModifierHTMLPARAGRAPHBREAK(self):
    value = self.stack.pop()
    newValue = value.replace('\r\n', '</p><p>')
    newValue = newvalue.replace('\n', '</p><p>')
    return newValue

  #----------------------------------------------------------------------------------------------------------
  #  f i e l d M o d i f i e r L O O P C O U N T E R
  #----------------------------------------------------------------------------------------------------------
  def fieldModifierLOOPCOUNTER(self):
    value = self.stack.pop()
    return `self.loopController.current()[0]`

  #----------------------------------------------------------------------------------------------------------
  #  f i e l d M o d i f i e r C R E D I T C A R D
  #----------------------------------------------------------------------------------------------------------
  def fieldModifierCREDITCARD(self):
    value = self.stack.pop()
    newValue = ''
    count = 1
    for x in value:
      if (x in string.digits):
        newValue += x
      if (not (count % 4)):
        newValue += ' '
      count += 1
    return newValue

  #----------------------------------------------------------------------------------------------------------
  #  f i e l d M o d i f i e r Z I P
  #----------------------------------------------------------------------------------------------------------
  def fieldModifierZIP(self):
    value = self.stack.pop()
    newValue = ''
    for x in value:
      if (x in string.digits or x in string.letters):
        newValue += x
    value = newValue
    if (len(value) == 6):
      return "%s %s" % (value[0:3], value[3:])
    newValue = ''
    count = 1
    for x in value:
      if (x in string.digits):
        if (count == 6):
          newValue += '-'
        newValue += x
        count += 1
    return newValue

  #----------------------------------------------------------------------------------------------------------
  #  f i e l d M o d i f i e r M A X C H A R A C T E R S
  #----------------------------------------------------------------------------------------------------------
  def fieldModifierMAXCHARACTERS(self):
    maxCharacters = string.atoi(self.stack.pop())
    value = self.stack.pop()
    return value[0:maxCharacters]

  #----------------------------------------------------------------------------------------------------------
  #  f i e l d M o d i f i e r W O R D B R E A K
  #----------------------------------------------------------------------------------------------------------
  def fieldModifierWORDBREAK(self):
    lineWidth = string.atoi(self.stack.pop())
    originalLine = self.stack.pop()
    aLine = ''
    for x in originalLine.split():
      if (len(aLine + x + ' ') < lineWidth):
        if (aLine != ''):
          aLine += ' '
        aLine += x
      else:
        return aLine
    return aLine

  #----------------------------------------------------------------------------------------------------------
  #  f i e l d M o d i f i e r E X P I R A T I O N D A T E
  #----------------------------------------------------------------------------------------------------------
  def fieldModifierEXPIRATIONDATE(self):
    value = self.stack.pop()
    twoPartDate = value.split('/');
    newValue = string.zfill(twoPartDate[0], 2) + '/' + string.zfill(twoPartDate[1], 2)[-2:]
    return newValue

  #----------------------------------------------------------------------------------------------------------
  #  f i e l d M o d i f i e r S P A R K L I N E S
  #----------------------------------------------------------------------------------------------------------
  def fieldModifierSPARKLINES(self):
    import Image, ImageDraw
    import StringIO
    import urllib
    import cPickle

    value = self.stack.pop()
    
    value = cPickle.loads(value)
    
    im = Image.new("RGB", (len(value)*2, 15), 'white')
    draw = ImageDraw.Draw(im)
    for (r, i) in zip(value, range(0, len(value)*2, 2)):
      color = (r > 50) and "red" or "gray"
      draw.line((i, im.size[1]-r/10-4, i, (im.size[1]-r/10)), fill=color)
    del draw
  
    f = StringIO.StringIO()
    im.save(f, "PNG")
    return 'data:image/png,' + urllib.quote(f.getvalue())

  #----------------------------------------------------------------------------------------------------------
  #  f i e l d M o d i f i e r N O T R A I L I N G U N D E R S C O R E
  #----------------------------------------------------------------------------------------------------------
  def fieldModifierNOTRAILINGUNDERSCORE(self):
    value = self.stack.pop()
    try:
      while value[-1] == '_':
        value = value[:-1]
    except:
      pass

    return value


#============================================================================================================
#
#  T e m p l a t e
#
#============================================================================================================
class Template(list):
  #----------------------------------------------------------------------------------------------------------
  #  _ _ i n i t _ _
  #----------------------------------------------------------------------------------------------------------
  def __init__(self, fileName):
    self.extend(open(fileName).readlines())

  #----------------------------------------------------------------------------------------------------------
  #  g e t L i n e
  #----------------------------------------------------------------------------------------------------------
  def getLine (self, index):
    return self[index]


#============================================================================================================
#
#  S t r i n g T e m p l a t e
#
#============================================================================================================
class StringTemplate(list):
  #----------------------------------------------------------------------------------------------------------
  #  _ _ i n i t _ _
  #----------------------------------------------------------------------------------------------------------
  def __init__(self, aString):
    self.extend(aString.splitlines())

  #----------------------------------------------------------------------------------------------------------
  #  g e t L i n e
  #----------------------------------------------------------------------------------------------------------
  def getLine (self, index):
    return self[index]



#============================================================================================================
#
#  S u b s t i t u t i o n E n g i n e
#
#============================================================================================================
class SubstitutionEngine:
  scriptLine = 0
  normalLine = 1
  normalOutput = 0
  supressOutput = 1
  supressPending = 2
  supressAll = 3

  #----------------------------------------------------------------------------------------------------------
  #  _ _ i n i t _ _
  #----------------------------------------------------------------------------------------------------------
  def __init__ (self):
    self.outputControlStack = [ SubstitutionEngine.normalOutput ]
    self.lineCounter = 0
    self.lineRepeat = 1
    self.lineRepeatCounter = 1
    self.doubleDoubleQuote = 0
    self.supressNewLine = 0
    self.supressLeadingSpaces = 0
    self.outputText = []
    self.showOutput = 0
    self.defaultModifierList = []
    SubstitutionEngine.scriptCommands = [x for x in SubstitutionEngine.__dict__.keys() if x.startswith('script')]

  #----------------------------------------------------------------------------------------------------------
  #  s t r i n g O u t p u t
  #----------------------------------------------------------------------------------------------------------
  def stringOutput (self):
    return string.join(self.outputText, '')

  #----------------------------------------------------------------------------------------------------------
  #  a c t
  #----------------------------------------------------------------------------------------------------------
  def act (self, template, dictionary):
    self.template = template
    self.dictionary = dictionary
    
    self.dictionary.replace('DOUBLE-DOUBLEQUOTE', 'DOUBLEDOUBLEQUOTE')
    self.dictionary.replace('NUMBER-OF-ENTRIES', 'NUMBEROFENTRIES')
    self.dictionary.replace('LINE-WITH-WORD-WRAP', 'LINEWITHWORDWRAP')
    self.dictionary.replace('NUMBER-OF-ENTRIES-IN-LINE-WITH-WORD-WRAP', 'NUMBEROFENTRIESINLINEWITHWORDWRAP')
    self.dictionary.replace('HTML-PARAGRAPH-BREAK', 'HTMLPARAGRAPHBREAK')
    
    self.loopController = LoopController()
    self.subsitutionDispatcher = SubstitutionDispatcher(self.dictionary, self.loopController)
    self.outputControllerStack = [ 1 ]
    self.outputText = []
    self.outputDestination = ''
    self.outputType = 'w'
    substitutionFieldFindingRegularExpression = re.compile(r"(%%.*?%%)")
    self.lineCounter = 0
    while (self.lineCounter < len(template)):
      x = template.getLine(self.lineCounter)
      # print "---INFO--- [SubstitutionEngine:act] considering: %s" % x
      for self.lineRepeatCounter in range(self.lineRepeat):
        self.subsitutionDispatcher.setLineRepeatIndex(self.lineRepeatCounter)
        tokenizedLine = substitutionFieldFindingRegularExpression.split(x)
        # print tokenizedLine
        newLine = []
        for y in tokenizedLine:
         if (y[0:2] == '%%'):
           aList = y[2:][:-2].split()
           aList = aList[:-1] + self.defaultModifierList + aList[-1:]
           newLine.append(self.subsitutionDispatcher.act(aList))
         elif (y != ''):
           newLine.append(y)

        #print '--> ', newLine
        completeLine = string.join(map(str, newLine), '')
        if (self.doubleDoubleQuote):
          completeLine = completeLine.replace('"', '""')
        if (self.supressNewLine):
          completeLine = completeLine.replace('\n', '')
          completeLine = completeLine.replace('\r', '')
        if (self.supressLeadingSpaces):
          completeLine = completeLine.lstrip()
        tokenizedNewLine = completeLine.split()
        try:
          if (self.interpret(tokenizedNewLine) == SubstitutionEngine.normalLine and self.outputControlStack[-1] == SubstitutionEngine.normalOutput):
            if (self.supressNewLine == SubstitutionEngine.supressPending):
              self.outputText[-1] += completeLine
            else:
              self.outputText.append(completeLine)
              if (self.supressNewLine == SubstitutionEngine.supressOutput):
                self.supressNewLine = SubstitutionEngine.supressPending
            if (self.showOutput):
              print "out:", completeLine,
        except IndexError:
          print "***ERROR*** (Line:", self.lineCounter, ") $$if $$else $$endif mismatch"
          return
      self.lineCounter += 1
    self.output()

  #----------------------------------------------------------------------------------------------------------
  #  o u t p u t
  #----------------------------------------------------------------------------------------------------------
  def output (self):
    #print self.outputText
    if (self.outputDestination != ''):
      #print 'writing output to:', self.outputDestination
      #print '-' * 50
      open(self.outputDestination, self.outputType).writelines(self.outputText)
      self.outputText = []

  #----------------------------------------------------------------------------------------------------------
  #  i s S c r i p t
  #----------------------------------------------------------------------------------------------------------
  def isScript (self, testString):
    testString = testString.lstrip()
    #print 'testing:', testString
    if (testString[0:2] != '$$'):
      #print 'No $$'
      return ''
    testString = 'script' + testString[2:].upper()
    #print 'testing:', testString
    if (testString in SubstitutionEngine.scriptCommands):
      return testString
    else:
      print testString, 'not in', SubstitutionEngine.scriptCommands
      return ''
 
  #----------------------------------------------------------------------------------------------------------
  #  i n t e r p r e t
  #----------------------------------------------------------------------------------------------------------
  def interpret (self, line):
    if (line == []):
      return SubstitutionEngine.normalLine
    command = self.isScript(line[0])
    #print command
    if (command):
      try:
        SubstitutionEngine.__dict__[command](self, line[1:])
      except:
        print "***ERROR***"
        print "           ", line
        raise
      return SubstitutionEngine.scriptLine
    return SubstitutionEngine.normalLine
      
     
  #----------------------------------------------------------------------------------------------------------
  #  s c r i p t
  #
  #    $$
  #
  #    comment line
  #----------------------------------------------------------------------------------------------------------
  def script (self, line):
    pass
   
  #----------------------------------------------------------------------------------------------------------
  #  s c r i p t N O O U T P U T
  #
  #    $$noOutput
  #
  #    eliminates the output file until a new one is set
  #----------------------------------------------------------------------------------------------------------
  def scriptNOOUTPUT (self, line):
    self.output()
    self.outputDestination = ''
   
  #----------------------------------------------------------------------------------------------------------
  #  s c r i p t O U T P U T
  #
  #    $$ouput
  #
  #    same as $$outputStream
  #----------------------------------------------------------------------------------------------------------
  def scriptOUTPUT (self, line):
    self.scriptOUTPUTSTREAM (line)
   
  #----------------------------------------------------------------------------------------------------------
  #  s c r i p t F I L E S T R E A M
  #
  #    $$fileStream
  #
  #    same as $$outputStream
  #----------------------------------------------------------------------------------------------------------
  def scriptFILESTREAM (self, line):
    self.scriptOUTPUTSTREAM (line)
     
  #----------------------------------------------------------------------------------------------------------
  #  s c r i p t O U T P U T S T R E A M
  #
  #    $$ouputStream
  #
  #    sets the output filename
  #----------------------------------------------------------------------------------------------------------
  def scriptOUTPUTSTREAM (self, line):
    if (self.outputControlStack[-1] == SubstitutionEngine.normalOutput):
      length = len(line)
      if (length == 0):
        print "***ERROR*** (Line:", self.lineCounter, ") file name missing on $$outputStream"
      else:
        self.output()
        self.outputDestination = line[0]
     
  #----------------------------------------------------------------------------------------------------------
  #  s c r i p t A P P E N D S T R E A M
  #
  #    $$appendStream
  #
  #    sets the output filename for appending
  #----------------------------------------------------------------------------------------------------------
  def scriptAPPENDSTREAM (self, line):
    if (self.outputControlStack[-1] == SubstitutionEngine.normalOutput):
      self.outputType = 'a'
      self.scriptOUTPUTSTREAM (line)
     
  #----------------------------------------------------------------------------------------------------------
  #  s c r i p t P R I N T D I C T I O N A R Y
  #
  #    $$printDictionary
  #
  #    outputs the Dictionary to standard out
  #----------------------------------------------------------------------------------------------------------
  def scriptPRINTDICTIONARY (self, line):
    if (self.outputControlStack[-1] == SubstitutionEngine.normalOutput):
      print self.dictionary
     
  #----------------------------------------------------------------------------------------------------------
  #  s c r i p t P R I N T
  #
  #    $$print
  #
  #    same as $$cout
  #----------------------------------------------------------------------------------------------------------
  def scriptPRINT (self, line):
    self.scriptCOUT(line)
     
  #----------------------------------------------------------------------------------------------------------
  #  s c r i p t C O U T
  #
  #    $$cout [ values ]
  #
  #    outputs the list of values to standard out
  #----------------------------------------------------------------------------------------------------------
  def scriptCOUT (self, line):
    if (self.outputControlStack[-1] == SubstitutionEngine.normalOutput):
      print string.join(line, ' ')
     
  #----------------------------------------------------------------------------------------------------------
  #  s c r i p t P R I N T O U T P U T C O N T R O L S T A C K
  #
  #    $$printOutputControlStack 
  #
  #    outputs the output control stack to standard out
  #----------------------------------------------------------------------------------------------------------
  def scriptPRINTOUTPUTCONTROLSTACK (self, line):
    if (self.outputControlStack[-1] == SubstitutionEngine.normalOutput):
      print self.outputControlStack
     
  #----------------------------------------------------------------------------------------------------------
  #  s c r i p t N E W D E F I N I T I O N
  #
  #    $$newDefinition variableName [ value ]
  #
  #    enters a new value into the dictionary
  #----------------------------------------------------------------------------------------------------------
  def scriptNEWDEFINITION (self, line):
    if (self.outputControlStack[-1] == SubstitutionEngine.normalOutput):
      length = len(line)
      if (length == 0):
        print "***ERROR*** (Line:", self.lineCounter, ") variable name missing on $$newDefinition"
      elif (length == 1):
        self.dictionary.insert(line[0], '')
      else:
        self.dictionary.insert(line[0], string.join(line[1:], ' '))
         
  #----------------------------------------------------------------------------------------------------------
  #  s c r i p t N E W F I R S T D E F I N I T I O N
  #
  #    $$newFirstDefinition variableName [ value ]
  #
  #    enters a new value into the dictionary
  #----------------------------------------------------------------------------------------------------------
  def scriptNEWFIRSTDEFINITION (self, line):
    if (self.outputControlStack[-1] == SubstitutionEngine.normalOutput):
      length = len(line)
      if (length == 0):
        print "***ERROR*** (Line:", self.lineCounter, ") variable name missing on $$newFirstDefinition"
      elif (length == 1):
        self.dictionary.insertAtBeginning(line[0], '')
      else:
        self.dictionary.insertAtBeginning(line[0], string.join(line[1:], ' '))
         
  #----------------------------------------------------------------------------------------------------------
  #  s c r i p t C H A N G E D E F I N I T I O N
  #
  #    $$changeDefinition variableName [ value ]
  #
  #    enters a new value into the dictionary
  #----------------------------------------------------------------------------------------------------------
  def scriptCHANGEDEFINITION (self, line):
    if (self.outputControlStack[-1] == SubstitutionEngine.normalOutput):
      length = len(line)
      if (length == 0):
        print "***ERROR*** (Line:", self.lineCounter, ") variable name missing on $$changeDefinition"
      elif (length == 1):
        self.dictionary.remove(line[0])
        self.dictionary.insert(line[0], '')
      else:
        self.dictionary.remove(line[0])
        self.dictionary.insert(line[0], string.join(line[1:], ' '))
         
  #----------------------------------------------------------------------------------------------------------
  #  s c r i p t R E M O V E D E F I N I T I O N
  #
  #    $$removeDefinition variableName 
  #
  #    removes a definition from the dictionary
  #----------------------------------------------------------------------------------------------------------
  def scriptREMOVEDEFINITION (self, line):
    if (self.outputControlStack[-1] == SubstitutionEngine.normalOutput):
      length = len(line)
      if (length == 0):
        print "***ERROR*** (Line:", self.lineCounter, ") variable name missing on $$removeDefinition"
      else:
        self.dictionary.remove(line[0])
         
  #----------------------------------------------------------------------------------------------------------
  #  s c r i p t D E F A U L T M O D I F I E R S
  #
  #    $$removeDefinition variableName 
  #
  #    removes a definition from the dictionary
  #----------------------------------------------------------------------------------------------------------
  def scriptDEFAULTMODIFIERS (self, line):
    if (self.outputControlStack[-1] == SubstitutionEngine.normalOutput):
      self.defaultModifierList = line[:]
      #print self.defaultModifierList
         
  #----------------------------------------------------------------------------------------------------------
  #  s c r i p t L I N E R E P E A T
  #
  #    $$lineRepeat [ [ value ] ... ]
  #
  #    All lines up to the next $$endLineRepeat are repeated 'value' times.  
  #    It chooses the maximum of the list of values
  #----------------------------------------------------------------------------------------------------------
  def scriptLINEREPEAT (self, line):
    if (self.outputControlStack[-1] == SubstitutionEngine.normalOutput):
      maxInteger = max ( map (string.atoi, line))
      self.lineRepeat = maxInteger
      
  #----------------------------------------------------------------------------------------------------------
  #  s c r i p t E N D L I N E R E P E A T
  #
  #    $$endLineRepeat
  #
  #----------------------------------------------------------------------------------------------------------
  def scriptENDLINEREPEAT (self, line):
    if (self.outputControlStack[-1] == SubstitutionEngine.normalOutput):
      self.lineRepeat = 1
      
  #----------------------------------------------------------------------------------------------------------
  #  s c r i p t D O U B L E D O U B L E Q U O T E
  #
  #    $$doubleDoubleQuote 
  #
  #    All double quotes are doubled until $$endDoubleDoubleQuote
  #----------------------------------------------------------------------------------------------------------
  def scriptDOUBLEDOUBLEQUOTE (self, line):
    if (self.outputControlStack[-1] == SubstitutionEngine.normalOutput):
      self.doubleDoubleQuote = 1

  #----------------------------------------------------------------------------------------------------------
  #  s c r i p t E N D D O U B L E D O U B L E Q U O T E
  #
  #    $$endDoubleDoubleQuote 
  #
  #----------------------------------------------------------------------------------------------------------
  def scriptENDDOUBLEDOUBLEQUOTE (self, line):
    if (self.outputControlStack[-1] == SubstitutionEngine.normalOutput):
      self.doubleDoubleQuote = 0

  #----------------------------------------------------------------------------------------------------------
  #  s c r i p t S U P P R E S S N E W L I N E
  #
  #    $$suppressNewLine 
  #
  #    All newlines are supressed - end with $$normalNewLine
  #----------------------------------------------------------------------------------------------------------
  def scriptSUPPRESSNEWLINE (self, line):
    if (self.outputControlStack[-1] == SubstitutionEngine.normalOutput):
      self.supressNewLine = 1

  #----------------------------------------------------------------------------------------------------------
  #  s c r i p t N O R M A L N E W L I N E
  #
  #    $$normalNewLine 
  #
  #----------------------------------------------------------------------------------------------------------
  def scriptNORMALNEWLINE (self, line):
    if (self.outputControlStack[-1] == SubstitutionEngine.normalOutput):
      self.supressNewLine = 0

  #----------------------------------------------------------------------------------------------------------
  #  s c r i p t S U P P R E S S L E A D I N G S P A C E S
  #
  #    $$suppressLeadingSpaces 
  #
  #    All leading spaces on a line are supressed - end with $$normalLeadingSpaces
  #----------------------------------------------------------------------------------------------------------
  def scriptSUPPRESSLEADINGSPACES (self, line):
    if (self.outputControlStack[-1] == SubstitutionEngine.normalOutput):
      self.supressLeadingSpaces = 1

  #----------------------------------------------------------------------------------------------------------
  #  s c r i p t N O R M A L L E A D I N G S P A C E S
  #
  #    $$normalLeadingSpaces 
  #
  #----------------------------------------------------------------------------------------------------------
  def scriptNORMALLEADINGSPACES (self, line):
    if (self.outputControlStack[-1] == SubstitutionEngine.normalOutput):
      self.supressLeadingSpaces = 0

  #----------------------------------------------------------------------------------------------------------
  #  s c r i p t S U P P R E S S O U T P U T
  #
  #    $$suppressOutput
  #
  #    same as $$never - close with $$endif or $$normalOutput
  #----------------------------------------------------------------------------------------------------------
  def scriptSUPPRESSOUTPUT (self, line):
    scriptNEVER(line)

  #----------------------------------------------------------------------------------------------------------
  #  s c r i p t N E V E R
  #
  #    $$never
  #
  #    an if varient that always pushes 'false'  close with $$endif or $$normalOutput
  #----------------------------------------------------------------------------------------------------------
  def scriptNEVER (self, line):
    if (self.outputControlStack[-1] == SubstitutionEngine.normalOutput):
      self.outputControlStack.append(SubstitutionEngine.supressOutput)
    elif (self.outputControlStack[-1] == SubstitutionEngine.supressPending):
      self.outputControlStack.append(SubstitutionEngine.supressPending)

  #----------------------------------------------------------------------------------------------------------
  #  s c r i p t I F I N
  #
  #    $$ifIn variableName [ value ]
  #
  #    (1) with just the variableName this function will push true 'true' if the variable
  #        exists in the dictionary, other wise it pushes a 'false' value.
  #    (2) with a value, this function will push 'true' if the variable exists in the 
  #        database and if the value is in the values list of that variable, otherwise
  #        it pushes a 'false' value
  #----------------------------------------------------------------------------------------------------------
  def scriptIFIN (self, line):
    if (self.outputControlStack[-1] == SubstitutionEngine.normalOutput):
      try:
        if (self.dictionary.has_key(line[0])):
          if (len(line) > 1):
            if (self.dictionary.contains(line[0], line[1])):
              self.outputControlStack.append(SubstitutionEngine.normalOutput)
            else:
              self.outputControlStack.append(SubstitutionEngine.supressOutput)
          else:
            self.outputControlStack.append(SubstitutionEngine.normalOutput)
        else:
          self.outputControlStack.append(SubstitutionEngine.supressOutput)
      except IndexError:
        print "***ERROR*** (Line:", self.lineCounter, ") key name missing on $$ifIn"
        self.outputControlStack.append(SubstitutionEngine.normalOutput)
    else:
      self.outputControlStack.append(SubstitutionEngine.supressPending)

  #----------------------------------------------------------------------------------------------------------
  #  s c r i p t I F D E F I N E D
  #
  #    $$ifDefined variableName 
  #
  #    pushes true if the value is found in the dictionary
  #----------------------------------------------------------------------------------------------------------
  def scriptIFDEFINED (self, line):
    self.scriptIFIN(line)

  #----------------------------------------------------------------------------------------------------------
  #  s c r i p t I F N O T I N
  #
  #    $$ifNotIn variableName [ value ]
  #
  #    (1) with just the variableName this function will push true 'false' if the variable
  #        exists in the dictionary, other wise it pushes a 'true' value.
  #    (2) with a value, this function will push 'false' if the variable exists in the 
  #        database and if the value is in the values list of that variable, otherwise
  #        it pushes a 'true' value
  #----------------------------------------------------------------------------------------------------------
  def scriptIFNOTIN (self, line):
    if (self.outputControlStack[-1] == SubstitutionEngine.normalOutput):
      try:
        if (self.dictionary.has_key(line[0])):
          if (len(line) > 1):
            if (self.dictionary.contains(line[0], line[1])):
              self.outputControlStack.append(SubstitutionEngine.supressOutput)
            else:
              self.outputControlStack.append(SubstitutionEngine.normalOutput)
          else:
            self.outputControlStack.append(SubstitutionEngine.supressOutput)
        else:
          self.outputControlStack.append(SubstitutionEngine.normalOutput)
      except IndexError:
        print "***ERROR*** (Line:", self.lineCounter, ") key name missing on $$ifNotIn"
        self.outputControlStack.append(SubstitutionEngine.normalOutput)
    else:
      self.outputControlStack.append(SubstitutionEngine.supressPending)

  #----------------------------------------------------------------------------------------------------------
  #  s c r i p t I F N O T D E F I N E D
  #
  #    $$ifNotDefined variableName 
  #
  #    pushes false if the value is found in the dictionary
  #----------------------------------------------------------------------------------------------------------
  def scriptIFNOTDEFINED (self, line):
    self.scriptIFNOTIN(line)

  #----------------------------------------------------------------------------------------------------------
  #  s c r i p t I F N U L L D E F I N I T I O N
  #
  #    $$ifNullDefinition variableName
  #
  #    (1) with just the variableName this function will push true 'true' if the variable
  #        doesn't exist in the dictionary OR
  #    (2) this function will push 'true' if the variable exists in the 
  #        database and if the current value of that variable is null
  #    (3) it pushes a 'false' value
  #----------------------------------------------------------------------------------------------------------
  def scriptIFNULLDEFINITION (self, line):
    if (self.outputControlStack[-1] == SubstitutionEngine.normalOutput):
      try:
        if (self.dictionary.has_key(line[0])):
          self.scriptIFCURRENT([ line[0], '' ])
        else:
          self.outputControlStack.append(SubstitutionEngine.normalOutput)
      except IndexError:
        print "***ERROR*** (Line:", self.lineCounter, ") key name missing on $$ifNullDefinition"
        self.outputControlStack.append(SubstitutionEngine.normalOutput)
    else:
      self.outputControlStack.append(SubstitutionEngine.supressPending)

  #----------------------------------------------------------------------------------------------------------
  #  s c r i p t I F C U R R E N T
  #
  #    $$ifCurrent variableName [ value ]
  #
  #    (1) with just the variableName this function will push true 'true' if the variable
  #        exists in the dictionary, other wise it pushes a 'false' value.
  #    (2) with a value, this function will push 'true' if the variable exists in the 
  #        database and if the value is the current value in the values list of that variable, otherwise
  #        it pushes a 'false' value
  #----------------------------------------------------------------------------------------------------------
  def scriptIFCURRENT (self, line):
    if (self.outputControlStack[-1] == SubstitutionEngine.normalOutput):
      try:
        if (self.dictionary.has_key(line[0])):
          if (len(line) > 1):
            currentValue = self.dictionary.lookup(line[0], self.loopController)
            if (currentValue == line[1]):
              self.outputControlStack.append(SubstitutionEngine.normalOutput)
            else:
              self.outputControlStack.append(SubstitutionEngine.supressOutput)
          else:
            self.outputControlStack.append(SubstitutionEngine.normalOutput)
        else:
          self.outputControlStack.append(SubstitutionEngine.supressOutput)
      except IndexError:
        print "***ERROR*** (Line:", self.lineCounter, ") key name missing on $$ifCurrent"
        self.outputControlStack.append(SubstitutionEngine.normalOutput)
    else:
      self.outputControlStack.append(SubstitutionEngine.supressPending)

  #----------------------------------------------------------------------------------------------------------
  #  s c r i p t I F N E X T
  #
  #    $$ifNext variableName [ value ]
  #
  #    (1) with just the variableName this function will push true 'true' if the variable
  #        exists in the dictionary, other wise it pushes a 'false' value.
  #    (2) with a value, this function will push 'true' if the variable exists in the 
  #        database and if the value is the next value in the values list of that variable, otherwise
  #        it pushes a 'false' value
  #----------------------------------------------------------------------------------------------------------
  def scriptIFNEXT (self, line):
    if (self.outputControlStack[-1] == SubstitutionEngine.normalOutput):
      try:
        if (self.dictionary.has_key(line[0])):
          if (len(line) > 1):
            currentValue = self.dictionary.lookupNext(line[0], self.loopController)
            if (currentValue == line[1]):
              self.outputControlStack.append(SubstitutionEngine.normalOutput)
            else:
              self.outputControlStack.append(SubstitutionEngine.supressOutput)
          else:
            self.outputControlStack.append(SubstitutionEngine.normalOutput)
        else:
          self.outputControlStack.append(SubstitutionEngine.supressOutput)
      except IndexError:
        print "***ERROR*** (Line:", self.lineCounter, ") key name missing on $$ifNext"
        self.outputControlStack.append(SubstitutionEngine.normalOutput)
    else:
      self.outputControlStack.append(SubstitutionEngine.supressPending)

  #----------------------------------------------------------------------------------------------------------
  #  s c r i p t I F A L L
  #
  #    $$ifAll variableName [ value ]
  #
  #    (1) with just the variableName this function will push true 'true' if the variable
  #        exists in the dictionary, other wise it pushes a 'false' value.
  #    (2) with a value, this function will push 'true' if the variable exists in the 
  #        dictionary and if the value is in all of the values list of that variable, otherwise
  #        it pushes a 'false' value
  #----------------------------------------------------------------------------------------------------------
  def scriptIFALL (self, line):
    if (self.outputControlStack[-1] == SubstitutionEngine.normalOutput):
      try:
        if (self.dictionary.has_key(line[0])):
          if (len(line) > 1):
            if (self.dictionary.containsAll(line[0], line[1])):
              self.outputControlStack.append(SubstitutionEngine.normalOutput)
            else:
              self.outputControlStack.append(SubstitutionEngine.supressOutput)
          else:
            self.outputControlStack.append(SubstitutionEngine.normalOutput)
        else:
          self.outputControlStack.append(SubstitutionEngine.supressOutput)
      except IndexError:
        print "***ERROR*** (Line:", self.lineCounter, ") key name missing on $$ifAll"
        self.outputControlStack.append(SubstitutionEngine.normalOutput)
    else:
      self.outputControlStack.append(SubstitutionEngine.supressPending)

  #----------------------------------------------------------------------------------------------------------
  #  s c r i p t I F Z E R O O R N E G A T I V E
  #
  #    $$ifZeroOrNegative value 
  #
  #    pushes true if the value is zero or negative
  #----------------------------------------------------------------------------------------------------------
  def scriptIFZEROORNEGATIVE (self, line):
    if (self.outputControlStack[-1] == SubstitutionEngine.normalOutput):
      try:
        if (string.atoi(line[0]) <= 0):
          self.outputControlStack.append(SubstitutionEngine.normalOutput)
        else:
          self.outputControlStack.append(SubstitutionEngine.supressOutput)
      except IndexError:
        print "***ERROR*** (Line:", self.lineCounter, ") value missing on $$ifZeroOrNegative"
        self.outputControlStack.append(SubstitutionEngine.normalOutput)
    else:
      self.outputControlStack.append(SubstitutionEngine.supressPending)

  #----------------------------------------------------------------------------------------------------------
  #  s c r i p t I F N O T N O N E
  #
  #    $$ifNotNone value 
  #
  #    pushes true if the value is not None
  #----------------------------------------------------------------------------------------------------------
  def scriptIFNOTNONE (self, line):
    if (self.outputControlStack[-1] == SubstitutionEngine.normalOutput):
      try:
        if self.dictionary.lookup(line[0], self.loopController, noConversion) is not None:
          # print "NOT NONE FOUND: ", self.dictionary.lookup(line[0], self.loopController)
          self.outputControlStack.append(SubstitutionEngine.normalOutput)
        else:
          self.outputControlStack.append(SubstitutionEngine.supressOutput)
      except IndexError:
        print "***ERROR*** (Line:", self.lineCounter, ") value missing on $$ifNotNone"
        self.outputControlStack.append(SubstitutionEngine.normalOutput)
    else:
      self.outputControlStack.append(SubstitutionEngine.supressPending)

  #----------------------------------------------------------------------------------------------------------
  #  s c r i p t I F N E G A T I V E
  #
  #    $$ifNegative value 
  #
  #    pushes true if the value is negative
  #----------------------------------------------------------------------------------------------------------
  def scriptIFNEGATIVE (self, line):
    if (self.outputControlStack[-1] == SubstitutionEngine.normalOutput):
      try:
        if (string.atoi(line[0]) < 0):
          self.outputControlStack.append(SubstitutionEngine.normalOutput)
        else:
          self.outputControlStack.append(SubstitutionEngine.supressOutput)
      except IndexError:
        print "***ERROR*** (Line:", self.lineCounter, ") value missing on $$ifNegative"
        self.outputControlStack.append(SubstitutionEngine.normalOutput)
    else:
      self.outputControlStack.append(SubstitutionEngine.supressPending)

  #----------------------------------------------------------------------------------------------------------
  #  s c r i p t I F G R E A T E R
  #
  #    $$ifGreater leftValue rightValue 
  #
  #    pushes true if the number leftValue is greater than rightValue
  #----------------------------------------------------------------------------------------------------------
  def scriptIFGREATER (self, line):
    if (self.outputControlStack[-1] == SubstitutionEngine.normalOutput):
      leftValue = 0
      rightValue = 0
      
      try:
        leftValue = string.atoi(line[0])
      except ValueError:
        try:
          leftValue = string.atof(line[0])
        except ValueError:
          leftValue = line[0]
      except IndexError:
        print "***ERROR*** (Line:", self.lineCounter, ") left value missing on $$ifGreater"
        self.outputControlStack.append(SubstitutionEngine.normalOutput)
        return
        
      try:
        rightValue = string.atoi(line[1])
      except ValueError:
        try:
          rightValue = string.atof(line[1])
        except ValueError:
          rightValue = line[1]
      except IndexError:
        print "***ERROR*** (Line:", self.lineCounter, ") right value missing on $$ifGreater"
        self.outputControlStack.append(SubstitutionEngine.normalOutput)
        return
        
      if type(leftValue) == str:
        rightValue = line[1]
      if type(rightValue) == str:
        leftValue = line[0]
        
      if (leftValue > rightValue):
        self.outputControlStack.append(SubstitutionEngine.normalOutput)
      else:
        self.outputControlStack.append(SubstitutionEngine.supressOutput)
    else:
      self.outputControlStack.append(SubstitutionEngine.supressPending)

  #----------------------------------------------------------------------------------------------------------
  #  s c r i p t E Q U A L
  #
  #    $$ifEqual leftValue rightValue 
  #
  #    pushes true if the number leftValue is equal to the rightValue
  #----------------------------------------------------------------------------------------------------------
  def scriptIFEQUAL (self, line):
    if (self.outputControlStack[-1] == SubstitutionEngine.normalOutput):
      leftValue = line[0]
      rightValue = line[1]
      if (leftValue == rightValue):
        self.outputControlStack.append(SubstitutionEngine.normalOutput)
      else:
        self.outputControlStack.append(SubstitutionEngine.supressOutput)
    else:
      self.outputControlStack.append(SubstitutionEngine.supressPending)

  #----------------------------------------------------------------------------------------------------------
  #  s c r i p t N O T E Q U A L
  #
  #    $$ifNotEqual leftValue rightValue 
  #
  #    pushes true if the number leftValue is equal to the rightValue
  #----------------------------------------------------------------------------------------------------------
  def scriptIFNOTEQUAL (self, line):
    if (self.outputControlStack[-1] == SubstitutionEngine.normalOutput):
      leftValue = line[0]
      rightValue = line[1]
      if (leftValue != rightValue):
        self.outputControlStack.append(SubstitutionEngine.normalOutput)
      else:
        self.outputControlStack.append(SubstitutionEngine.supressOutput)
    else:
      self.outputControlStack.append(SubstitutionEngine.supressPending)

  #----------------------------------------------------------------------------------------------------------
  #  s c r i p t I F N U L L
  #
  #    $$ifNull [ value ] 
  #
  #    pushes true if a non-white space value is provided
  #----------------------------------------------------------------------------------------------------------
  def scriptIFNULL (self, line):
    if (self.outputControlStack[-1] == SubstitutionEngine.normalOutput):
      if (len(line) == 0):
        self.outputControlStack.append(SubstitutionEngine.normalOutput)
      else:
        self.outputControlStack.append(SubstitutionEngine.supressOutput)
    else:
      self.outputControlStack.append(SubstitutionEngine.supressPending)

  #----------------------------------------------------------------------------------------------------------
  #  s c r i p t I F N O T N U L L
  #
  #    $$ifNotNull [ value ] 
  #
  #    pushes false if a non-white space value is provided
  #----------------------------------------------------------------------------------------------------------
  def scriptIFNOTNULL (self, line):
    if (self.outputControlStack[-1] == SubstitutionEngine.normalOutput):
      if (len(line) != 0):
        self.outputControlStack.append(SubstitutionEngine.normalOutput)
      else:
        self.outputControlStack.append(SubstitutionEngine.supressOutput)
    else:
      self.outputControlStack.append(SubstitutionEngine.supressPending)

  #----------------------------------------------------------------------------------------------------------
  #  s c r i p t I F I N C R E M E N T
  #
  #    $$ifIncrement integerValue
  #
  #    pushes 'true' if the current loop counter is evenly divisible by the 'integerValue', otherwise 
  #    it pushes a 'false' value
  #----------------------------------------------------------------------------------------------------------
  def scriptIFINCREMENT (self, line):
    if (self.outputControlStack[-1] == SubstitutionEngine.normalOutput):
      try:
        integerValue = string.atoi(line[0])
	# print "---INFO---", self.loopController.current()[0], integerValue, self.loopController.current()[0] % integerValue
        if (self.loopController.current()[0] % integerValue):
          self.outputControlStack.append(SubstitutionEngine.supressOutput) 
        else:
          self.outputControlStack.append(SubstitutionEngine.normalOutput)
      except IndexError:
        print "***ERROR*** (Line:", self.lineCounter, ") value missing on $$ifIncrement"
        self.outputControlStack.append(SubstitutionEngine.normalOutput)
    else:
      self.outputControlStack.append(SubstitutionEngine.supressPending)

  #----------------------------------------------------------------------------------------------------------
  #  s c r i p t I F N O T L A S T L O O P
  #
  #    $$ifNotLastLoop 
  #
  #    pushes 'true' if the current loop counter is on its last value
  #----------------------------------------------------------------------------------------------------------
  def scriptIFNOTLASTLOOP (self, line):
    if (self.outputControlStack[-1] == SubstitutionEngine.normalOutput):
      if (self.loopController[-1].isLast()):
        self.outputControlStack.append(SubstitutionEngine.supressOutput)
      else:
        self.outputControlStack.append(SubstitutionEngine.normalOutput)
    else:
      self.outputControlStack.append(SubstitutionEngine.supressPending)

  #----------------------------------------------------------------------------------------------------------
  #  s c r i p t I F H A L F T H R O U G H L O O P
  #
  #    $$ifHalfThroughLoop 
  #
  #    pushes 'true' if the current loop counter is halfway through its current loop
  #----------------------------------------------------------------------------------------------------------
  def scriptIFHALFTHROUGHLOOP (self, line):
    if (self.outputControlStack[-1] == SubstitutionEngine.normalOutput):
      if (self.loopController[0].current() == (self.loopController[0].lastValue() + 1) / 2):
        self.outputControlStack.append(SubstitutionEngine.normalOutput)
      else:
        self.outputControlStack.append(SubstitutionEngine.supressOutput)
    else:
      self.outputControlStack.append(SubstitutionEngine.supressPending)

  #----------------------------------------------------------------------------------------------------------
  #  s c r i p t I F N O T F I R S T L O O P
  #
  #    $$ifNotFirstLoop 
  #
  #    pushes 'true' if the current loop counter is not in its first iteration
  #----------------------------------------------------------------------------------------------------------
  def scriptIFNOTFIRSTLOOP (self, line):
    if (self.outputControlStack[-1] == SubstitutionEngine.normalOutput):
      if (self.loopController[-1].current() > 0):
        self.outputControlStack.append(SubstitutionEngine.normalOutput)
      else:
        self.outputControlStack.append(SubstitutionEngine.supressOutput)
    else:
      self.outputControlStack.append(SubstitutionEngine.supressPending)

  #----------------------------------------------------------------------------------------------------------
  #  s c r i p t I F V A L U E V A L I D
  #
  #    $$ifNextValueValid 
  #
  #    pushes 'true' if the current loop counter is not on its last value
  #----------------------------------------------------------------------------------------------------------
  def scriptIFVALUEVALID (self, line):
    if (self.outputControlStack[-1] == SubstitutionEngine.normalOutput):
      if (self.loopController[-1].isLast()):
        self.outputControlStack.append(SubstitutionEngine.normalOutput)
      else:
        self.outputControlStack.append(SubstitutionEngine.supressOutput)
    else:
      self.outputControlStack.append(SubstitutionEngine.supressPending)

  #----------------------------------------------------------------------------------------------------------
  #  s c r i p t I F F I L E E X I S T S
  #
  #    $$ifFileExists fileName
  #
  #    pushes 'true' if the current loop counter is not on its last value
  #----------------------------------------------------------------------------------------------------------
  def scriptIFFILEEXISTS (self, line):
    if (self.outputControlStack[-1] == SubstitutionEngine.normalOutput):
      try:
        if (os.path.exists(line[0])):
          self.outputControlStack.append(SubstitutionEngine.normalOutput) 
        else:
          self.outputControlStack.append(SubstitutionEngine.supressOutput)
      except IndexError:
        print "***ERROR*** (Line:", self.lineCounter, ") fileName missing on $$ifFileExists"
        self.outputControlStack.append(SubstitutionEngine.normalOutput)
    else:
      self.outputControlStack.append(SubstitutionEngine.supressPending)

  #----------------------------------------------------------------------------------------------------------
  #  s c r i p t E L S E
  #----------------------------------------------------------------------------------------------------------
  def scriptELSE (self, line):
    if (len(self.outputControlStack) > 1):
      if (self.outputControlStack[-1] == SubstitutionEngine.normalOutput):
        self.outputControlStack[-1] = SubstitutionEngine.supressAll
      elif (self.outputControlStack[-1] == SubstitutionEngine.supressPending or
            self.outputControlStack[-1] == SubstitutionEngine.supressAll):
        pass
      else:
        #need to look into implementing the $$else $$ifXXX construct
        if (line == []):
          self.outputControlStack[-1] = SubstitutionEngine.normalOutput
        else:
          print '$$else $$if  has been found ', line
          self.outputControlStack.pop()
          self.interpret(line)
    else:
      print "***ERROR*** (Line:", self.lineCounter, ") $$if $$else $$endif mismatch detected on $$else"
  
  #----------------------------------------------------------------------------------------------------------
  #  s c r i p t N O R M A L O U T P U T
  #
  #  same as $$endif - used to close $$suppressOutput
  #----------------------------------------------------------------------------------------------------------
  def scriptNORMALOUTPUT (self, line):
    scriptENDIF(line)

  #----------------------------------------------------------------------------------------------------------
  #  s c r i p t E N D I F
  #----------------------------------------------------------------------------------------------------------
  def scriptENDIF (self, line):
    if (len(self.outputControlStack) > 1):
      self.outputControlStack.pop()
    else:
      print "***ERROR*** (Line:", self.lineCounter, ") $$if $$else $$endif mismatch detected on $$endif"

  #----------------------------------------------------------------------------------------------------------
  #  s c r i p t R E P E A T
  #----------------------------------------------------------------------------------------------------------
  def scriptREPEAT (self, line):
    scriptLOOP (line)
      
  #----------------------------------------------------------------------------------------------------------
  #  s c r i p t L O O P
  #
  #  $$loop variableName [ incrementValue [ absoluteMaxValue ] ]
  #----------------------------------------------------------------------------------------------------------
  def scriptLOOP (self, line):
    if (self.outputControlStack[-1] == SubstitutionEngine.normalOutput):
      # print "---INFO--- SubstitutionEngine: ", self.loopController
      length = len(line)
      incrementValue = 1
      absoluteMaxValue = 10000
      if (length == 0):
        print "***ERROR*** (Line:", self.lineCounter, ") $$loop missing variableName"
        return
      if (length == 3):
        absoluteMaxValue = string.atoi(line[2])
      if (length >= 2):
        incrementValue = string.atoi(line[1])
      self.loopController.newLoop(min([self.dictionary.lookupNumberOfEntries(line[0], self.loopController), absoluteMaxValue ]), incrementValue, self.lineCounter + 1)

  #----------------------------------------------------------------------------------------------------------
  #  s c r i p t L O O P D U M P
  #
  #  $$loopdump 
  #----------------------------------------------------------------------------------------------------------
  def scriptLOOPDUMP (self, line):
    if (self.outputControlStack[-1] == SubstitutionEngine.normalOutput):
      print "---INFO--- SubstitutionEngine:LoopDump ", self.loopController
 
  #----------------------------------------------------------------------------------------------------------
  #  s c r i p t E N D
  #
  #  $$end
  #----------------------------------------------------------------------------------------------------------
  def scriptEND (self, line):
    if (self.outputControlStack[-1] == SubstitutionEngine.normalOutput):
      if not self.loopController.increment():
        self.lineCounter = self.loopController.jump() - 1

#============================================================================================================
#
#  M o d u l e F u n c t i o n s
#
#============================================================================================================
#----------------------------------------------------------------------------------------------------------
#  i n t e r p r e t F r o m S t r i n g
#----------------------------------------------------------------------------------------------------------
def interpretFromString (aTemplate, aDictionary, templateType=StringTemplate, dictionaryType=Dictionary, engineType=SubstitutionEngine):
  return interpret(aTemplate, aDictionary, templateType, dictionaryType, engineType)

#----------------------------------------------------------------------------------------------------------
#  i n t e r p r e t
#----------------------------------------------------------------------------------------------------------
def interpret (aTemplate, aDictionary, templateType=Template, dictionaryType=Dictionary, engineType=SubstitutionEngine):
  if (type(aTemplate) == str):
    aTemplate = templateType(aTemplate)
  if (type(aDictionary) == str):
    aDictionaryFileName = aDictionary
    aDictionary = dictionaryType()
    aDictionary.insertDictionaryFromFile(aDictionaryFileName)
  anEngine = engineType()
  anEngine.act(aTemplate, aDictionary)
  return anEngine.stringOutput()


#******************************************************
 
if __name__ == "__main__":

 
  def test1():
    d = Dictionary()
    d.insert ('id', '1')
    d.insert ('id', '2')
    d.insert ('id', '3')
    d.insert ('iid', 'fred')
    d.insert ('iid', 'sally')
    d.insert ('iid', 'george')
    d.insert ('null', '')
    d.insert ('name', 'Object #1')
    d.insert ('name', 'Object #2')
    d.insert ('name', 'Object #3')
    d.insert ('price', '5.5')
    d.insert ('price', '10.95')
    d.insert ('price', '7.5')
    d.insert ('threshold', '2')
    t = StringTemplate("""
  $$loop id
  %%FIRSTONLY isfirstonly%% - %%NOTLAST isnotlast%% - %%LASTONLY islastonly%% === 
  
  $$end
    """)
    se = SubstitutionEngine()
    se.act(t, d)
    print se.stringOutput()
     
     
  def test2():
    st = StringTemplate('FileName.%%LEFTFILL 0 3 SEQ filesequence%%')
    d = Dictionary()
    se = SubstitutionEngine()
    se.act(st, d)
    print '--->', se.stringOutput()
    
  def test3():
    st = StringTemplate("""
    $$defaultmodifiers NOWHITESPACE
    ===%%TEXESCAPE alpha%%==="""
    )
    d = Dictionary()
    aString = '$ & % # _ { } \\'
    d.insert ('alpha', aString)
    se = SubstitutionEngine()
    se.act(st, d)
    print '===>', aString
    print '--->', se.stringOutput()
    
  def test4():
    st = StringTemplate("""
    $$ $$defaultmodifiers NOHTML
    ===%%NOHTML alpha%%==="""
    )
    d = Dictionary()
    aString = '<a href="somerose.html">Some Rose</a>'
    d.insert ('alpha', aString)
    se = SubstitutionEngine()
    se.act(st, d)
    print '===>', aString
    print '--->', se.stringOutput()
  
  
  def test5():
    d = Dictionary()
    d.replace ('id', '1')
    d.insert ('id', '2')
    d.insert ('id', '3')
    d.insert ('iid', 'fred')
    d.insert ('iid', 'sally')
    d.insert ('iid', 'george')
    d.insert ('null', '')
    d.insert ('name', 'Object #1   ')
    d.insert ('name', 'Object #2')
    d.insert ('name', 'Object #3')
    d.insert ('price', '5.5')
    d.insert ('price', '10.95')
    d.insert ('price', '7.5')
    d.insert ('threshold', '2')
  
    print interpretFromString("'%%STRIP name%%'", d)
    print interpretFromString("%%SEQFILL 6 seq%%", d)
    print interpret("%%SPACEOUT HowdyHowdyHowdy%%%%SEQFILL 6 seq%%", d, StringTemplate)
  
  def test6():
    d = Dictionary()
    d.insert('a', [1, 2, 3, 4])
    d.insert('b', [4, 5, 6, 7])
    print d
    
    d2 = Dictionary()
    d2.insertNestedDictionary(d)
    d2.insertNestedDictionary(d)
    print d2
    
    d3 = Dictionary()
    d3.insert('a', 'fred')
    d3.insert('b', 'sally')
    d3.insertNestedDictionary(d)
    d3.insertNestedDictionary(d)
    print d3
    
    td = TabularData.TabularData(((('a', 1, 2, 3, 4, 5, 6), ('b', 7, 8, 9, 10, 11, 12), ('c', 13, 14, 15, 16, 17, 18)), [(1, 2, 3), (4, 5, 6), (7, 8, 9)]))
    d4 = Dictionary()
    d4.insertTabularData(td)
    print d4
    
    d5 = Dictionary()
    d5.insertNestedTabularData(td)
    d5.insertNestedTabularData(td)
    print d5

  def test7():
    d2 = Dictionary()
    d2.insert('a', 10)
    d2.insert('c', None)
    
    d2.insert('a', 11)
    print "{"
    d = Dictionary()
    d.insert('c', 1)
    d.insert('c', 2)
    print "}"
    d2.insertNestedDictionary(d)
    
    print d2
    
    t2 = """
    $$loop c
      $$ $$ifNotNone c
        $$loop c
          $$cout %%c%%
        $$end
      $$ $$else
      $$  $$cout "None found"
      $$ $$endif
    $$end
    """
    t = """
    $$loop c
      $$loop c
        $$cout %%c%%
      $$end
    $$end
    """
    print interpretFromString(t, d2)
  
  test7()
  
