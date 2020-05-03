#include <iostream>
#include <cstring>
#include <chrono>
#include <omp.h>

#include <boost/random/mersenne_twister.hpp>
#include <boost/random/uniform_int_distribution.hpp>

typedef int v16si __attribute__ ((vector_size (64)));
typedef unsigned int v16ui __attribute__ ((vector_size (64)));

typedef struct{
    size_t skn_rows;
    unsigned int* __restrict__ sk_t0;
    unsigned int ts0;
    unsigned int nthreads;
    
    unsigned int* __restrict__ select_seed;
    unsigned int* __restrict__ c0;

} parameters;


unsigned int* readUArrayFromFile(const char* filename, size_t * filesize = NULL){
    FILE *f1 = fopen(filename, "rb");
    assert(f1 != NULL);
    fseek(f1, 0, SEEK_END);
    size_t fsize1 = ftell(f1);
    if(filesize) *filesize=fsize1;
    fseek(f1, 0, SEEK_SET);
    unsigned int* tab1 = (unsigned int*) aligned_alloc(64,fsize1);
    size_t x = fread(tab1, fsize1, 1, f1);
    fclose(f1);

    return tab1;
}

void writeSArrayToFile(const char* filename, int* elements, size_t size){
    FILE *f1 = fopen(filename, "w");
    assert(f1 != NULL);
    
    fwrite(elements, sizeof(int), size, f1);
    fclose(f1);
}

v16ui parity(v16ui x) {
   v16ui y;
   y = x ^ (x >> 1);
   y = y ^ (y >> 2);
   y = y ^ (y >> 4);
   y = y ^ (y >> 8);
   y = y ^ (y >>16);
   return y & 1;
}

unsigned int parity(unsigned int x) {
   unsigned int y;
   y = x ^ (x >> 1);
   y = y ^ (y >> 2);
   y = y ^ (y >> 4);
   y = y ^ (y >> 8);
   y = y ^ (y >> 16);
   return y & 1;
}

unsigned int nonlinear_h(unsigned int x) {
    return __builtin_parity((x >> 0) | (x >> 1));
}

v16ui is_set(v16ui x, v16ui pos) {
    return (x >> pos) & 1;
}

v16ui is_set(unsigned int x, v16ui pos) {
    return (x >> pos) & 1;
}

unsigned int is_set(unsigned int x, unsigned int pos) {
    return (x >> pos) & 1;
}

v16ui is_set(v16ui x, unsigned int pos) {
    return (x >> pos) & 1;
}

v16ui h3(unsigned int x, v16ui* seed) {
    seed = (v16ui*) __builtin_assume_aligned(seed, 64);
    v16ui hash = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
    for(int i = 0; i < 32; i++){
        hash ^= is_set(x,i) * seed[i]; 
    }
    return hash;
}

v16ui h3(v16ui x, unsigned int* seed) {
    v16ui hash = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
    for(int i = 0; i < 32; i++){
        hash ^= is_set(x,i) * seed[i];
    }
    return hash;
}


unsigned long sketch_contruction(parameters* p){
    omp_set_dynamic(0);
    omp_set_num_threads(p->nthreads);

    auto begin = std::chrono::high_resolution_clock::now();

#pragma omp parallel
{    
    unsigned int cnt = omp_get_num_threads();
    unsigned int partition_size = (p->ts0-1) / cnt + 1;
    int id = omp_get_thread_num();

    for(unsigned int i = 0; i < p->skn_rows; i+=16){
        v16ui* vsk = (v16ui*) __builtin_assume_aligned(p->sk_t0+id*p->skn_rows+i, 64);
        v16ui counter = {UINT_MAX,UINT_MAX,UINT_MAX,UINT_MAX,UINT_MAX,UINT_MAX,UINT_MAX,UINT_MAX,UINT_MAX,UINT_MAX,UINT_MAX,UINT_MAX,UINT_MAX,UINT_MAX,UINT_MAX,UINT_MAX};
        
        for(unsigned int j = id*(partition_size); j < (id+1)*partition_size && j < p->ts0; j++){
            v16ui x = h3(*(p->c0+j), ((v16ui*) (p->select_seed+i*32))) ;
            counter = (x < counter)*x + (x > counter)*counter;
        }
        *vsk = counter;
    }
}
    auto end = std::chrono::high_resolution_clock::now();
    return std::chrono::duration_cast<std::chrono::milliseconds>(end-begin).count();
}

int main( int argc, const char* argv[] )
{
    parameters p;

    int skn_rows = atoi(argv[1]);
    p.nthreads = atoi(argv[2]);
    p.skn_rows = ((skn_rows-1)/16+1)*16;
    
    p.ts0= 268435456*2;

    p.sk_t0 = (unsigned int*) aligned_alloc(64,p.skn_rows*p.nthreads*sizeof(unsigned int));
    std::memset(p.sk_t0, 255, p.skn_rows*p.nthreads*sizeof(int));

    p.c0 = readUArrayFromFile("./data.dump");
    boost::random::mt19937 gen;

    p.select_seed = (unsigned int*) aligned_alloc(64,32*p.skn_rows*sizeof(unsigned int));
    for(unsigned int i = 0; i < p.skn_rows*32;  i++ ){
       p.select_seed[i] = gen();
    }

    unsigned long time = sketch_contruction(&p);
    std::cout << skn_rows << ";" << p.ts0*sizeof(unsigned int)*8.0 / (1000.0*1000.0*1000.0*time/1000.0) << std::endl;

    writeSArrayToFile("sketch.dump", (int*) p.sk_t0, p.skn_rows*p.nthreads);
    return 0;
}
