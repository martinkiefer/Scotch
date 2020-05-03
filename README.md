# Scotch
Scotch is a framework for generating optimized FPGA-accelerators for sketching algorithms. 

It provides three core features:
* ScotchDSL: A domain specific language + programming models to describe a variety of sketching algorithms
* Code Generators: ScotchDSL specifications are automatically translated into a VHDL architecture containing all necessary components to perform sketching.
* Auto-Tune: An automated tuning algorithms optimizes the size of the sketch summary with respect to provided constraints and resource consumption of the FPGA

A publication on Scotch is currently prepared. Stay tuned for the publication and further documentation.

## Requirements
* A recent Linux operating system. For the code generator, OSX will do either.
* Python 3.6+ is required
* The follwing Python modules are required: antlr4-python3-runtime, numpy, pandas
* The ANTLR4 parser generator is required to generate the ScotchDSL parser. A setup script is provided for your convenience, see README in the ScotchDSL folder.
* An FPGA toolchain is required. For now, only IntelFPGAs / Quartus Prime is supported, Xilinx support is planned. We tested with Quartus Prime Pro 19.3 and Quartus Prime 19.1. Thus all *10 and *V product lines should be supported.

## Project Structure
**ScotchDSL:** Contains all code generator files and implementations of various algorithms in ScotchDSL.

**Autotune:** Contains all files regarding automated tuning.