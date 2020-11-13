# Scotch
Scotch is a framework for generating optimized FPGA-accelerators for sketching algorithms. 

It provides three core features:
* ScotchDSL: A domain specific language + programming models to describe a variety of sketching algorithms
* Code Generators: ScotchDSL specifications are automatically translated into a VHDL architecture containing all necessary components to perform sketching.
* Auto-Tune: An automated tuning algorithms optimizes the size of the sketch summary with respect to provided constraints and resources on the FPGA

Scotch has a corresponding publication in PVLDB (soon available):

*Martin Kiefer, Ilias Poulakis, Sebastian Breß, and Volker Markl. Scotch: Generating FPGA-Accelerators for Sketching at Line Rate. PVLDB, 14(3), 2021.*

## Requirements
* A recent Linux operating system. For the code generator, OSX will do either.
* Python 3.6+ is required. We used Python 3.6.
* The following Python modules are required (used version in brackets): antlr4-python3-runtime (4.7.2), numpy (1.170), pandas (0.25.0).
* The ANTLR4 parser generator is required to generate the ScotchDSL parser (4.7.2). A setup script is provided for your convenience that downloads the appropriate jar and generates the parser. See README in the ScotchDSL folder.
* An FPGA toolchain is required. Intel FPGAs with Quartus Prime are supported. We tested with Quartus Prime Pro 19.3 and Quartus Prime 19.1. Thus all *10 and *V product lines should be supported. Furthermore, we support support Xilinx /Vivado. We tested with Version 2020.1.
* CPU baselines require GCC and Boost. We used GCC 7 and Boost 1.53.
* GPU baselines require CUDA and Boost. We used CUDA 10.2 with GCC 6 and Boost 1.53.

## Project Structure
**ScotchDSL:** Contains all code generator files and implementations of various algorithms in ScotchDSL.

**Autotune:** Contains all files regarding automated tuning.

**Baselines:** CPU and GPU baseline implementations.

**Sketches:** ScotchDSL implementations of sketching algorithms.

**IO-Controllers:** I/O controller examples.

**Util:** Miscallaneous little helpers. Contains scripts for scaling experiments.


[Our reproducibility/availability wiki page can help to get you started.](https://github.com/martinkiefer/Scotch/wiki/Reproducibility)
