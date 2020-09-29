# CPU Baselines
Our CPU baselines can be compiled with g++. Be sure to add -fopenmp as a compiler flag and include Boost.

For matrix sketches (FAGMS, CM), the syntax is 
```
  ./executable rows columns parallel_threads
```

For column sketches (AGMS, MH), the number of columns can be omitted since it is fixed to one. Set the number of parallel threads to as many hardware threads are available on your architecture.


# Implementation Strategies
As CPUs have large caches, each thread maintains its own copy of the sketch.

## Column Sketches
Each thread is responsible for a chunk of the data. The implementation performs multiple passes over the chunk. Each pass updates 16 sketch counters simultaneously in a vectorized fashion (AVX512). The implementations is compute bound for reasonably large sketch sizes.

## Matrix / Row Sketches
Each thread is responsible for a chunk of the data. The implementation performs multiple passes over the chunk. One pass per row is made, computing the update for 16 consecutive input values in a vectorized fashion (AVX512). The random reads and writes to main memory have to be serialized. The implementation is mostly compute bound, for sketch matrices with large rows it can become bound by memory latency.

# Generating Sample Data
The implementations assume a 2G input file called ./data.dump exists. It can be generated using the following command: 

```
head -c 2G </dev/urandom > ./data.dump
```
