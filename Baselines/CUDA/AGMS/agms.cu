#pragma GCC diagnostic ignored "-Wignored-attributes"
#include <iostream>
#include <chrono>

#include <boost/random/mersenne_twister.hpp>
#include <boost/random/uniform_int_distribution.hpp>

#define gpuErrchk(ans) { gpuAssert((ans), __FILE__, __LINE__); }
inline void gpuAssert(cudaError_t code, const char *file, int line, bool abort=true)
{
   if (code != cudaSuccess) 
   {
      fprintf(stderr,"GPUassert: %s %s %d\n", cudaGetErrorString(code), file, line);
      if (abort) exit(code);
   }
}

__device__ unsigned int parity(unsigned int x) {
    unsigned int y;
    y = x ^ (x >> 1);
    y = y ^ (y >> 2);
    y = y ^ (y >> 4);
    y = y ^ (y >> 8);
    y = y ^ (y >>16);
    return y & 1;
 }
 
 __device__ unsigned int nonlinear_h(unsigned int x) {
     return parity((x >> 0) | (x >> 1));
 }
 
 __device__ unsigned int is_set(unsigned int x, unsigned int pos) {
     return (x >> pos) & 1;
 }
 

 __device__ unsigned int h3(unsigned int x, unsigned int nsketches, unsigned int* seed) {
    unsigned int hash = 0;
    for(int i = 0; i < 32; i++){
        hash ^=  seed[i*nsketches]*is_set(x,i); 
    }
    return hash;
}


 __device__ int ech3(unsigned int v, unsigned int seed, unsigned int sbit){
     //First we compute the bitwise AND between the seed and the value
     //Aaaand here comes the parity
     int res = parity(v & seed) ^ nonlinear_h(v) ^ sbit ;
     return 2*res-1;
 }

 __global__ void construct_sketch(
    unsigned int skn_rows,
    unsigned int n_values,
    unsigned int n_replicas,
    unsigned int* __restrict__ c0,
    unsigned int* __restrict__ c0_ls, 
    unsigned int* __restrict__ c0_ss,
    int* __restrict__ sketches) 
{
    //unsigned int global_size = gridDim.x * blockDim.x;
    unsigned int global_id = blockIdx.x * blockDim.x + threadIdx.x;

    //unsigned full_work_set = skn_rows * n_replicas;
    unsigned int partition_size = (n_values-1)/n_replicas+1;

        unsigned int partition = global_id / skn_rows;
        unsigned int sketch = global_id % skn_rows;
        unsigned int my_c0_ls = (sketch < skn_rows) ? c0_ls[sketch] : 0; 
        unsigned int my_c0_ss = (sketch < skn_rows) ? is_set(c0_ss[sketch/32], sketch % 32) : 0;
   

        int counter = 0;
        for(unsigned int i = partition*partition_size; i < (partition+1)*partition_size && i < n_values; i++){
            if(sketch >= skn_rows) continue;

                int update = ech3(c0[i],my_c0_ls,my_c0_ss);
                counter += update;
        }
        atomicAdd(sketches+sketch, counter); 
}


typedef struct{

    size_t skn_rows;

    int* sk_t0;
    unsigned int ts0;

    unsigned int* c0;
    unsigned int* c0_lseed;
    unsigned int* c0_sseed;
} parameters;

void* cudaAllocAndCopy(void* hst_ptr, size_t size){
    void* d_ptr;
    cudaMalloc((void **) &d_ptr, size);
    cudaMemcpy(d_ptr, hst_ptr, size, cudaMemcpyHostToDevice);
    return d_ptr;
}

void writeSArrayToFile(const char* filename, int* elements, size_t size){
    FILE *f1 = fopen(filename, "w");
    assert(f1 != NULL);
    
    fwrite(elements, sizeof(int), size, f1);
    fclose(f1);
}

unsigned int* readUArrayFromFile(const char* filename, size_t * filesize = NULL){
    FILE *f1 = fopen(filename, "rb");
    assert(f1 != NULL);
    fseek(f1, 0, SEEK_END);
    size_t fsize1 = ftell(f1);
    if(filesize) *filesize=fsize1;
    fseek(f1, 0, SEEK_SET);
    unsigned int* tab1 = (unsigned int*) malloc(fsize1);
    size_t x = fread(tab1, fsize1, 1, f1);
    fclose(f1);

    return tab1;
}

unsigned long sketch_contruction(parameters* p){
    size_t local = 64;
    int tot_SM = 0;
    cudaDeviceGetAttribute(&tot_SM, cudaDevAttrMultiProcessorCount, 0);
    unsigned int target_utilization = tot_SM*2048;
    unsigned int n_partitions = target_utilization / p->skn_rows;
    unsigned int target_global_size = n_partitions * p->skn_rows;
    //unsigned int slack = ((p->ts0-1)/n_partitions+1)*n_partitions - p->ts0;
    

    size_t global = target_global_size;
    //std::cout << "local: " << local << " global:" << global << " partitions: " << n_partitions << std::endl;
    //std::cout << "Slack: " << slack << std::endl;

    auto begin = std::chrono::high_resolution_clock::now();
    construct_sketch<<<global/local, local>>>((unsigned int) p->skn_rows, p->ts0, n_partitions, p->c0, p->c0_lseed, p->c0_sseed, p->sk_t0);
    //while(1) construct_sketch<<<global/local, local>>>((unsigned int) p->skn_rows, p->ts0, n_partitions, p->c0, p->c0_lseed, p->c0_sseed, p->sk_t0);
    gpuErrchk(cudaPeekAtLastError());
    cudaDeviceSynchronize();
    auto end = std::chrono::high_resolution_clock::now();
    return std::chrono::duration_cast<std::chrono::milliseconds>(end-begin).count();
}



int main( int argc, const char* argv[] )
{
    parameters p;
    cudaSetDevice(0);

    p.skn_rows = (unsigned int) atoll(argv[1]);

    p.ts0= 2147483648/4;
    
    cudaMalloc((void **) &p.sk_t0, p.skn_rows*sizeof(int));
    cudaMemset(p.sk_t0, 0, p.skn_rows*sizeof(int));

    unsigned int* t0_c0 = readUArrayFromFile("/data/Martin/GPU/GPU-CUDA-AGMS/data.dump");
    cudaMalloc((void **) &p.c0, p.ts0*sizeof(unsigned int));
    cudaMemcpy(p.c0, t0_c0, sizeof(unsigned int)*p.ts0, cudaMemcpyHostToDevice);


    unsigned int* c0_lseed =  (unsigned int*) malloc(sizeof(unsigned int)*p.skn_rows);
    unsigned int* c0_sseed =  (unsigned int*) malloc(((p.skn_rows-1)/(sizeof(unsigned int)*8) +1)*sizeof(unsigned int));

    boost::random::mt19937 gen;
    for(unsigned int i = 0; i < p.skn_rows;  i++ ){
       c0_lseed[i] = gen();
    }
    for(unsigned int i = 0; i < ((p.skn_rows-1)/(sizeof(unsigned int)*8) +1);  i++ ){
       c0_sseed[i] = gen();
    }
    p.c0_lseed = (unsigned int*) cudaAllocAndCopy(c0_lseed, sizeof(unsigned int)*p.skn_rows);
    p.c0_sseed = (unsigned int*) cudaAllocAndCopy(c0_sseed, ((p.skn_rows-1)/(sizeof(unsigned int)*8) +1)*sizeof(unsigned int));
    unsigned long time = 0;
    //while(1) time = sketch_contruction(&p);
    time = sketch_contruction(&p);
    //std::cout << "GPU Execution Time: " << time << std::endl;
    //std::cout << "Normalized execution time: " << ((float) time /p.skn_rows) << std::endl;
    //std::cout << "Throughput: "<< p.ts0*sizeof(unsigned int)*8.0 / (1000.0*1000.0*1000.0*time/1000.0) << " gbps" << std::endl;
    //std::cout << "Normalized Throughput: "<< p.ts0*sizeof(unsigned int)*8.0*p.skn_rows / (1000.0*1000.0*1000.0*time/1000.0) << " gbps" << std::endl;
    std::cout << p.skn_rows << ";" << p.ts0*sizeof(unsigned int)*8.0 / (1000.0*1000.0*1000.0*time/1000.0) << std::endl;

    int* res = (int*) malloc(p.skn_rows*sizeof(int));
    cudaMemcpy(res, p.sk_t0, p.skn_rows*sizeof(int), cudaMemcpyDeviceToHost);

    writeSArrayToFile("sketch.dump", res, p.skn_rows);

    return 0;
}