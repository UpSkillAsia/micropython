/*
 * This file is part of the MicroPython project, http://micropython.org/
 *
 * The MIT License (MIT)
 *
 * Copyright (c) 2013, 2014 Damien P. George and 2017, 2018 Rami Ali
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */

#ifndef INCLUDED_MPHALPORT_H
#define INCLUDED_MPHALPORT_H

#include "py/obj.h"
#include "shared/runtime/interrupt_char.h"

#define mp_hal_stdin_rx_chr() (0)
void mp_hal_stdout_tx_strn(const char *str, size_t len);

void mp_hal_delay_ms(mp_uint_t ms);
void mp_hal_delay_us(mp_uint_t us);
mp_uint_t mp_hal_ticks_ms(void);
mp_uint_t mp_hal_ticks_us(void);
mp_uint_t mp_hal_ticks_cpu(void);

int mp_hal_get_interrupt_char(void);

// C-level pin HAL
#include "py/obj.h"
#define MP_HAL_PIN_FMT "%u"
#define mp_hal_pin_obj_t int
mp_hal_pin_obj_t machine_pin_get_id(mp_obj_t pin_in);
#define mp_hal_get_pin_obj(o) machine_pin_get_id(o)
#define mp_obj_get_pin(o) machine_pin_get_id(o) // legacy name; only to support esp8266/modonewire
#define mp_hal_pin_name(p) (p)
static inline void mp_hal_pin_input(mp_hal_pin_obj_t pin) {
    /* gpio_pad_select_gpio(pin);
    gpio_set_direction(pin, GPIO_MODE_INPUT); */
}
static inline void mp_hal_pin_output(mp_hal_pin_obj_t pin) {
    /* gpio_pad_select_gpio(pin);
    gpio_set_direction(pin, GPIO_MODE_INPUT_OUTPUT);*/
}
static inline void mp_hal_pin_open_drain(mp_hal_pin_obj_t pin) {
    /*gpio_pad_select_gpio(pin);
    gpio_set_direction(pin, GPIO_MODE_INPUT_OUTPUT_OD);*/
}
static inline void mp_hal_pin_od_low(mp_hal_pin_obj_t pin) {
    // gpio_set_level(pin, 0);
}
static inline void mp_hal_pin_od_high(mp_hal_pin_obj_t pin) {
    // gpio_set_level(pin, 1);
}
static inline int mp_hal_pin_read(mp_hal_pin_obj_t pin) {
    // return gpio_get_level(pin);
    return 0;
}
static inline void mp_hal_pin_write(mp_hal_pin_obj_t pin, int v) {
    // gpio_set_level(pin, v);
}

#endif // INCLUDED_MPHALPORT_H
