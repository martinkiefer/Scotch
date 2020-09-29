# CUDA Baselines
Our CUDA baselines can be compiled with nvcc. Make sure to include Boost.

For matrix sketches (FAGMS, CM), the syntax is 
```
  ./executable rows columns
```

For column sketches (AGMS, MH), the number of columns can be omitted since it is fixed to one.
For row sketches (FC, HLL), the number of rows determines the number of replicas that is created simultaneously (see below).


# Implementation Strategies

## Column Sketches
Each thread is responsible for one chunk of input data and one sketch counter. Sketch states are kept in registers and merged using atomics at the end. The implementation is compute-bound.

## Matrix Sketches
There are two implementation strategies we evaluated. The experiments in the paper always show the performance of the better implementation for each data point.

**Roy-by-Row:** All threads cooperatively work on a single row using atomics. Ideal for large rows with few conflicts since it improves locality and can prevent some reads and writes to device memory.

**Row-Parallel**:  Each thread is responsible for one chunk of the input data and one row. Atomics are used for every update. Ideal for small rows with a higher chance for conflicts since the entire sketch is built simultaneously. 

The implementations are bound by computation, random memory accesses, or memory conflicts depending on the size of the sketch matrix.

## Row Sketches
As we can not run the Row-Parallel strategy due to only one row being required, we use a different strategy. Similar to the CPU implementation, we create multiple replicas of the sketch simultaneously. The number of rows on the command line determines the number of replicas consntructed in a data parallel fashion over the input data. Setting the number of replicas to one is equivalent to the Row-by-Row strategy.

The implementations is bound by computation, random memory accesses, or memory conflicts depending on the size of the sketch matrix and the number of replicas.


# Generating Sample Data
The implementations assume a 2G input file called ./data.dump exists. It can be generated using the following command: 

```
head -c 2G </dev/urandom > ./data.dump
```
