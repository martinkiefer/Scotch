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
    int* __restrict__ sk_t0;
    unsigned int ts0;
    unsigned int nthreads;
    
    unsigned int* __restrict__ c0;
    unsigned int* __restrict__ c0_lseed;
    unsigned int* __restrict__ c0_sseed;


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

v16ui h3(unsigned int x, v16ui* seed) {
    seed = (v16ui*) __builtin_assume_aligned(seed, 64);
    v16ui hash = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
    for(int i = 0; i < 32; i++){
        hash ^= is_set(x,i) * seed[i]; 
    }
    return hash;
}

v16si ech3(unsigned int v, v16ui seed, v16ui sbit){
    //First we compute the bitwise AND between the seed and the value
    //Aaaand here comes the parity
    v16si res = (v16si) (parity(v & seed) ^ nonlinear_h(v) ^ sbit) ;
    //std::cout << y[0] << "|" << y[1] << "|" << y[2] << "|" << y[3] << std::endl;
    return 2*res-1;
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
        v16si* vsk = (v16si*) __builtin_assume_aligned(p->sk_t0+id*p->skn_rows+i, 64);
        v16si counter = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
        v16ui indexes = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15};
        v16ui my_c0_ls = *((v16ui*) __builtin_assume_aligned(p->c0_lseed+i, 64));
        unsigned int x = *((unsigned int*) __builtin_assume_aligned(p->c0_sseed,64)+i/32);
        v16ui my_c0_ss = is_set(x, (indexes+i) % 32);
        
        for(unsigned int j = id*(partition_size); j < (id+1)*partition_size && j < p->ts0; j++){
            counter += ech3(p->c0[j],my_c0_ls,my_c0_ss);
            //counter += (v16si) my_c0_ls;
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
    p.skn_rows = ((skn_rows-1)/16+1) * 16;
    
    p.ts0= 268435456*2;

    p.sk_t0 = (int*) aligned_alloc(64,p.skn_rows*p.nthreads*sizeof(int));
    std::memset(p.sk_t0, 0, p.skn_rows*p.nthreads*sizeof(int));

    p.c0 = readUArrayFromFile("./data.dump");
    boost::random::mt19937 gen;

    p.c0_lseed =  (unsigned int*) aligned_alloc(64, sizeof(unsigned int)*p.skn_rows);
    p.c0_sseed =  (unsigned int*) aligned_alloc(64, ((p.skn_rows-1)/(sizeof(unsigned int)*8) +1)*sizeof(unsigned int));

    for(unsigned int i = 0; i < p.skn_rows;  i++ ){
       p.c0_lseed[i] = gen();
    }
    for(unsigned int i = 0; i < ((p.skn_rows-1)/(sizeof(unsigned int)*8) +1);  i++ ){
       p.c0_sseed[i] = gen();
    }

    unsigned long time = sketch_contruction(&p);
    //std::cout << "CPU Execution Time: " << time << std::endl;
    //std::cout << "Normalized execution time: " << ((float) time /p.skn_rows) << std::endl;
    //std::cout << "Throughput: "<< p.ts0*sizeof(unsigned int)*8.0 / (1000.0*1000.0*1000.0*time/1000.0) << " gbps" << std::endl;
    //std::cout << "Normalized Throughput: "<< p.ts0*sizeof(unsigned int)*8.0*p.skn_rows / (1000.0*1000.0*1000.0*time/1000.0) << " gbps" << std::endl;
    std::cout << skn_rows << ";" << p.ts0*sizeof(unsigned int)*8.0 / (1000.0*1000.0*1000.0*time/1000.0) << std::endl;

    writeSArrayToFile("sketch.dump", p.sk_t0, p.skn_rows*p.nthreads);
    return 0;
}
