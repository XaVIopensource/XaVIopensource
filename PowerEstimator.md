

# The OpenPyPE PowerEstimator Tool

OpenROAD (the RTL-to-GDS digital synthesis and layout physical implementation flow) does not have power analysis capability. 
Here's the definition of a Python class to provide this capability.

This first version is crude, generating _average estimated_ power per cell, not based on which input is causing transitions or what input and output transition times are. The code could be simplified by just counting the number of cells of each type rather than having one entry per cell. But this scheme allows the code to be improved to 
the _'non-averaged, non-estimated'_ case. It would also be a stepping stone to an IR-drop estimator.


## Overview

PyPowerEstimator:
* Reads in a .def file of a layout
* Reads in a .lib cell library file 
* Reads in a VCD file from a simulation
and outputs:
* Sum of current within a portion of the design within a time window.

This allows:
* Simple static IR drop.
* Dynamic IR drop through repeated calling with small time steps.


## Python Methods Definition

```class PyPowerEstimator():

def ReadDef(def_file="design.def", xlxhylyh=(0,1e6,0,1e6)):
  pass
  # returns dictionary of cells that fall within the rectangle defined by xlxhylyh (x and y lower and higher coordinates)
  # For each cell, indexed by instance name, it populates: x and y coordinates (not used) and cell type

def ReadLibertyLib(lib_file="cell_library.lib"):
  # returns dictionary of cells, with each item containing:
  # (i) Leakage currents when output is high and low, (ii) Energy consumed by output high and output low transitions*
  # * Averaged from mid-table values in .lib LUTs

def ReadVcd(vcd_file="sim.vcd", def_dict, start=0, finish=9e9):
  # Adds another entry to each DEF Dictionary entry: a list of time-and-value transitions extracted from the VCD file.

def CalculateLeakage(def_dict):
  # For every cell int the dictionary, it traverses the transitions list to calculate:
  # * the total duration the output is low.
  # * the total duration the output is high.

def ReportTotalLeakage(def_dict, start=0, finish=9e9):
  # Adds up the total leakage contribution from every cell.
  # Leakage energy = time_high*leakage_current_high + time_low*leakage_current_low

def ReportTotalDynamicPower(def_dict, start=0, finish=9e9):
  # Adds up the total dynamic power contribution from every cell.
  # dynamic power = number_of_rising_transitions*rising_power_dissipation + number_of_falling_transitions*falling_power_dissipation

```


## Tool Usage

* By sweeping rectangular windows across the design, storing the results in 2-d arrays, a 'heat map' plot can be produced (courtesy of matplotlib).
* By sweeping time windows across the design, storing the results in a 1-d array, a power consumption graph can be produced (again courtesy of matplotlib).

Windowing also helps to keep the dictionaries down to a reasonable size.
(The VCD file should only be collected from a relatively narrow window of a digital simulation anyway.)


## IR Drop

A somewhat crude IR drop could follow on relatively easily from this.

With:
* the 2-d array providing currents in each rectangular window across the design,
* a list of nodes in the array where supplies are connected (tuple or voltage and source resistance), and
* supply trck resistances horizontally and vertically for VDD and VSS (approximated through calculations),
it would be possible to calculate VDD and VSS voltages at each mesh node (and therefore VDD-VSS voltages) - probably using a numpy matrix inversion.

The results would be very much influenced by the choice of mesh resistance but guidance could be provided following comparisons with more accurate (commercial) tools.


## Before Diving In Though: OpenSTA

The long-term solution is likely best achieved by integrating with the OpenROAD projects STA tool, even if it is to extract load capacitances and transition times (that are calculated as part of STA) in order to get more accurate power and leakage results. See https://github.com/The-OpenROAD-Project/OpenSTA.


## Project Usage

In the context of the XaVI project, power analysis is wanted following an OpenROAD layout to provide the final overall metric to be used for optimization. 






