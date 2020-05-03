#include <iostream>
#include <cstring>
#include <chrono>
#include <omp.h>

#include <boost/random/mersenne_twister.hpp>
#include <boost/random/uniform_int_distribution.hpp>

typedef int v16si __attribute__ ((vector_size (64)));
typedef unsigned int v16ui __attribute__ ((vector_size (64)));

typedef struct{
    unsigned int skn_rows;
    unsigned int skn_cols;
    int* __restrict__ sk_t0;
    unsigned int ts0;
    unsigned int nthreads;
    
    unsigned int* __restrict__ select_seed;

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

v16ui nonlinear_h(v16ui x) {
    return parity((x >> 0) | (x >> 1));
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

v16ui h3(v16ui x, unsigned int* seed) {
    v16ui hash = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
    for(int i = 0; i < 32; i++){
        hash ^= is_set(x,i) * seed[i]; 
    }
    return hash;
}

unsigned int h3(unsigned int x, unsigned int* seed) {
    unsigned int hash = 0;
    for(int i = 0; i < 32; i++){
        hash ^= is_set(x,i) * seed[i]; 
    }
    return hash;
}

v16si eh3(v16ui v, unsigned int seed, unsigned int sbit){
    //First we compute the bitwise AND between the seed and the value
    //Aaaand here comes the parity
    v16si res = (v16si) (parity(v & seed) ^ nonlinear_h(v) ^ sbit) ;
    //std::cout << y[0] << "|" << y[1] << "|" << y[2] << "|" << y[3] << std::endl;
    return 2*res-1;
}

int eh3(int v, unsigned int seed, unsigned int sbit){
    //First we compute the bitwise AND between the seed and the value
    //Aaaand here comes the parity
    int res = (int) (parity(v & seed) ^ nonlinear_h(v) ^ sbit) ;
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
    int id = omp_get_thread_num();

    unsigned int partition_size = (p->ts0-1) / (cnt) + 1;
    partition_size = ((partition_size-1) / 16 + 1) * 16;

    unsigned int partition_upper = (id+1)*partition_size;
    unsigned int data_upper = (p->ts0 / 16) * 16;
    unsigned int upper = std::min(partition_upper, data_upper);

    for(unsigned int i = 0; i < p->skn_rows; i++){

        //unsigned int c0_ls = *(p->c0_lseed+i);
        //unsigned int x = *(p->c0_sseed+i/32);
        //unsigned int c0_ss = is_set(x, i % 32);

	unsigned int j = id*(partition_size);
        for(j = id*(partition_size); j < upper; j += 16){
            v16ui select = h3(*((v16ui*) (p->c0+j)), p->select_seed+32*i);
            //v16si update = eh3(*((v16ui*) (p->c0+j)),c0_ls,c0_ss);

            //select = select >> (1 + __builtin_clz(p->skn_cols));
            select = select % p->skn_cols;

            for(unsigned int k = 0; k < 16; k++){
                p->sk_t0[id*p->skn_rows*p->skn_cols + i*p->skn_cols + select[k]] += 1; 
                //p->sk_t0[id*p->skn_rows*p->skn_cols + i*p->skn_cols + select[k]] += update[k];
            }
        }


        for(; j < partition_upper && j < p->ts0; j++){
            unsigned int select = h3( *(p->c0+j), p->select_seed+32*i);
            //int update = eh3(p->c0[j],c0_ls,c0_ss);
            int update = 1;
            //select = select >> (1 + __builtin_clz(p->skn_cols));
            select = select % p->skn_cols;

            //p->sk_t0[id*p->skn_rows*p->skn_cols + i*p->skn_cols + select] += 1; 
            p->sk_t0[id*p->skn_rows*p->skn_cols + i*p->skn_cols + select] += update; 
        }

    }
}
    auto end = std::chrono::high_resolution_clock::now();
    return std::chrono::duration_cast<std::chrono::milliseconds>(end-begin).count();
}

int main( int argc, const char* argv[] )
{
    parameters p;

    int skn_rows = atoi(argv[1]);
    int skn_cols = atoi(argv[2]);
    p.nthreads = atoi(argv[3]);
    p.skn_rows = skn_rows;
    p.skn_cols = skn_cols;
    //std::cout << "Rows: " << p.skn_rows << " x " << p.skn_cols << std::endl;
    
    p.ts0= 268435456*2;

    p.sk_t0 = (int*) aligned_alloc(64,p.skn_rows*p.skn_cols*p.nthreads*sizeof(int));
    std::memset(p.sk_t0, 0, p.skn_rows*p.skn_cols*p.nthreads*sizeof(int));

    p.c0 = readUArrayFromFile("./data.dump");
    boost::random::mt19937 gen;


    p.select_seed = (unsigned int*) aligned_alloc(64,32*p.skn_rows*sizeof(unsigned int));
    for(unsigned int i = 0; i < p.skn_rows*32;  i++ ){
       p.select_seed[i] = gen();
    }

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
    std::cout << p.skn_rows << ";" << p.skn_cols << ";" << p.ts0*sizeof(unsigned int)*8.0 / (1000.0*1000.0*1000.0*time/1000.0) << std::endl;

    writeSArrayToFile("sketch.dump", p.sk_t0, p.skn_rows*p.skn_cols*p.nthreads);
    return 0;
}
