# Autotune
This folder contains all autotune related logic and the autotune.py script.

## autotune.py
The script is the frontend to the autotune algorithm. A sketching descriptor and a matching I/O controller are required to use it. 
Returns the maximum sketch size supported for the specified configuration without violating timing set by the I/O controller.
The synthesis projects created and compiled in the process are found in the ./work directory created at runtime.

Depending on the FPGA used, running autotune can take several days and consume tens of Gigabytes of data. Use tmux/nohup and provide disk space accordingly.

```
python3 ReplicatedMatrixSketchGenerator.py plain
  -generator [column, matrix, column-ma] 
      Type of generator used. column and matrix use the select-update model. 
      Column-ma is for column sketches given in map-apply.
  -descriptor_path str
      Path to sketch descriptor.
  -template_path
      Path to IO controller folder.
  -dp int
      Degree of data parallelism used. 
      Parameter is ignored for column-ma generator as it is fixed in descriptor.
  -memseg_depth int
      Depth of segments used for state memory. Only affects matrix generators.
  -quartus_prefix str
      Path to quartus executable. (e.g. /opt/quartus_prime/bin/quartus)
  -fix_rows int
      Fix the number of rows to a particular value. Columns are optimized then. 
      Forbidden for column-ma and column. Can not be used together with fix_cols.
  -fix_cols int
      Fix the number of columns to a particular value. Rows are optimized then.
      Can not be used together with fix_rows.
  -initial_guess int
      Initial guess to establish search interval. Optional. Defaut: 16.      
  -cfactor int
      Branching factor for the collect unit. Optional. Defaut: 4.
  -dfactor int
      Branching factor for the collect unit. Optional. Defaut: 4.
  
```
