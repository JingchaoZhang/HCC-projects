Installation
=================

Though not required, installation an operation of XALT is easier with pre-requisite software: lua and lmod.

Lmod provides the spider utility which creates the map, but can be added later.  A script is available to update table entreis with ReverseMap.

Install XALT
^^^^^^^^^^^^
XALT may be downloaded from either sourceforge or github:

  http://sourceforge.net/projects/xalt/

  http://github.com/Fahey-McLay/xalt/

.. _Lmod:

Lmod Installation
^^^^^^^^^^^^^^^^^^

Get Lmod-7.1 or greater from from sourceforge::

	http://sourceforge.net/projects/lmod/files/



Or get Lmod-7.1 or greater from::

  $ git clone TACC/Lmod/Lmod.git

::

	download Lmod-<ver>.tar.gz from lmod.sourceforge.net



Installation instructions and documentation for Lmod:
  http://lmod.readthedocs.org/

If machines had different architectures, then each machine needs a build of Lmod. 

Installation Steps
^^^^^^^^^^^^^^^^^^

In the documentation, we install everything to $XALT_DIR.

First, untar the XALT file, change the directory to XALT, configure, then install::

	$ cd xalt	
	$ ./configure --prefix=$XALT_DIR --with-etcDir=$XALT_ETC_DIR
	$ make
	$ make install

Remove Job Launchers
---------------------

Next, remove job launchers that are not supported on your system. Launchers currently on XALT include: aprun, ibrun, mpirun, mpiexec, srun.

For removing launchers on a Cray, which only supports 'aprun'::

	$ cd $XALT_DIR/bin
	$ rm ibrun* mpirun mpiexec srun

For job launchers not part of XALT, you will ned to develop your own launcher which involves creating site/xalt_find_exec_xxxx.py. If you complete this step, please submit your launcher to the XALT team.

	
Manual Steps
------------

To return the names/names of the hosts you want stored in the database you must modify the site/xalt_syshost_default.py file

We suggest one name for an entire machine, but you could go with a name for each compute node/partition. 

Depending on your installation and batch schedulers, you may need to edit site/xalt_site_pkg.py.

XALT currently provides support for LSF, SGE, SLURM, and PBS queuing systems.
 

ReverseMap & Libmap
--------------------

Build a file for ReverseMap and libmap. 

ReverseMap associates libraries and object files with the modulefile that specifies them. 

Libmap lists the library files (.a and .so) whose call to their function will be tracked by XALT. 

The reverse map needs to be created or updated per machine every time a new modulefile or package is installed. So, it either has to become part of the software installation process, or run as a cron job on a routine basis.

ReverseMap and Libmap are stored in the same file.

On a cluster::

    $ $LMOD_DIR/lmod/lmod/libexec/spider -o jsonReverseMapT $MODULEPATH > ${XALT_ETC_DIR}/reverseMapD/jsonReverseMapT.json

It is important to use the same filename and directory "reverseMapD" as they
are used by conventions in XALT.

On a Cray (XC, XE, XK), the process is a bit more involved, so a script has been
provided under contrib/ directory in the XALT source distribution to make it
easier. Use this script and run::

	$ xalt/contrib/build_reverseMapT_cray/cray_build_rmapT.sh $XALT_ETC_DIR

Once the ReverseMap file is built, add libmap to is using as::

	$ $XALT_DIR/sbin/xalt_rmap_lmap.py 

Database Creation
------------------- 

Create the file to hold database credentials::

	$ cd $XALT_ETC_DIR
	$ python $XALT_DIR/sbin/conf_create.py #-- create xalt_db.conf

In this step, make sure that the credential you created have the necessary privileges to create tables, etc. If you want the database credential to be more restrictive,recreate the file to hold database credentials with the desired privilege account. 


Create the database and tables for XALT (need to be run from $XALT_ETC_DIR)::

	$ cd $XALT_ETC_DIR
	$ python $XALT_DIR/sbin/createDB.py
	

Next Steps - Database Set Up
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  :doc:`040_Database`
