#include "max_read.h"

#include<string.h>

#include "driver/spi_slave.h"

#include "pins.h"
#include "soc/gpio_pins.h"

// void printbin(char *data,int len){
//     for(int i =0;i<len/8;i++){
//         char c = data[i*8];
//         for(int j =0;j<8;j++){
//             printf("%c ",'0'+(c&(0x80>>j)));
//         }
//         printf("\n");
//     }
// }

void max_read(void) {
    spi_bus_config_t slave_bus_config = {
        .mosi_io_num=MOSI,
        .miso_io_num=-1,
        .sclk_io_num=SCK,
        .quadwp_io_num = -1,
        .quadhd_io_num = -1,
    };

    spi_slave_interface_config_t config = {
        .spics_io_num=Q0,
        .flags=0,
        .queue_size=3,
        .mode=0,
    };
    int ret = spi_slave_initialize(SPI3_HOST, &slave_bus_config, &config, SPI_DMA_CH_AUTO);
    assert(ret == ESP_OK);
    char recv_buffer[128]={0};
    spi_slave_transaction_t transaction;
    while (true)
    {
        memset(recv_buffer,0,128);

        transaction.length = 128*8;
        transaction.rx_buffer = recv_buffer;
        transaction.tx_buffer = NULL;

        ret = spi_slave_transmit(SPI3_HOST, &transaction, 200);
        printf("Spi read %s\n",recv_buffer);
    }
    
    // Now 
}
