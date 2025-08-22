#ifndef MAX2769_H
#define MAX2769_H

#include <stdint.h>
#include "driver/spi_master.h"

#define MAX2769_CONF1 0
#define MAX2769_CONF2 2
#define MAX2769_CONF3 2
#define MAX2769_PLLCONF 3
#define MAX2769_DIV 4
#define MAX2769_FDIV 5
#define MAX2769_STRM 6
#define MAX2769_CLK 7
#define MAX2769_TEST1 8
#define MAX2769_TEST2 9

struct Configuration1 {
    uint32_t CHIPEN;
    uint32_t IDLE;
    uint32_t ILNA1;
    uint32_t ILNA2;
    uint32_t ILO;
    uint32_t IMIX;
    uint32_t MIXPOLE;
    uint32_t LNAMODE;
    uint32_t MIXEN;
    uint32_t ANTEN;
    uint32_t FCEN;
    uint32_t FBW;
    uint32_t F3OR5;
    uint32_t FCENX;
    uint32_t FGAIN;
};

struct Configuration2 {
    uint32_t IQEN;
    uint32_t GAINREF;
    uint32_t AGCMODE;
    uint32_t FORMAT;
    uint32_t BITS;
    uint32_t DRVCFG;
    uint32_t LOEN;
};
struct Configuration3 {
    uint32_t GAININ;
    uint32_t FSLOWEN;
    uint32_t HILOADEN;
    uint32_t ADCEN;
    uint32_t DRVEN;
    uint32_t FOFSTEN;
    uint32_t FILTEN;
    uint32_t FHIPEN;
    uint32_t PGAQEN;
    uint32_t PGAIEN;
    uint32_t STRMEN;
    uint32_t STRMSTART;
    uint32_t STRMSTOP;
    uint32_t STRMCOUNT;
    uint32_t STRMBITS;
    uint32_t STAMPEN;
    uint32_t TIMESYNCEN;
    uint32_t DATASYNCEN;
    uint32_t SSTRMRST;
};

struct PLLConfiguration {
    uint32_t VCOEN;
    uint32_t IVCO;
    uint32_t REFOUTEN;
    uint32_t REFDIV;
    uint32_t IXTAL;
    uint32_t XTALCAP;
    uint32_t LDMUX;
    uint32_t ICP;
    uint32_t PFDEN;
    uint32_t CPTEST;
    uint32_t INT_PLL;
    uint32_t PWRSAV;
};

struct PLLIntegerDivisionRatio {
    uint32_t NDIV;
    uint32_t RDIV;
};

struct DSPInterface {
    uint32_t FRAMECOUNT;
};

struct PLLDivisionRatio {
    uint32_t FDIV;
};

struct ClockFractionalDivisionRatio {
    uint32_t L_CNT;
    uint32_t M_CNT;
    uint32_t FCLKIN;
    uint32_t ADCCLK;
    uint32_t SERCLK;
    uint32_t MODE;
};

void init_configuration1(struct Configuration1* config);
uint32_t encode_configuration1(const struct Configuration1* config);
void init_configuration2(struct Configuration2 *config);
uint32_t encode_configuration2(const struct Configuration2 *config);
void init_configuration3(struct Configuration3* config);
uint32_t encode_configuration3(const struct Configuration3* config);
void init_pllconfiguration(struct PLLConfiguration* config);
uint32_t encode_pllconfiguration(const struct PLLConfiguration* config);
void init_pllintegerdivisionratio(struct PLLIntegerDivisionRatio* config);
uint32_t encode_pllintegerdivisionratio(const struct PLLIntegerDivisionRatio* config);
void init_plldivisionratio(struct PLLDivisionRatio* config);
uint32_t encode_plldivisionratio(const struct PLLDivisionRatio* config);
void init_dspinterface(struct DSPInterface* config);
uint32_t encode_dspinterface(const struct DSPInterface* config);
void init_clockfractionaldivisionratio(struct ClockFractionalDivisionRatio* config);
uint32_t encode_clockfractionaldivisionratio(const struct ClockFractionalDivisionRatio* config);
uint32_t TestMode1();
uint32_t TestMode2();


// void setup_max2769() {
//     Configuration1 conf1 = Configuration1();
//     Configuration2 conf2 = Configuration2();
//     Configuration3 conf3 = Configuration3();

//     conf2.IQEN = 0;
//     conf2.FORMAT = 0b10;
//     conf2.BITS = 0b100;
//     conf3.STRMCOUNT = 0b000;
//     conf3.STRMEN = 0b1;
//     conf3.STAMPEN = 0b1;
//     conf3.TIMESYNCEN = 0b0;
//     conf3.DATASYNCEN = 0b0;

//     write_reg(MaxRegister::CONF1,   conf1.encode());
//     write_reg(MaxRegister::CONF2,   conf2.encode());
//     write_reg(MaxRegister::CONF3,   conf3.encode());
//     write_reg(MaxRegister::PLLCONF, PLLConfiguration().encode());
//     write_reg(MaxRegister::DIV,     PLLIntegerDivisionRatio().encode());
//     write_reg(MaxRegister::FDIV,    PLLDivisionRatio().encode());
//     write_reg(MaxRegister::STRM,    DSPInterface().encode());
//     write_reg(MaxRegister::CLK,     ClockFractionalDivisionRatio().encode());
//     write_reg(MaxRegister::TEST1,   TestMode1().encode());
//     write_reg(MaxRegister::TEST2,   TestMode2().encode());
// }

esp_err_t max2769_write(spi_device_handle_t handle, uint8_t register, uint32_t data);
bool setup_max2769(spi_device_handle_t handle);
#endif
