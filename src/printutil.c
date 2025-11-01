#include <printutil.h>

void print_hex(uint8_t *data,size_t len){
    for(int i =0;i<len;i++){
        printf("%02x ", data[i]);
    }
}