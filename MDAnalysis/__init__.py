# $Id$
# MDAnalysis http://mdanalysis.googlecode.com
# Copyright (c) 2006-2010 Naveen Michaud-Agrawal, Elizabeth J. Denning, Oliver Beckstein
# Released under the GNU Public Licence, v2

"""
:mod:`MDAnalysis` --- analysis of molecular simulations in python
=================================================================

MDAnalysis is a python framework to analyze molecular dynamics
trajectories generated by CHARMM, NAMD, Gromacs, or LAMMPS.

It allows one to read molecular dynamics trajectories and access the
atomic coordinates through numpy arrays. This provides an extremely
flexible and relatively fast framework for complex analysis tasks. In
addition, CHARMM-style atom selection commands are
implemented. Trajectories can also be manipulated (for instance, fit
to a reference structure) and written out. Time-critical code is
written in C for speed.

Code and documentation are hosted at http://code.google.com/p/mdanalysis/

Help is also available through the mailinglist at
http://groups.google.com/group/mdnalysis-discussion

Please report bugs and feature requests through the issue tracker at
http://code.google.com/p/mdanalysis/issues/ 

Getting started
---------------

Import the package::
 
  >>> import MDAnalysis

(note that not everything in MDAnalysis is imported right away; for
additional functionality you might have to import sub-modules
separately, e.g. for RMS fitting ``import MDAnalysis.core.rms_fitting``.)

Build a "universe" from a topology (PSF, PDB) and a trajectory (DCD, XTC/TRR);
here we are assuming that PSF, DCD, etc contain file names. If you don't have
trajectories at hand you can play with the ones that come with MDAnalysis for
testing (see below under `Examples`_)::

  >>> u = MDAnalysis.Universe(PSF, DCD)

Select the C-alpha atoms and store them as a group of atoms::

  >>> ca = u.selectAtoms('name CA')
  >>> len(ca)
  214  

Calculate the centre of mass of the CA and of all atoms::

  >>> ca.centerOfMass()
  array([ 0.06873595, -0.04605918, -0.24643682])
  >>> u.atoms.centerOfMass()
  array([-0.01094035,  0.05727601, -0.12885778])

Calculate the CA end-to-end distance (in angstroem)::
  >>> from numpy import sqrt, dot
  >>> coord = ca.coordinates()
  >>> v = coord[-1] - coord[0]   # last Ca minus first one
  >>> sqrt(dot(v, v,))
  10.938133

Define a function eedist():
  >>> def eedist(atoms):
  ...     coord = atoms.coordinates()
  ...     v = coord[-1] - coord[0] 
  ...     return sqrt(dot(v, v,))
  ... 
  >>> eedist(ca)
  10.938133

and analyze all timesteps *ts* of the trajectory::
  >>> for ts in u.trajectory:
  ...      print eedist(ca)
  10.9381
  10.8459
  10.4141
   9.72062 
  ....

.. SeeAlso:: :class:`MDAnalysis.core.AtomGroup.Universe` for details


Examples
--------

MDAnalysis comes with a number of real trajectories for testing. You
can also use them to explore the functionality and ensure that
everything is working properly::

  from MDAnalysis import *
  from MDAnalysis.tests.datafiles import PSF,DCD, PDB,XTC
  u_dims_adk = Universe(PSF,DCD)
  u_eq_adk = Universe(PDB, XTC)

The PSF and DCD file are a closed-form-to-open-form transition of
Adenylate Kinase (from [Beckstein2009]_) and the PDB+XTC file are ten
frames from a Gromacs simulation of AdK solvated in TIP4P water with
the OPLS/AA force field.

[Beckstein2009] O. Beckstein, E.J. Denning, J.R. Perilla and
                T.B. Woolf, Zipping and Unzipping of Adenylate Kinase: Atomistic
                Insights into the Ensemble of Open <--> Closed Transitions. J Mol Biol
                394 (2009), 160--176, doi:10.1016/j.jmb.2009.09.009
"""

# Only import often used modules and objects; anything else should be imported
# when needed. In particular, we avoid 
#   import core.rms_fitting
# because it tends to be a show stopper if no LAPACK found; given that many
# people don't need it we rather wait for them to import it and then throw
# a error (TODO: catch that ImportError when no liblapack.so found so that we 
# can issue sensible advice)
__all__ = ['Timeseries', 'Universe', 'asUniverse', 'Writer', 'collection']

import logging
# see the advice on logging and libraries in
# http://docs.python.org/library/logging.html?#configuring-logging-for-a-library
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
h = NullHandler()
logging.getLogger("MDAnalysis").addHandler(h)
del h

def start_logging(logfile="MDAnalysis.log"):
    """Start logging of messages to file and console."""
    import core.log
    core.log.create("MDAnalysis", logfile=logfile)
    logging.getLogger("MDAnalysis").info("MDAnalysis STARTED logging to %r", logfile)

def stop_logging():
    """Stop logging to logfile."""
    import core.log
    logger = logging.getLogger("MDAnalysis")
    logger.info("MDAnalysis STOPPED logging")
    core.log.clear_handlers(logger)  # this _should_ do the job...

# custom exceptions and warnings
class SelectionError(Exception):
    """Raised when a atom selection failed."""

class NoDataError(ValueError):
    """Raised when empty input is not allowed or required data are missing."""

class FormatError(EnvironmentError):
    """Raised when there appears to be a problem with format of input files."""

class SelectionWarning(Warning):
    """Warning indicating a possible problem with a selection."""

class MissingDataWarning(Warning):
    """Warning indicating is that required data are missing."""

# Bring some often used objects into the current namespace
from core import Timeseries
from core.AtomGroup import Universe, asUniverse
from coordinates.core import writer as Writer

collection = Timeseries.TimeseriesCollection()

