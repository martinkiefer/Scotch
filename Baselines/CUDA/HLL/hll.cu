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
 
 __device__ unsigned int is_set(unsigned int x, unsigned int pos) {
     return (x >> pos) & 1;
 }
 

 __global__ void construct_sketch(
    unsigned int replicas,
    unsigned int skn_cols,
    unsigned int n_values,
    unsigned int* __restrict__ c0,
    unsigned int* __restrict__ c0_select_seed,
    unsigned int* __restrict__ c0_update_seed,
    unsigned int* __restrict__ sketches) 
{
    unsigned int global_size = gridDim.x * blockDim.x;
    unsigned int global_id = blockIdx.x * blockDim.x + threadIdx.x;


    //unsigned int my_c0_ls = (sketch < replicas) ? c0_ls[sketch] : 0; 
    //unsigned int my_c0_ss = (sketch < replicas) ? is_set(c0_ss[sketch/32], sketch % 32) : 0;
    //unsigned int* my_c0_select_seed = (sketch < replicas) ? c0_select_seed + sketch : 0;

    unsigned int r = global_id % replicas;

    unsigned int sseeds[32];
    for(int i = 0; i < 32; i++){
        sseeds[i] = c0_select_seed[i];
    }

    unsigned int useeds[32];
    for(int i = 0; i < 32; i++){
        useeds[i] = c0_update_seed[i];
    }

    //Energy consumption endless loop. Comment in, if necessary.
    //while(1)
    for(unsigned int i = global_id; i < n_values; i += global_size){
            unsigned int select = 0;
            for(int k = 0; k < 32; k++)  if(is_set(c0[i],k)) select ^= sseeds[k] ;
            select = select % skn_cols;

            unsigned int update = 0;
            for(int k = 0; k < 32; k++)  if(is_set(c0[i],k)) update ^= useeds[k] ;
            //printf("%d\n", __clz(update));
            //int update = ech3(c0[i],my_c0_ls,my_c0_ss);
            atomicMax(&sketches[r*skn_cols+select], (unsigned int) (__clz(update)+1));
            //printf(" %d %d\n",__clz(update)+1, sketches[r*skn_cols+select]);
    }
}

typedef struct{

    size_t replicas;
    size_t skn_cols;

    unsigned int* sk_t0;
    unsigned int ts0;

    unsigned int* c0;
    unsigned int* c0_select_seed;
    unsigned int* c0_update_seed;

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
    size_t local = 64;
    int tot_SM = 0;
    int tot_tpsm = 0;
    cudaDeviceGetAttribute(&tot_SM, cudaDevAttrMultiProcessorCount, 0);
    cudaDeviceGetAttribute(&tot_tpsm, cudaDevAttrMaxThreadsPerMultiProcessor, 0);
    unsigned int target_utilization = tot_SM*tot_tpsm;
    size_t global = target_utilization;

    auto begin = std::chrono::high_resolution_clock::now();
    int iterations = 1;
    for(int i = 0; i < iterations; i++){
            construct_sketch<<<global/local, local>>>((unsigned int) p->replicas, (unsigned int) p->skn_cols, p->ts0, p->c0, p->c0_select_seed, p->c0_update_seed, p->sk_t0);
            gpuErrchk(cudaPeekAtLastError());
    }
    cudaDeviceSynchronize();
    auto end = std::chrono::high_resolution_clock::now();
    return std::chrono::duration_cast<std::chrono::milliseconds>(end-begin).count()/ (double) iterations;
}



int main( int argc, const char* argv[] )
{
    parameters p;
    cudaSetDevice(0);

    p.replicas = (unsigned int) atoll(argv[1]);
    p.skn_cols = (unsigned int) atoll(argv[2]);

    p.ts0= 2147483648/4;
    
    cudaMalloc((void **) &p.sk_t0, p.replicas*p.skn_cols*sizeof(unsigned int));
    cudaMemset(p.sk_t0, 0, p.replicas*p.skn_cols*sizeof(unsigned int));

    unsigned int* t0_c0 = readUArrayFromFile("./data.dump");
    cudaMalloc((void **) &p.c0, p.ts0*sizeof(unsigned int));
    cudaMemcpy(p.c0, t0_c0, sizeof(unsigned int)*p.ts0, cudaMemcpyHostToDevice);


    boost::random::mt19937 gen(1337);
    unsigned int* c0_select_seed =  (unsigned int*) malloc(sizeof(unsigned int)*32);
    for(unsigned int i = 0; i < 32; i++){
       c0_select_seed[i] = gen();
    }

    unsigned int* c0_update_seed =  (unsigned int*) malloc(sizeof(unsigned int)*32);
    for(unsigned int i = 0; i < 32; i++){
       c0_update_seed[i] = gen();
    }

    p.c0_select_seed = (unsigned int*) cudaAllocAndCopy(c0_select_seed, 32*sizeof(unsigned int));
    p.c0_update_seed = (unsigned int*) cudaAllocAndCopy(c0_update_seed, 32*sizeof(unsigned int));

    double time = sketch_contruction(&p);
    std::cout << p.replicas << ";" << p.skn_cols << ";" << p.ts0*sizeof(unsigned int)*8.0 / (1000.0*1000.0*1000.0*time / 1000.0) << std::endl;

    int* res = (int*) malloc(p.replicas*p.skn_cols*sizeof(int));
    cudaMemcpy(res, p.sk_t0, p.replicas*p.skn_cols*sizeof(int), cudaMemcpyDeviceToHost);

    writeSArrayToFile("sketch.dump", res, p.replicas*p.skn_cols);
    
    //Debugging print
    for(int i = 0; i < p.replicas; i++){
        //std::cout << "Row: | " << i << std::endl;
        int row_sum = 0;
        for(int j = 0; j < p.skn_cols; j++){
            row_sum += res[i*p.skn_cols+ j];
            //std::cout << res[i*p.skn_cols+ j] << " | ";
        }
        //std::cout << "| Sum: " << row_sum << std::endl;
    }


    return 0;
}
