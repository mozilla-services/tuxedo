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


import getopt
import os
import sys
import cStringIO

class ConfigurationManagerConfigFileMissing (IOError):
  pass
  
class ConfigurationManagerConfigFileOptionNameMissing (Exception):
  pass
  
class ConfigurationManagerNotAnOption (Exception):
  pass


#========================================
# C o n f i g u r a t i o n M a n a g e r
#========================================
class ConfigurationManager (dict):
  """This class encapsulates the process of getting command line arguments, configuration files and environment variables into a program.
  It wraps the Python getopt module and provides a more comprehensive interface.
  """
  def __init__ (self, configurationOptionsList=[], optionNameForConfigFile="config"):
    """Initialize a new instance.  
    
    Parameters:
      configurationOptionsList: a list of tuples that represent the options available to the user.  The tuples take this form:
        (singleCharacterOptionForm, longOptionForm, takesParametersBoolean, defaultValue, humanReadableOptionExplanation [, optionalListOfOptionParameterPairs ])
        The optionalListOfOptionParameterPairs to create short cuts for sets of options.  The form is a list of two element tuples specifying some other option
        and its value.  Examples can be seen below.
      optionNameForConfigFile: the name of the option that stores the pathname of the configuration file - if this is set to None then we assume there
        is no configuration file and one will not be tried
    """
    self.originalConfigurationOptionsList = configurationOptionsList
    
    self.singleLetterCommandLineOptionsForGetopt = ""
    self.expandedCommandLineOptionsForGetopt = []
    
    self.allowableOptionDictionary = {}
    for x in configurationOptionsList:
      self.allowableOptionDictionary[x[0]] = x
      self.allowableOptionDictionary[x[1]] = x
      self.addOptionsForGetopt(x)
      
    # setup all defaults for options:
    for x in configurationOptionsList:
      if x[2] and x[3] is not None:
        self[x[1]] = x[3]

    # get options from the environment - these override defaults
    for x in os.environ:
      if self.allowableOptionDictionary.has_key(x):
        self[self.allowableOptionDictionary[x][1]] = os.environ.get(x)
        self.insertCombinedOption(x, self)
        
    # get the options from the command line - these will eventually override all other methods of setting options
    try:
      options, self.arguments = getopt.getopt(sys.argv[1:], self.singleLetterCommandLineOptionsForGetopt, self.expandedCommandLineOptionsForGetopt)
    except getopt.GetoptError, e:
      raise ConfigurationManagerNotAnOption, e
    commandLineEnvironment = {} # save these options for merging later
    for x in options:
      if len(x[0]) == 2: #single letter option
        longFormOfSingleLetterOption = self.allowableOptionDictionary[x[0][1]][1] 
        if self.allowableOptionDictionary[longFormOfSingleLetterOption][2]:
          commandLineEnvironment[longFormOfSingleLetterOption] = x[1]
        else:
          commandLineEnvironment[longFormOfSingleLetterOption] = None
        self.insertCombinedOption(longFormOfSingleLetterOption, commandLineEnvironment)
      else:
        longFormOption = x[0][2:]
        if self.allowableOptionDictionary[longFormOption][2]:
          commandLineEnvironment[longFormOption] = x[1]
        else:
          commandLineEnvironment[longFormOption] = None
        self.insertCombinedOption(longFormOption, commandLineEnvironment)
        
    # get any options from the config file
    # any options already set in the environment are overridden
    if optionNameForConfigFile is not None:
      try:
        try:
          configFile = open(commandLineEnvironment[optionNameForConfigFile], 'r')
        except KeyError:
          configFile = open(self[optionNameForConfigFile], 'r')
        except IOError, e:
          raise ConfigurationManagerConfigFileMissing()
          raise e
        for x in configFile:
          x = x.lstrip().rstrip()
          if not x or x[0] == '#' : continue
          keyValuePair = x.split('=', 1)
          if self.allowableOptionDictionary.has_key(keyValuePair[0]):
            longFormOption = self.allowableOptionDictionary[keyValuePair[0]][1]
            self.insertCombinedOption(longFormOption, self)
            try:
              self[longFormOption] = keyValuePair[1]
            except IndexError:
              self[longFormOption] = None
          else:
            raise ConfigurationManagerNotAnOption, "option '%s' in the config file is not recognized" % keyValuePair[0]
      except KeyError:
        raise ConfigurationManagerConfigFileOptionNameMissing()
      except IOError:
        raise ConfigurationManagerConfigFileMissing()
    
    # merge command line options with the workingEnvironment
    # any options already specified in the environment or
    # configuration file are overridden.
    for x in commandLineEnvironment:
      self[x] = commandLineEnvironment[x]

    # make sure that non-string values in the workingEnvironment
    # have the right type.  Assume the default value has the right
    # type and cast the existing value to that type
    for x in self.allowableOptionDictionary.values():
      valueType = type(x[3])
      if valueType != str and valueType != type(None):
        try: self[x[1]] = valueType(self[x[1]])
        except KeyError: pass

  #--------------------------------------
  # a d d O p t i o n s F o r G e t o p t
  #--------------------------------------
  def addOptionsForGetopt (self, optionTuple):
    """Internal Use - during setup, this function sets up internal structures with a new optionTuple.
    
    Parameters:
      optionTuple: a tuple of the form - (singleCharacterOptionForm, longOptionForm, takesParametersBoolean, ...)
    """
    if optionTuple[2]: #does this option have parameters?
      self.singleLetterCommandLineOptionsForGetopt = "%s%s:" % (self.singleLetterCommandLineOptionsForGetopt, optionTuple[0])
      self.expandedCommandLineOptionsForGetopt.append("%s=" % optionTuple[1])
    else:
      self.singleLetterCommandLineOptionsForGetopt = "%s%s" % (self.singleLetterCommandLineOptionsForGetopt, optionTuple[0])
      self.expandedCommandLineOptionsForGetopt.append(optionTuple[1])

  #----------------------------------------
  # i n s e r t C o m b i n e d O p t i o n
  #----------------------------------------
  def insertCombinedOption (self, anOption, theDictionaryToInsertInto):
    """
    """
    try:
      for x in self.allowableOptionDictionary[anOption][5]:
        theDictionaryToInsertInto[x[0]] = x[1]
    except KeyError: pass
    except IndexError: pass
    
  #----------------------------------------
  # o u t p u t C o m m a n d S u m m a r y
  #----------------------------------------
  def outputCommandSummary (self, outputStream=sys.stdout, sortOption=0, outputTemplateForOptionsWithParameters="\t-%s, --%s\n\t\t%s (default: %s)", outputTemplateForOptionsWithoutParameters="\t-%s, --%s\n\t\t%s"):
    """outputs the list of acceptable commands.  This is useful as the output of the 'help' option or usage.
    
    Parameters:
      outputStream: where to send the output
      sortOption: 0 - sort by the single character option
                  1 - sort by the long option
      outputTemplateForOptionsWithParameters: a string template for outputing options that have parameters
      outputTemplateForOptionsWithoutParameters: a string template for outputing options that have no parameters
    """
    optionsList = [ x for x in self.originalConfigurationOptionsList ]
    optionsList.sort(lambda a, b: (a[sortOption] > b[sortOption]) or -(a[sortOption] < b[sortOption]))
    for x in optionsList:
      if x[2]:
        print >>outputStream, outputTemplateForOptionsWithParameters % (x[0], x[1], x[4], x[3])
      else:
        print >>outputStream, outputTemplateForOptionsWithoutParameters % (x[0], x[1], x[4])
        
  #------------
  # o u t p u t
  #------------
  def output (self, outputStream=sys.stdout, outputTemplateForOptionsWithParameters="\t%s=%s", outputTemplateForOptionsWithoutParameters="\t%s", blockPassword=True):
    """this routine will right the current values of all options to an output stream.
    
    Parameters:
      outputStream: where to write the output
      outputTemplateForOptionsWithParameters: a string template for outputing options that have parameters
      outputTemplateForOptionsWithoutParameters: a string template for outputing options that have no parameters
      blockPassword: a boolean controlling the output of options that have the string 'password' in their name
        True - the value will be printed as **********
        False - the value will print normally
    """
    environmentList = [x for x in self.iteritems() ]
    environmentList.sort(lambda x, y: (x[0] > y[0]) or -(x[0] < y[0]))
    for x in environmentList:
      if blockPassword and x[1] is not None and "password" in x[0].lower():
        print >>outputStream, outputTemplateForOptionsWithParameters % (x[0], "*" * 10)
        continue
      if x[1] is not None:
        print >>outputStream, outputTemplateForOptionsWithParameters % x
      else:
        print >>outputStream, outputTemplateForOptionsWithoutParameters % x[0]
        
  #--------------
  # _ _ s t r _ _
  #--------------
  def __str__ (self):
    stringio = cStringIO.StringIO()
    self.output(stringio)
    s = stringio.getvalue()
    stringio.close()
    return s
      
if __name__ == "__main__":
        
  commandLineOptions = [ ('?', 'help', False, None, 'print this message'), 
                         ('c', 'config', True, './config', "the config file"),
                         ('a', 'alpha', True, 600, "the alpha option"),
                         ('b', 'beta', True, 'hello', 'the beta option'),
                         ('g', 'gamma', False, None, "the gamma option"),
                         ('p', 'secretpassword', True, '', 'the password'), 
                         ('$', 'dollar', False, None, "combo of 'alpha=22, beta=10'", [ ("alpha", 22), ("beta", 10) ] ),
                         ('#', 'hash', False, None, "combo of 'alpha=2, beta=100, gamma'", [ ("alpha", 1), ("beta", 10), ("gamma", None) ] ),
                       ]

  cm = ConfigurationManager(commandLineOptions)
  if cm.has_key("help"): 
    cm.outputCommandSummary()
    sys.exit()
  
  print cm
  c = `cm`
  print c
  #cm.output()
  
  #print cm['alpha'] + 100  #cm['alpha'] should be int
  
  
  
 
  
