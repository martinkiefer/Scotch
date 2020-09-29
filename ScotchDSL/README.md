# Setup
Move to the Grammar directory and execute the following commands:
```bash
bash generateParser.sh
```
It generates the parser files and copies them to the translation directory where they are needed.

# RTL Generators
There are differente code generators available in ./Translation. They differ in the sketches they support and programming model assumed. All of them can also be used without invoking Autotune. All of them require a sketch descriptor as an input argument that contains parameters and points to the ScotchDSL functions (see the ../Sketches folder for examples). The code generation target is VHDL.

## Matrix Sketches / Row Sketches
For matrix sketches, there is only ReplicatedMatrixSketchGenerator.py. It assumes the Select-Update model and uses the following arguments:

```
python3 ReplicatedMatrixSketchGenerator.py path_to_descriptor ram_depth rams_per_row nrows dispatch_branching_factor collect_branching_factor n_replicas output_dir
```

**path_to_descriptor:** The path to the sketch descriptor.\
**ram_depth:** Number of values per RAM segment. You probably want to choose this value depending as the depth fof the used BRAMs for the value size determined in the descriptor.\
**rams_per_row:** The number of pipelined RAM segments used for the memory of a row.\
**nrows:** Number of rows in the sketch.\
**dispatch/branching_factor:** Branching factor for the tree-shaped dispatch and collect unit. If you have no other reason to do otherwise, choose 4.\
**n_replicas:** Number of parallel sketch replicas / degree of data parallelism.\
**output_dir:** Output directory containing the generated HDL files. Optional. Default is ./output.

## Column Sketches
### Map-Apply
```
python3 DataParallelColumnSketchGenerator.py path_to_descriptor nrows dispatch_branching_factor collect_branching_factor output_dir
```

**path_to_descriptor:** The path to the sketch descriptor.\
**nrows:** Number of rows in the sketch.\
**dispatch/branching_factor:** Branching factor for the tree-shaped dispatch and collect unit. If you have no other reason to do otherwise, choose 4.\
**output_dir:** Output directory containing the generated HDL files. Optional. Default is ./output.

### Select-Update
```
python3 ReplicatedColumnSketchGenerator.py path_to_descriptor nrows dispatch_branching_factor collect_branching_factor n_replicas output_dir
```

**path_to_descriptor:** The path to the sketch descriptor.\
**nrows:** Number of rows in the sketch.\
**dispatch/branching_factor:** Branching factor for the tree-shaped dispatch and collect unit. If you have no other reason to do otherwise, choose 4.\
**n_replicas:** Number of parallel sketch replicas / degree of data parallelism.\
**output_dir:** Output directory containing the generated HDL files. Optional. Default is ./output.







