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

void app_main(void)
{
    init_gpio();
    gpio_set_level(LED_GREEN, 1);
    spi_bus_config_t max_2769_serial_in = {
        .miso_io_num = -1, // We do not have master in for the MAX 2769
        .mosi_io_num = MOSI,
        .sclk_io_num = SCK,
        .quadwp_io_num = -1,
        .quadhd_io_num = -1,
        .max_transfer_sz = 32,
    };
    printf("Setting");
    fflush(stdout);
    esp_err_t err = spi_bus_initialize(SPI2_HOST, &max_2769_serial_in, SPI_DMA_DISABLED);
    gpio_set_level(LED_BLUE, 1);
    if (err != ESP_OK) {
        gpio_set_level(LED_RED, 1);
    }
    // ESP_ERROR_CHECK(err);
    printf("Setup SPI bus");
    fflush(stdout);
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
    gpio_set_level(LED_ORANGE, 1);

    struct Configuration1 conf1;
    struct Configuration2 conf2;
    struct Configuration3 conf3;

    init_configuration1(&conf1);
    init_configuration2(&conf2);
    init_configuration3(&conf3);

    conf3.STRMCOUNT = 0b000;
    conf3.STRMEN = 0b1;
    conf3.STAMPEN = 0b1;
    conf3.TIMESYNCEN = 0b0;
    conf3.STRMSTART = 0b1;
    conf3.DATASYNCEN = 0b1;
    // // Now try writing to it?
    setup_max2769(handle);
    while (1) {
        // Write strm start
        conf3.STRMEN = 0b1;
        max2769_write(handle, MAX2769_CONF3, encode_configuration3(&conf3));
        //max_read();
        vTaskDelay(500 / portTICK_PERIOD_MS);
    }
}
