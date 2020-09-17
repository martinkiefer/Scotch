# Scotch
Scotch is a framework for generating optimized FPGA-accelerators for sketching algorithms. 

It provides three core features:
* ScotchDSL: A domain specific language + programming models to describe a variety of sketching algorithms
* Code Generators: ScotchDSL specifications are automatically translated into a VHDL architecture containing all necessary components to perform sketching.
* Auto-Tune: An automated tuning algorithms optimizes the size of the sketch summary with respect to provided constraints and resources on the FPGA

A publication on Scotch is currently prepared. Stay tuned for the publication and further documentation.

## Requirements
* A recent Linux operating system. For the code generator, OSX will do either.
* Python 3.6+ is required
* The following Python modules are required: antlr4-python3-runtime, numpy, pandas
* The ANTLR4 parser generator is required to generate the ScotchDSL parser. A setup script is provided for your convenience, see README in the ScotchDSL folder.
* An FPGA toolchain is required. Intel FPGAs / Quartus Prime is supported. We tested with Quartus Prime Pro 19.3 and Quartus Prime 19.1. Thus all *10 and *V product lines should be supported. Furthermore, we support support Xilinx /Vivado. We tested with Version 2020.1.
* CPU baselines require GCC. We used GCC 6 and GCC 7.
* GPU baselines require CUDA. We used CUDA 10.2 with GCC 6.

## Project Structure
**ScotchDSL:** Contains all code generator files and implementations of various algorithms in ScotchDSL.

**Autotune:** Contains all files regarding automated tuning.

**Baselines:** CPU and GPU baseline implementations.

**Sketches:** ScotchDSL implementations of sketching algorithms.

**IO-Controllers:** I/O controller examples.
