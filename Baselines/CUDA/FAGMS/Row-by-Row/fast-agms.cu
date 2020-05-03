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


/* __device__ unsigned int h3(unsigned int x, unsigned int nsketches, unsigned long* seed) {
    unsigned long hash = 0;
    for(int i = 0; i < 16; i++){
        unsigned long seed_l = seed[i*nsketches];
        hash ^= seed_l & ((is_set(x,i*2)*0x00000000FFFFFFFFL) | (is_set(x, i*2+1)*0xFFFFFFFF00000000L)) ;
    }
    return ((unsigned int) hash ^ (unsigned int) (hash >> 32));
}*/

 __device__ int ech3(unsigned int v, unsigned int seed, unsigned int sbit){
     //First we compute the bitwise AND between the seed and the value
     //Aaaand here comes the parity
     int res = parity(v & seed) ^ nonlinear_h(v) ^ sbit ;
     return 2*res-1;
 }

 __global__ void construct_sketch(
    unsigned int r,
    unsigned int skn_cols,
    unsigned int n_values,
    unsigned int* __restrict__ c0,
    unsigned int* __restrict__ c0_ls, 
    unsigned int* __restrict__ c0_ss,
    unsigned int* __restrict__ c0_select_seed,
    int* __restrict__ sketches) 
{
    unsigned int sseeds[32];

    unsigned int global_size = gridDim.x * blockDim.x;
    unsigned int global_id = blockIdx.x * blockDim.x + threadIdx.x;


    unsigned int my_c0_ls = c0_ls[r]; 
    unsigned int my_c0_ss = is_set(c0_ss[r/32], r % 32);
    //unsigned int* my_c0_select_seed = (sketch < skn_rows) ? c0_select_seed + sketch : 0;


    for(int i = 0; i < 32; i++){
        sseeds[i] = c0_select_seed[r*32+i];
    }

    for(unsigned int i = global_id; i < n_values; i += global_size){
            unsigned int select = 0;
            for(int k = 0; k < 32; k++)  if(is_set(c0[i],k)) select ^= sseeds[k] ;
            select = select % skn_cols;

            int update = ech3(c0[i],my_c0_ls,my_c0_ss);
            //int update = 1;
            atomicAdd(&sketches[r*skn_cols+select], update);
    }
}

typedef struct{

    size_t skn_rows;
    size_t skn_cols;

    int* sk_t0;
    unsigned int ts0;

    unsigned int* c0;
    unsigned int* c0_lseed;
    unsigned int* c0_sseed;
    unsigned int* c0_select_seed;

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

double sketch_contruction(parameters* p){
    size_t local = 32;
    int tot_SM = 0;
    cudaDeviceGetAttribute(&tot_SM, cudaDevAttrMultiProcessorCount, 0);
    unsigned int target_utilization = tot_SM*2048;
    size_t global = target_utilization;

    auto begin = std::chrono::high_resolution_clock::now();
    int iterations = 1;
    for(int i = 0; i < iterations; i++){
        for(unsigned int r = 0; r < p->skn_rows; r++){
            construct_sketch<<<global/local, local>>>(r, (unsigned int) p->skn_cols, p->ts0, p->c0, p->c0_lseed, p->c0_sseed, p->c0_select_seed, p->sk_t0);
            gpuErrchk(cudaPeekAtLastError());
        }
    }
    cudaDeviceSynchronize();
    auto end = std::chrono::high_resolution_clock::now();
    return std::chrono::duration_cast<std::chrono::milliseconds>(end-begin).count()/ (double) iterations;
}



int main( int argc, const char* argv[] )
{
    parameters p;
    cudaSetDevice(0);

    p.skn_rows = (unsigned int) atoll(argv[1]);
    p.skn_cols = (unsigned int) atoll(argv[2]);

    p.ts0= 2147483648/4;
    
    cudaMalloc((void **) &p.sk_t0, p.skn_rows*p.skn_cols*sizeof(int));
    cudaMemset(p.sk_t0, 0, p.skn_rows*p.skn_cols*sizeof(int));

    unsigned int* t0_c0 = readUArrayFromFile("./data.dump");
    cudaMalloc((void **) &p.c0, p.ts0*sizeof(unsigned int));
    cudaMemcpy(p.c0, t0_c0, sizeof(unsigned int)*p.ts0, cudaMemcpyHostToDevice);


    unsigned int* c0_lseed =  (unsigned int*) malloc(sizeof(unsigned int)*p.skn_rows);
    unsigned int* c0_sseed =  (unsigned int*) malloc(((p.skn_rows-1)/(sizeof(unsigned int)*8) +1)*sizeof(unsigned int));
    unsigned int* c0_select_seed =  (unsigned int*) malloc(sizeof(unsigned int)*32*32*p.skn_rows);

    boost::random::mt19937 gen(1338);
    for(unsigned int i = 0; i < p.skn_rows;  i++ ){
       c0_lseed[i] = gen();
    }
    for(unsigned int i = 0; i < p.skn_rows*32*32; i++){
       c0_select_seed[i] = gen();
    }
    for(unsigned int i = 0; i < ((p.skn_rows-1)/(sizeof(unsigned int)*8) +1);  i++ ){
       c0_sseed[i] = gen();
    }
    p.c0_lseed = (unsigned int*) cudaAllocAndCopy(c0_lseed, sizeof(unsigned int)*p.skn_rows);
    p.c0_select_seed = (unsigned int*) cudaAllocAndCopy(c0_select_seed, p.skn_rows*32*32*sizeof(unsigned int));
    p.c0_sseed = (unsigned int*) cudaAllocAndCopy(c0_sseed, ((p.skn_rows-1)/(sizeof(unsigned int)*8) +1)*sizeof(unsigned int));

    double time = sketch_contruction(&p);
    std::cout << p.skn_rows << ";" << p.skn_cols << ";" << p.ts0*sizeof(unsigned int)*8.0 / (1000.0*1000.0*1000.0*time / 1000.0) << std::endl;

    int* res = (int*) malloc(p.skn_rows*p.skn_cols*sizeof(int));
    cudaMemcpy(res, p.sk_t0, p.skn_rows*p.skn_cols*sizeof(int), cudaMemcpyDeviceToHost);

    writeSArrayToFile("sketch.dump", res, p.skn_rows*p.skn_cols);
    
    /*Debugging print
    for(int i = 0; i < p.skn_rows; i++){
        //std::cout << "Row: | " << i << std::endl;
        int row_sum = 0;
        for(int j = 0; j < p.skn_cols; j++){
            row_sum += res[i*p.skn_cols+ j];
            std::cout << res[i*p.skn_cols+ j] << " | ";
        }
        std::cout << "| Sum: " << row_sum << std::endl;
    }*/


    return 0;
}
