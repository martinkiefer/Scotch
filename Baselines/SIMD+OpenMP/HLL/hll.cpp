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
    unsigned char* __restrict__ sk_t0;
    unsigned int ts0;
    unsigned int nthreads;
    
    unsigned int* __restrict__ select_seed;
    unsigned int* __restrict__ update_seed;

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

void writeSArrayToFile(const char* filename, unsigned char* elements, size_t size){
    FILE *f1 = fopen(filename, "w");
    assert(f1 != NULL);
    
    fwrite(elements, sizeof(unsigned char), size, f1);
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

    //Energy consumption endless loop. Comment in, if necessary.
    //while(1)
    for(unsigned int i = 0; i < p->skn_rows; i++){

	unsigned int j = id*(partition_size);
        for(j = id*(partition_size); j < upper; j += 16){
            v16ui select = h3(*((v16ui*) (p->c0+j)), p->select_seed+32*i);
            v16ui update = h3(*((v16ui*) (p->c0+j)), p->update_seed+32*i);

            //select = select >> (1 + __builtin_clz(p->skn_cols));
            select = select % p->skn_cols;

            for(unsigned int k = 0; k < 16; k++){
                //p->sk_t0[id*p->skn_rows*p->skn_cols + i*p->skn_cols + select[k]] += 1; 
		unsigned int o = id*p->skn_rows*p->skn_cols + i*p->skn_cols + select[k];
                p->sk_t0[o] = std::max(p->sk_t0[o], (unsigned char) (1+__builtin_clz(update[k])));
            }
        }


        for(; j < partition_upper && j < p->ts0; j++){
            unsigned int select = h3( *(p->c0+j), p->select_seed+32*i);
            unsigned int update = h3( *(p->c0+j), p->update_seed+32*i);
            update = __builtin_clz(update);
            //int update = 1;
            //select = select >> (1 + __builtin_clz(p->skn_cols));
            select = select % p->skn_cols;

            //p->sk_t0[id*p->skn_rows*p->skn_cols + i*p->skn_cols + select] += 1; 
            unsigned int o = id*p->skn_rows*p->skn_cols + i*p->skn_cols + select;
            p->sk_t0[o] = std::max(p->sk_t0[o], (unsigned char) update); 
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

    p.sk_t0 = (unsigned char*) aligned_alloc(64,p.skn_rows*p.skn_cols*p.nthreads*sizeof(unsigned char));
    std::memset(p.sk_t0, 0, p.skn_rows*p.skn_cols*p.nthreads*sizeof(unsigned char));

    p.c0 = readUArrayFromFile("./data.dump");
    boost::random::mt19937 gen;


    p.select_seed = (unsigned int*) aligned_alloc(64,32*p.skn_rows*sizeof(unsigned int));
    for(unsigned int i = 0; i < p.skn_rows*32;  i++ ){
       p.select_seed[i] = gen();
    }

    p.update_seed = (unsigned int*) aligned_alloc(64,32*p.skn_rows*sizeof(unsigned int));
    for(unsigned int i = 0; i < p.skn_rows*32;  i++ ){
       p.update_seed[i] = gen();
    }
    unsigned long time = 0;
    volatile int x = 1;
    while(x) time = sketch_contruction(&p);

/*    for(unsigned int i = 0; i < p.nthreads; i++){
        std::cout << "Thread: " << i << std::endl;
        for(unsigned int j = 0; j < p.skn_cols; j++){
                std::cout << "|" << (unsigned int) p.sk_t0[i*p.skn_cols+j] ;
        }
        std::cout << std::endl;
    }
*/

    //std::cout << "CPU Execution Time: " << time << std::endl;
    //std::cout << "Normalized execution time: " << ((float) time /p.skn_rows) << std::endl;
    //std::cout << "Throughput: "<< p.ts0*sizeof(unsigned int)*8.0 / (1000.0*1000.0*1000.0*time/1000.0) << " gbps" << std::endl;
    //std::cout << "Normalized Throughput: "<< p.ts0*sizeof(unsigned int)*8.0*p.skn_rows / (1000.0*1000.0*1000.0*time/1000.0) << " gbps" << std::endl;
    std::cout << p.skn_rows << ";" << p.skn_cols << ";" << p.ts0*sizeof(unsigned int)*8.0 / (1000.0*1000.0*1000.0*time/1000.0) << std::endl;

    writeSArrayToFile("sketch.dump", p.sk_t0, p.skn_rows*p.skn_cols*p.nthreads);
    return 0;
}
