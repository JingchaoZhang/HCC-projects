#-----------------------------------------------------------------------
# XALT: A tool that tracks users jobs and environments on a cluster.
# Copyright (C) 2013-2014 University of Texas at Austin
# Copyright (C) 2013-2014 University of Tennessee
# 
# This library is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation; either version 2.1 of 
# the License, or (at your option) any later version. 
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser  General Public License for more details. 
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free
# Software Foundation, Inc., 59 Temple Place, Suite 330,
# Boston, MA 02111-1307 USA
#-----------------------------------------------------------------------

from __future__ import print_function
from time       import sleep
import os, sys, re, base64, json
dirNm, execName = os.path.split(os.path.realpath(sys.argv[0]))
sys.path.append(os.path.realpath(os.path.join(dirNm, "../libexec")))
sys.path.append(os.path.realpath(os.path.join(dirNm, "../site")))

import MySQLdb, getpass, time
import warnings
from   xalt_util     import *
from   xalt_global   import *
from   xalt_site_pkg import translate, keep_env_var
try:
  import configparser
except:
  import ConfigParser as configparser

warnings.filterwarnings("ignore", "Unknown table.*")

# In 'directdb' transmission, print goes to syslog (for exception, etc)
if (XALT_TRANSMISSION_STYLE == 'directdb' and not XALT_TRACING):
  logger = config_logger()
  print = logger.exception

import inspect

def __LINE__():
    try:
        raise Exception
    except:
        return sys.exc_info()[2].tb_frame.f_back.f_lineno

def __FILE__():
    fnA = os.path.split(inspect.currentframe().f_code.co_filename)
    return fnA[1]

#print ("file: '%s', line: %d" % (__FILE__(), __LINE__()), file=sys.stderr)

def convertToTinyInt(s):
  """
  Convert to string to int.  Protect against bad input.
  @param s: Input string
  @return: integer value.  If bad return 0.
  """
  try:
    value = int(s)
    if  (value > 127):
      value = 127
    elif(value < -128):
      value = -128
  except ValueError as e:
    value = 0
  return value

class XALTdb(object):
  """
  This XALTdb class opens the XALT database and is responsible for
  all the database interactions.
  """
  def __init__(self, confFn):
    """ Initialize the class and save the db config file. """
    self.__host   = None
    self.__user   = None
    self.__passwd = None
    self.__db     = None
    self.__conn   = None
    self.__confFn = confFn

  def __readFromUser(self):
    """ Ask user for database access info. (private) """

    self.__host   = raw_input("Database host:")
    self.__user   = raw_input("Database user:")
    self.__passwd = getpass.getpass("Database pass:")
    self.__db     = raw_input("Database name:")

  def __readConfig(self):
    """ Read database access info from config file. (private)"""
    confFn = self.__confFn
    try:
      config=configparser.ConfigParser()
      config.read(confFn)
      self.__host    = config.get("MYSQL","HOST")
      self.__user    = config.get("MYSQL","USER")
      self.__passwd  = base64.b64decode(config.get("MYSQL","PASSWD"))
      self.__db      = config.get("MYSQL","DB")
    except configparser.NoOptionError as err:
      sys.stderr.write("\nCannot parse the config file\n")
      sys.stderr.write("Switch to user input mode...\n\n")
      self.__readFromUser()

  def connect(self, databaseName = None):
    """
    Public interface to connect to DB.
    @param db:  If this exists it will be used.
    
    """
    if(os.path.exists(self.__confFn)):
      self.__readConfig()
    else:
      self.__readFromUser()

    try:
      self.__conn = MySQLdb.connect \
                      (self.__host,self.__user,self.__passwd, use_unicode=True, \
                       charset="utf8", connect_timeout=120)
      if (databaseName):
        cursor = self.__conn.cursor()
        
        # If MySQL version < 4.1, comment out the line below
        cursor.execute("SET SQL_MODE=\"NO_AUTO_VALUE_ON_ZERO\"")
        cursor.execute("USE "+xalt.db())

        self.__conn.set_character_set('utf8')
        cursor.execute("SET NAMES utf8;") #or utf8 or any other charset you want to handle
        cursor.execute("SET CHARACTER SET utf8;") #same as above
        cursor.execute("SET character_set_connection=utf8;") #same as above

    except MySQLdb.Error as e:
      print ("XALTdb: Error: %s %s" % (e.args[0], e.args[1]))
      raise
    return self.__conn

  def db(self):
    """ Return name of db"""
    return self.__db

  def link_to_db(self, reverseMapT, linkT):
    """
    Stores the link table data into the XALT db
    @param reverseMapT: The reverse map table that maps directories to modules
    @param linkT:       The table that contains the link data.
    """
    query = ""

    try:
      conn   = self.connect()
      cursor = conn.cursor()
      query  = "USE "+self.db()
      conn.query(query)
      query  = "START TRANSACTION"
      conn.query(query)
      
      query  = "SELECT uuid FROM xalt_link WHERE uuid=%s"
      cursor.execute(query, [linkT['uuid']])
      if (cursor.rowcount > 0):
        return

      build_epoch = float(linkT['build_epoch'])
      dateTimeStr = time.strftime("%Y-%m-%d %H:%M:%S",
                                  time.localtime(float(linkT['build_epoch'])))

      #paranoid conversion:  Protect DB from bad input:
      exit_code   = convertToTinyInt(linkT['exit_code'])
      exec_path   = linkT['exec_path']
      link_prg    = linkT['link_program'][:64]
      link_path   = linkT.get('link_path',"UNKNOWN")
      link_mname  = obj2module(link_path,reverseMapT)
      link_line   = json.dumps(linkT.get('link_line',"[]"))
      build_user  = linkT['build_user']
      build_shost = linkT['build_syshost']

      # It is unique: lets store this link record
      query = "INSERT into xalt_link VALUES (NULL,%s,%s,%s, %s,%s,%s, COMPRESS(%s),%s,%s, %s,%s,%s)"
      cursor.execute(query, (linkT['uuid'], linkT['hash_id'],     dateTimeStr, 
                             link_prg,      link_path,            link_mname,
                             link_line,     build_user,           build_shost,
                             build_epoch,   exit_code,            exec_path))

      link_id = cursor.lastrowid

      XALT_Stack.push("load_xalt_objects():"+linkT['exec_path'])
      self.load_objects(conn, linkT['linkA'], reverseMapT, linkT['build_syshost'],
                        "join_link_object", link_id)
      v = XALT_Stack.pop()  # unload function()
      carp("load_xalt_objects()",v)
      
      # store tracked functions
      if ('function' in linkT):
        for func_name in linkT['function']:
          query = "SELECT func_id FROM xalt_function WHERE function_name=%s"
          cursor.execute(query, [func_name[:255]])
          if (cursor.rowcount > 0):
            func_id = int(cursor.fetchone()[0])
          else:
            query = "INSERT INTO xalt_function VALUES (NULL, %s)"
            cursor.execute(query, [func_name[:255]])
            func_id = cursor.lastrowid
        
          query = "INSERT INTO join_link_function VALUES(NULL, %s, %s) \
                       ON DUPLICATE KEY UPDATE func_id = %s, link_id = %s"
          cursor.execute(query, (func_id, link_id, func_id, link_id))
        
      query = "COMMIT"
      conn.query(query)
      
      conn.close()

    except Exception as e:
      print(XALT_Stack.contents())
      print(query)
      print ("link_to_db(): Error %s" % e)
      sys.exit (1)

  def load_objects(self, conn, objA, reverseMapT, syshost, tableName, index):
    """
    Stores the objects that make an executable into the XALT DB.
    @param conn:         The db connection object
    @param objA:         The array of objects that are stored.
    @param reverseMapT:  The map between directories and modules
    @param syshost:      The system host name (stampede, darter), not login1.stampede.tacc.utexas.edu
    @param tableName:    Name of the object table.
    @param index:        The db index for the join table.
    """

    cursor = conn.cursor()
    try:
      for entryA in objA:
        object_path  = entryA[0]
        hash_id      = entryA[1]
        if (hash_id == "unknown"):
          continue

        query = "SELECT obj_id, object_path FROM xalt_object WHERE hash_id=%s AND object_path=%s AND syshost=%s"
          
        cursor.execute(query,(hash_id, object_path, syshost))

        if (cursor.rowcount > 0):
          row    = cursor.fetchone()
          obj_id = int(row[0])
        else:
          moduleName = obj2module(object_path, reverseMapT)
          obj_kind   = obj_type(object_path)

          query      = "INSERT into xalt_object VALUES (NULL,%s,%s,%s,%s,NOW(),%s)"
          
          if (moduleName and len(moduleName) > 64):
            moduleName = moduleName[:63]
                      
          cursor.execute(query,(object_path, syshost, hash_id, moduleName, obj_kind))
          obj_id   = conn.insert_id()
          #print("obj_id: ",obj_id, ", obj_kind: ", obj_kind,", path: ", object_path, "moduleName: ", moduleName)

        # Now link libraries to xalt_link record:
        query = "INSERT into " + tableName + " VALUES (NULL,%s,%s) "  
        cursor.execute(query,(obj_id, index))
  
    except Exception as e:
      print(XALT_Stack.contents())
      print(query)
      print ("load_xalt_objects(): Error %d: %s" % (e.args[0], e.args[1]))
      sys.exit (1)

  def run_to_db(self, reverseMapT, runT):
    """
    Store the "run" data into the database.
    @param: reverseMapT: The map between directories and modules
    @param: runT:        The run data stored in a table
    """
    
    nameA = [ 'num_cores', 'num_nodes', 'account', 'job_id', 'queue' , 'submit_host']
    query = ""
    try:
      conn   = self.connect()
      cursor = conn.cursor()
      query  = "USE "+self.db()
      conn.query(query)
      query  = "START TRANSACTION"
      conn.query(query)

      
      translate(nameA, runT['envT'], runT['userT']);
      XALT_Stack.push("SUBMIT_HOST: "+ runT['userT']['submit_host'])

      runTime     = "%.2f" % float(runT['userT']['run_time'])
      endTime     = "%.2f" % float(runT['userT']['end_time'])
      dateTimeStr = time.strftime("%Y-%m-%d %H:%M:%S",
                                  time.localtime(float(runT['userT']['start_time'])))
      uuid        = runT['xaltLinkT'].get('Build.UUID',None)
      #print( "Looking for run_uuid: ",runT['userT']['run_uuid'])

      query = "SELECT run_id FROM xalt_run WHERE run_uuid=%s"
      cursor.execute(query,[runT['userT']['run_uuid']])

      if (cursor.rowcount > 0):
        #print("found")
        row    = cursor.fetchone()
        run_id = int(row[0])
        if (runT['userT']['end_time'] > 0):
          query  = "UPDATE xalt_run SET run_time=%s, end_time=%s WHERE run_id=%s" 
          cursor.execute(query,(runTime, endTime, run_id))
          query = "COMMIT"
          conn.query(query)
        v = XALT_Stack.pop()
        carp("SUBMIT_HOST",v)

        return
      else:
        #print("not found")
        moduleName    = obj2module(runT['userT']['exec_path'], reverseMapT)
        exit_status   = convertToTinyInt(runT['userT'].get('exit_status',0))
        num_threads   = convertToTinyInt(runT['userT'].get('num_threads',0))
        usr_cmdline   = json.dumps(runT['cmdlineA'])

        job_num_cores = int(runT['userT'].get('job_num_cores',0))
        startTime     = "%.f" % float(runT['userT']['start_time'])
        query  = "INSERT INTO xalt_run VALUES (NULL, %s,%s,%s, %s,%s,%s, %s,%s,%s, %s,%s,%s, %s,%s,%s, %s,%s,%s, %s,%s,%s, COMPRESS(%s))"
        cursor.execute(query, (runT['userT']['job_id'],      runT['userT']['run_uuid'],    dateTimeStr,
                               runT['userT']['syshost'],     uuid,                         runT['hash_id'],
                               runT['userT']['account'][:20],runT['userT']['exec_type'],   startTime,
                               endTime,                      runTime,                      runT['userT']['num_cores'],
                               job_num_cores,                runT['userT']['num_nodes'],   num_threads,
                               runT['userT']['queue'],       exit_status,                  runT['userT']['user'],
                               runT['userT']['exec_path'],   moduleName,                   runT['userT']['cwd'],
                               usr_cmdline))
        run_id   = cursor.lastrowid


      self.load_objects(conn, runT['libA'], reverseMapT, runT['userT']['syshost'],
                        "join_run_object", run_id)

      envT    = runT['envT']
      jsonStr = json.dumps(envT)
      query   = "INSERT INTO xalt_total_env VALUES(NULL, %s, COMPRESS(%s))"
      cursor.execute(query, [run_id, jsonStr])
      
      # loop over env. vars.
      for key in envT:
        if (not keep_env_var(key)):
          continue
        value = envT[key]
        query = "SELECT env_id FROM xalt_env_name WHERE env_name=%s"
        cursor.execute(query,[key])
        if (cursor.rowcount > 0):
          row    = cursor.fetchone()
          env_id = int(row[0])
          found  = True
        else:
          query  = "INSERT INTO xalt_env_name VALUES(NULL, %s)"
          cursor.execute(query,[key[:64]])
          env_id = cursor.lastrowid
          found  = False
        
        query = "INSERT INTO join_run_env VALUES (NULL, %s, %s, %s)"
        cursor.execute(query,(env_id, run_id, value))
          
      v = XALT_Stack.pop()
      carp("SUBMIT_HOST",v)
      query = "COMMIT"
      conn.query(query)
      conn.close()

    except Exception as e:
      print(XALT_Stack.contents())
      print(query.encode("ascii","ignore"))
      print ("run_to_db(): %s" % e)
      sys.exit (1)

