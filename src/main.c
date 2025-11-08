/*
 * SPDX-FileCopyrightText: 2010-2022 Espressif Systems (Shanghai) CO LTD
 *
 * SPDX-License-Identifier: CC0-1.0
 */

#include <stdio.h>
#include <inttypes.h>
#include "sdkconfig.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_chip_info.h"
#include "esp_flash.h"
#include "esp_system.h"
#include "driver/gpio.h"
#include "pins.h"
#include "MAX2769.h"

#include "driver/spi_master.h"
#include "max_read.h"
#include "max_read2.h"

#include "shared_output.h"
#include "tinyusb.h"
#include "tinyusb_cdc_acm.h"
#include "tinyusb_default_config.h"
#include "printutil.h"

#if TUD_OPT_HIGH_SPEED
    #warn "TUD OPT HIGH SPEED"
#endif

static const tusb_desc_device_t cdc_device_descriptor = {
    .bLength = sizeof(cdc_device_descriptor),
    .bDescriptorType = TUSB_DESC_DEVICE,
    .bcdUSB = 0x0200,
    .bDeviceClass = TUSB_CLASS_MISC,
    .bDeviceSubClass = MISC_SUBCLASS_COMMON,
    .bDeviceProtocol = MISC_PROTOCOL_IAD,
    .bMaxPacketSize0 = CFG_TUD_ENDPOINT0_SIZE,
    .idVendor = 0x0155,
    .idProduct = 0xa40a,
    .bcdDevice = 0x0100,
    .iManufacturer = 0x01,
    .iProduct = 0x02,
    .iSerialNumber = 0x01,
    .bNumConfigurations = 0x01
};



#if (TUD_OPT_HIGH_SPEED)
static const tusb_desc_device_qualifier_t device_qualifier = {
    .bLength = sizeof(tusb_desc_device_qualifier_t),
    .bDescriptorType = TUSB_DESC_DEVICE_QUALIFIER,
    .bcdUSB = 0x0200,
    .bDeviceClass = TUSB_CLASS_MISC,
    .bDeviceSubClass = MISC_SUBCLASS_COMMON,
    .bDeviceProtocol = MISC_PROTOCOL_IAD,
    .bMaxPacketSize0 = CFG_TUD_ENDPOINT0_SIZE,
    .bNumConfigurations = 0x01,
    .bReserved = 0
};
#endif

struct SharedOutput output;

static void tinyusb_cdc_rx_callback(int itf, cdcacm_event_t *event)
{
}


void init_gpio(void) {
    // Init gpio
    gpio_set_direction(LED_RED, GPIO_MODE_OUTPUT);
    gpio_set_direction(LED_BLUE, GPIO_MODE_OUTPUT);
    gpio_set_direction(LED_GREEN, GPIO_MODE_OUTPUT);
    gpio_set_direction(LED_ORANGE, GPIO_MODE_OUTPUT);

    // Disable all GPIOs
    gpio_set_level(LED_RED, 0);
    gpio_set_level(LED_BLUE, 0);
    gpio_set_level(LED_GREEN, 0);
    gpio_set_level(LED_ORANGE, 0);
}

void max_read_main(void)
{
    gpio_set_level(LED_GREEN, 1);
    spi_bus_config_t max_2769_serial_in = {
        .miso_io_num = -1, // We do not have master in for the MAX 2769
        .mosi_io_num = MOSI,
        .sclk_io_num = SCK,
        .quadwp_io_num = -1,
        .quadhd_io_num = -1,
        .max_transfer_sz = 32,
    };
    // printf("Setting");
    // fflush(stdout);
    esp_err_t err = spi_bus_initialize(SPI2_HOST, &max_2769_serial_in, SPI_DMA_DISABLED);
    if (err != ESP_OK) {
        gpio_set_level(LED_RED, 1);
    }
    // ESP_ERROR_CHECK(err);
    // printf("Setup SPI bus");
    // fflush(stdout);
    spi_device_interface_config_t max_2769_config = {
        .command_bits = 0,
        .address_bits = 0,
        .mode = 0,
        .queue_size = 10,
        .clock_speed_hz = 1 * 1000 * 1000,
        .spics_io_num = CS
    };
    spi_device_handle_t handle;
    err = spi_bus_add_device(SPI2_HOST, &max_2769_config, &handle);

    struct Configuration1 conf1;
    struct Configuration2 conf2;
    struct Configuration3 conf3;

    init_configuration1(&conf1);
    init_configuration2(&conf2);
    init_configuration3(&conf3);

    conf3.STRMCOUNT = 0b000;
    conf3.STRMEN = 0b1;
    conf3.ADCEN = 0b1;
    conf3.STRMBITS = 0b0;
    conf3.STAMPEN = 0b0;
    conf3.TIMESYNCEN = 0b0;
    conf3.STRMSTART = 0b1;
    conf3.DATASYNCEN = 0b1;
    // // Now try writing to it?
    setup_max2769(handle);
    max2769_write(handle, MAX2769_CONF3, encode_configuration3(&conf3));
    while (1) {
        read_max2(&output);
        // yield();
    }
}

void print_task_main(void) {
    while(1) {
        while (output.current_read_buf > output.current_write_buf) {
            vTaskDelay(1);
        }
        fwrite(output.output_buf[output.current_read_buf % OUTPUT_BUF_COUNT], sizeof(uint8_t), OUTPUT_BUF_SIZE, stdout);
        // Ideally we should flush lol
        // print_hex(output.output_buf[output.current_read_buf % OUTPUT_BUF_COUNT], OUTPUT_BUF_SIZE);
        output.current_read_buf++;
        vTaskDelay(1);
    }
}

#define STACK_SIZE  8192

void app_main() {
    output.current_read_buf = 0;
    output.current_write_buf = 0;

    init_gpio();

    static const uint16_t cdc_desc_config_len = TUD_CONFIG_DESC_LEN + CFG_TUD_CDC * TUD_CDC_DESC_LEN;
    static const uint8_t cdc_desc_configuration[] = {
        TUD_CONFIG_DESCRIPTOR(1, 4, 0, cdc_desc_config_len, TUSB_DESC_CONFIG_ATT_REMOTE_WAKEUP, 100),
        TUD_CDC_DESCRIPTOR(0, 4, 0x81, 8, 0x02, 0x82, (TUD_OPT_HIGH_SPEED ? 512 : 64)),
        TUD_CDC_DESCRIPTOR(2, 4, 0x83, 8, 0x04, 0x84, (TUD_OPT_HIGH_SPEED ? 512 : 64)),
    };

    tinyusb_config_t tusb_cfg = TINYUSB_DEFAULT_CONFIG();

    tusb_cfg.descriptor.device = &cdc_device_descriptor;
    tusb_cfg.descriptor.full_speed_config = cdc_desc_configuration;
    #if (TUD_OPT_HIGH_SPEED)
    tusb_cfg.descriptor.qualifier = &device_qualifier;
    tusb_cfg.descriptor.high_speed_config = cdc_desc_configuration;
#endif // TUD_OPT_HIGH_SPEED

    tinyusb_config_cdcacm_t acm_cfg = {
        .cdc_port = TINYUSB_CDC_ACM_0,
        .callback_rx = &tinyusb_cdc_rx_callback,
        .callback_rx_wanted_char = NULL,
        .callback_line_state_changed = NULL,
        .callback_line_coding_changed = NULL
    };
    tinyusb_driver_install(&tusb_cfg);

    // Init CDC 0
    tinyusb_cdcacm_initialized(TINYUSB_CDC_ACM_0);
    tinyusb_cdcacm_init(&acm_cfg);
    tinyusb_cdcacm_initialized(TINYUSB_CDC_ACM_0);

    // StaticTask_t max_read_task;
    // static unsigned char max_read_stack[STACK_SIZE];
    // xTaskCreateStaticPinnedToCore(((TaskFunction_t) max_read_main), "max_read", STACK_SIZE, NULL, tskIDLE_PRIORITY + 0xF, max_read_stack, &max_read_task, 0);


    // StaticTask_t print_task;
    // static unsigned char print_task_stack[STACK_SIZE];
    // xTaskCreateStaticPinnedToCore(((TaskFunction_t) print_task_main), "print_task", STACK_SIZE, NULL, tskIDLE_PRIORITY + 0xF, print_task_stack, &print_task, 1);

    while (1) {
        vTaskDelay(1);
        printf("Hello testing");
    }
}
