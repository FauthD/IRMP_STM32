/*
 *  A solution to display stus with neopixel leds
 *
 *  Copyright (C) 2024 Dieter Fauth
 *
 *  This program is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; either version 2 of the License, or
 *  (at your option) any later version.
 */

#define HW_TRACE 1

#include <stdio.h>
#include <stdlib.h>

#include "pico/stdlib.h"
#include "hardware/pio.h"
#include "hardware/clocks.h"
#include "hardware/gpio.h"
#include "hardware/sync.h"
#include "ws2812.pio.h"
#include "config.h"
#include "write_neopixel.h"
#include "hw_trace.h"

#define IS_RGBW false

/*
Hint:
The PIO Fifo is 8 entries long. This is sufficient to load 8 leds without much delay (~ 1.2 uSec).
For longer led chains, you must expext an extra 30uSec per led. Or even 40 uSec for RGBW leds.
*/

// FIXME: Either need to close IRQs or use DMA here
// Reason: If an IRQ takes longer that the amount of bits send out,
// we get wrong LED setup.
// For now I limit to 8 pixels
void WriteNeopixel(int len, unsigned long *buf)
{
	HW_Trace1_H();
	uint32_t status = save_and_disable_interrupts();
	for (int n=0; n<len; n++)
	{
		pio_sm_put_blocking(pio0, 0, buf[n]);
	}
	restore_interrupts(status);
	HW_Trace1_L();
}

// FIXME: Either need to close IRQs or use DMA here
// Turn off all pixels
void ResetNeopixel(int len)
{
	HW_Trace2_H();
	uint32_t status = save_and_disable_interrupts();
	for (int n=0; n<len; n++)
	{
		pio_sm_put_blocking(pio0, 0, 0);
	}
	restore_interrupts(status);
	HW_Trace2_L();
}

static void DemoSweep(uint8_t r, uint8_t g, uint8_t b);

void InitNeopixel(int len, bool is_rgbw)
{
	HW_Trace_Init();

	// todo get free sm
	PIO pio = pio0;
	int sm = 0;
	uint offset = pio_add_program(pio, &ws2812_program);
	ws2812_program_init(pio, sm, offset, WS2812_PIN, 800000, is_rgbw);

	ResetNeopixel(len);
	
	DemoSweep(150,5,5);
}

///////////////////////////////////////////////////////////////////////////////
// Below is just a demo
// Will probably be removed when I have written the host side code
#define NUM_PIXELS 8
static uint32_t Pixels[NUM_PIXELS+1];

static void show(void)
{
	HW_Trace2_H();
	for (int n=0; n<NUM_PIXELS; n++)
	{
		pio_sm_put_blocking(pio0, 0, Pixels[n]);
	}
	HW_Trace2_L();
}

static inline uint32_t urgb_u32(uint8_t r, uint8_t g, uint8_t b) {
    return
            ((uint32_t) (r) << 8) |
            ((uint32_t) (g) << 16) |
            (uint32_t) (b);
}

static void setPixelColor(int n, uint8_t r, uint8_t g, uint8_t b)
{
	if(n>=0 && n<NUM_PIXELS)
	{
		Pixels[n] = urgb_u32(r,g,b) << 8u;
	}
}

static void setDarkPixelColor(int n, uint8_t r, uint8_t g, uint8_t b)
{
	setPixelColor(n, r/8,g/8,b/8);
}

static void DemoSweep(uint8_t r, uint8_t g, uint8_t b)
{
	int time=50;

	for (int n=0; n<NUM_PIXELS; n++)
	{
		setPixelColor(n, r,g,b);
		setDarkPixelColor(n+1, r,g,b);
		setDarkPixelColor(n-1, r,g,b);
		show();
		sleep_ms(time);
		setPixelColor(n, 0,0,0);
		setPixelColor(n-1, 0,0,0);
	}

	for(int n=NUM_PIXELS-1; n>=0; n--)
	{
		setPixelColor(n, r,g,b);
		setDarkPixelColor(n-1, r,g,b);
		setDarkPixelColor(n+1, r,g,b);
		show();
		sleep_ms(time);
		setPixelColor(n, 0,0,0);
		setPixelColor(n+1, 0,0,0);
	}

	setPixelColor(0, 0,0,0);
	show();
}
