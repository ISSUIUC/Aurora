#include "usboutput.h"
#include "tinyusb.h"
#include "tinyusb_cdc_acm.h"
#include "tinyusb_default_config.h"
#include "tinyusb_console.h"



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


static void tinyusb_cdc_rx_callback(int itf, cdcacm_event_t *event)
{
}

void init_usb() {
    static const uint16_t cdc_desc_config_len = TUD_CONFIG_DESC_LEN + CFG_TUD_CDC * TUD_CDC_DESC_LEN;
    static const uint8_t cdc_desc_configuration[] = {
        TUD_CONFIG_DESCRIPTOR(1, 4, 0, cdc_desc_config_len, TUSB_DESC_CONFIG_ATT_REMOTE_WAKEUP, 100),
        TUD_CDC_DESCRIPTOR(0, 4, 0x81, 8, 0x02, 0x82, (TUD_OPT_HIGH_SPEED ? 512 : 64)),
        TUD_CDC_DESCRIPTOR(2, 4, 0x83, 8, 0x04, 0x84, (TUD_OPT_HIGH_SPEED ? 512 : 64)),
    };

    tinyusb_config_t tusb_cfg = TINYUSB_DEFAULT_CONFIG();

    tinyusb_driver_install(&tusb_cfg);

    tinyusb_config_cdcacm_t acm_cfg = {
        .cdc_port = TINYUSB_CDC_ACM_0,
        .callback_rx = &tinyusb_cdc_rx_callback,
        .callback_rx_wanted_char = NULL,
        .callback_line_state_changed = NULL,
        .callback_line_coding_changed = NULL
    };
    // Init CDC 0
    tinyusb_cdcacm_init(&acm_cfg);
    tinyusb_console_init(TINYUSB_CDC_ACM_0);
}

 {
    while(1) {
        while (output.current_read_buf > output.current_write_buf) {
            taskYIELD();
        }
        tud_cdc_n_write(
            TINYUSB_CDC_ACM_0,
            output.output_buf[output.current_read_buf % OUTPUT_BUF_COUNT],
            OUTPUT_BUF_SIZE
        );
        tud_cdc_n_write_flush(TINYUSB_CDC_ACM_0);
        // Ideally we should flush lol
        // print_hex(output.output_buf[output.current_read_buf % OUTPUT_BUF_COUNT], OUTPUT_BUF_SIZE);
        output.current_read_buf++;
        taskYIELD();
    }
}
