# Sketches
In this folder, we provide several implementations of sketching algorithms. Feel free to adjust the implementations to your needs or use them as examples to implement your own.

## Sketch Descriptor
A Scotch implementation of a sketching algorithm is defined by a JSON file called sketching descriptor. It is primarily used for variable declarations and points to the ScotchDSL functions. It has the following attributes:

### Select-Update
**value_size, int:** Size of an input value.\
**state_size, int:** Size of a state value.\
**initial_state, str:** Initial value for the state (e.g "\"1111\""). Optional. Default is all bits set to zero. At the moment, matrix sketches are ignoring this parameter.

**offset_max_size, int:** Number of bits required for the output value of the select function.\
**selector_seed_size, int:** Size of the random seed passed to the selector function of each row.\
**selector_function_file, str:** Path to the ScotchDSL selector function file.\
**select_function_variables, JSON:** Contains pairs of variable names and the number of bits required for them (e.g. "my_variable" : 32). These ones are for the select function.


**update_seed_size, int:** Size of the random seed passed to the update function.\
**update_function_file, str:** Path to the ScotchDSL update function file.\
**update_function_variables, JSON:** Contains pairs of variable names and the number of bits required for them (e.g. "my_variable" : 32). These ones are for the update function.


### Map-Apply
**value_size, int:** Size of an input value.\
**state_size, int:** Size of a state value.\
**parallel_values, int:** Number of parallel input values.\
**compute_neutral, int:** Neutral element passed to the apply function is no enable was asserted. (e.g. "\"00\"")
**initial_state, str:** Initial value for the state (e.g "\"1111\""). Optional. Default is all bits set to zero.

**compute_out_size, int:** Number of bits returned by the map function.\
**compute_function_file, str:** Path to the ScotchDSL map function file.\
**compute_function_variables, JSON:** Contains pairs of variable names and the number of bits required for them (e.g. "my_variable" : 32). These ones are for the map function.

**update_seed_size, int:** Size of the random seed passed to the apply function.\
**update_function_file, str:** Path to the ScotchDSL apply function file.\
**update_function_variables, JSON:** Contains pairs of variable names and the number of bits required for them (e.g. "my_variable" : 32). These ones are for the apply function.

### Future
In the future, setting descriptor variables will probably be moved directly to the ScotchDSL files. This would effectively remove the need for additional JSON files and get rid of inconsistencies (e.g. for map-apply variable names.
