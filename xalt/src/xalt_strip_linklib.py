#-----------------------------------------------------------------------
# XALT: A tool that tracks users jobs and environments on a cluster.
# Copyright (C) 2013-2015 University of Texas at Austin
# Copyright (C) 2013-2015 University of Tennessee
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
#
# Git Version: @git@

from __future__                import print_function
import os, sys, json
from   collections import defaultdict

dirNm, execName = os.path.split(os.path.realpath(sys.argv[0]))
sys.path.insert(1,os.path.realpath(os.path.join(dirNm, "../libexec")))
sys.path.insert(1,os.path.realpath(os.path.join(dirNm, "../site")))

from   xalt_global import *
from   Rmap_XALT   import Rmap

RMapFn = os.path.join(XALT_ETC_DIR,"reverseMapD")
libmap = Rmap(RMapFn).libMap()

refLibs = set()
for lib in libmap:
  name = lib.replace('.a','').replace('.so','')
  refLibs.add(name)

# Remove libraries that are in reference lib
linkline = sys.argv[1:]
aLibs    = []
for iLib in linkline:
  testLib = os.path.basename(iLib.replace("-l", "lib") \
                             .replace('.a','').replace('.so','').strip())
  if testLib in refLibs:
    continue
    
  aLibs.append(iLib)
    
print(" ".join(aLibs))
