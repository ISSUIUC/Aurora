#ifndef __SHARED_OUTPUT_H__
#define __SHARED_OUTPUT_H__
#include <stdint.h>

#define OUTPUT_BUF_SIZE 1024
#define OUTPUT_BUF_COUNT 4
struct SharedOutput {
    uint8_t output_buf[OUTPUT_BUF_COUNT][OUTPUT_BUF_SIZE];

    uint32_t current_read_buf;
    uint32_t current_write_buf;
};
#endif // __SHARED_OUTPUT_H__
