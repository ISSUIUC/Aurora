#include "MAX2769.h"

bool setup_max2769(spi_device_handle_t handle) {
    struct Configuration1 conf1;
    struct Configuration2 conf2;
    struct Configuration3 conf3;

    init_configuration1(&conf1);
    init_configuration2(&conf2);
    init_configuration3(&conf3);
    conf2.IQEN = 0;
    conf2.FORMAT = 0b10;
    conf2.BITS = 0b100;
    conf3.STRMCOUNT = 0b000;
    conf3.STRMEN = 0b1;
    conf3.STAMPEN = 0b1;
    conf3.TIMESYNCEN = 0b0;
    conf3.DATASYNCEN = 0b0;

    spi_device_acquire_bus(handle, portMAX_DELAY);

    max2769_write(handle, MAX2769_CONF1, encode_configuration1(&conf1));
    max2769_write(handle, MAX2769_CONF2, encode_configuration2(&conf2));
    max2769_write(handle, MAX2769_CONF3, encode_configuration3(&conf3));

    spi_device_release_bus(handle);
    return true;
}


/**
 * Assumes bus has been acquired. You will need to acquire and free the bus
 * 
 * @param handle the spi device handle to write to
 * @param data the 32 bit value to write to the max
 */
esp_err_t max2769_write(spi_device_handle_t handle, uint8_t register_id, uint32_t data) {
    spi_transaction_t t = {
        .cmd = 0,
        .flags = SPI_TRANS_USE_TXDATA | SPI_TRANS_USE_RXDATA,
        .user = NULL,
        .tx_data = {(data >> 8) & 0xFF, (data >> 4) & 0xFF, data & 0xFF, register_id},
        .length = 32
    };

    esp_err_t err = spi_device_polling_transmit(handle, &t);
    if (err != ESP_OK) {
        return err;
    }

    return ESP_OK;
}


void init_configuration1(struct Configuration1* config) {
    config->CHIPEN = 1;
    config->IDLE = 0;
    config->ILNA1 = 0b1000;
    config->ILNA2 = 0b10;
    config->ILO = 0b10;
    config->IMIX = 0b01;
    config->MIXPOLE = 0;
    config->LNAMODE = 0b00;
    config->MIXEN = 1;
    config->ANTEN = 1;
    config->FCEN = 0b00110;
    config->FBW = 0b00;
    config->F3OR5 = 0;
    config->FCENX = 1;
    config->FGAIN = 1;
}

uint32_t encode_configuration1(const struct Configuration1* config) {
    return (config->CHIPEN << 27)
        | (config->IDLE << 26)
        | (config->ILNA1 << 22)
        | (config->ILNA2 << 20)
        | (config->ILO << 18)
        | (config->IMIX << 16)
        | (config->MIXPOLE << 15)
        | (config->LNAMODE << 13)
        | (config->MIXEN << 12) 
        | (config->ANTEN << 11)
        | (config->FCEN << 5)
        | (config->FBW << 3)
        | (config->F3OR5 << 2)
        | (config->FCENX << 1)
        | (config->FGAIN << 0);

}

void init_configuration2(struct Configuration2 *config) {
    config->IQEN = 0;
    config->GAINREF = 170;
    config->AGCMODE = 0b00;
    config->FORMAT = 0b01;
    config->BITS = 0b010;
    config->DRVCFG = 0b00;
    config->LOEN = 1;
}

uint32_t encode_configuration2(const struct Configuration2 *config) {
        return (config->IQEN << 27)
        | (config->GAINREF << 15)
        | (config->AGCMODE << 11)
        | (config->FORMAT << 9)
        | (config->BITS << 6)
        | (config->DRVCFG << 4)
        | (config->LOEN << 3);
}

void init_configuration3(struct Configuration3* config) {
    config->GAININ = 0b111010;
    config->FSLOWEN = 1;
    config->HILOADEN = 0;
    config->ADCEN = 1;
    config->DRVEN = 1;
    config->FOFSTEN = 1;
    config->FILTEN = 1;
    config->FHIPEN = 1;
    config->PGAQEN = 0;
    config->PGAIEN = 1;
    config->STRMEN = 0;
    config->STRMSTART = 0;
    config->STRMSTOP = 0;
    config->STRMCOUNT = 0b111;
    config->STRMBITS = 0b01;
    config->STAMPEN = 1;
    config->TIMESYNCEN = 1;
    config->DATASYNCEN = 0;
    config->SSTRMRST = 0;
}

uint32_t encode_configuration3(const struct Configuration3* config) {
    return (config->GAININ << 22)
    | (config->FSLOWEN << 21)
    | (config->HILOADEN << 20)
    | (config->ADCEN << 19)
    | (config->DRVEN << 18)
    | (config->FOFSTEN << 17)
    | (config->FILTEN << 16)
    | (config->FHIPEN << 15)
    | (1 << 14)
    | (config->PGAIEN << 13)
    | (config->PGAQEN << 12)
    | (config->STRMEN << 11)
    | (config->STRMSTART << 10)
    | (config->STRMSTOP << 9)
    | (config->STRMCOUNT << 6)
    | (config->STRMBITS << 4)
    | (config->STAMPEN << 3)
    | (config->TIMESYNCEN << 2)
    | (config->DATASYNCEN << 1)
    | (config->SSTRMRST << 0);
}


void init_pllconfiguration(struct PLLConfiguration* config) {
    config->VCOEN = 1;
    config->IVCO = 0;
    config->REFOUTEN = 1;
    config->REFDIV = 0b11;
    config->IXTAL = 0b01;
    config->XTALCAP = 0b10000;
    config->LDMUX = 0b0000;
    config->ICP = 0;
    config->PFDEN = 0;
    config->CPTEST = 0b000;
    config->INT_PLL = 1;
    config->PWRSAV = 0;
}

uint32_t encode_pllconfiguration(const struct PLLConfiguration* config) {
        return (config->VCOEN << 27)
        | (config->IVCO << 26)
        | (config->REFOUTEN << 24)
        | (1 << 23)
        | (config->REFDIV << 21)
        | (config->IXTAL << 19)
        | (config->XTALCAP << 14)
        | (config->LDMUX << 10)
        | (config->ICP << 9)
        | (config->PFDEN << 8)
        | (config->CPTEST << 4)
        | (config->INT_PLL << 3);
}

void init_pllintegerdivisionratio(struct PLLIntegerDivisionRatio* config) {
    config->NDIV = 1536;
    config->RDIV = 16;
}

uint32_t encode_pllintegerdivisionratio(const struct PLLIntegerDivisionRatio* config) {
    return (config->NDIV << 13) | (config->RDIV << 3);
}

void init_plldivisionratio(struct PLLDivisionRatio* config) {
    config->FDIV = 0x80000;
}

uint32_t encode_plldivisionratio(const struct PLLDivisionRatio* config) {
    return (config->FDIV << 8) | (0b01110000);
}

void init_dspinterface(struct DSPInterface* config) {
    config->FRAMECOUNT = 0x8000000;
}

uint32_t encode_dspinterface(const struct DSPInterface* config) {
    return config->FRAMECOUNT;
}

void init_clockfractionaldivisionratio(struct ClockFractionalDivisionRatio* config) {
    config->L_CNT = 256;
    config->M_CNT = 1563;
    config->FCLKIN = 0;
    config->ADCCLK = 0;
    config->SERCLK = 1;
    config->MODE = 0;
}

uint32_t encode_clockfractionaldivisionratio(const struct ClockFractionalDivisionRatio* config) {
    return (config->L_CNT << 16)
    | (config->M_CNT << 4)
    | (config->FCLKIN << 3)
    | (config->ADCCLK << 2)
    | (config->SERCLK << 1)
    | (config->MODE << 0);
}


uint32_t TestMode1() {
    return 0x1E0F401;
}

uint32_t TestMode2() {
    return 0x14C0402;
}
