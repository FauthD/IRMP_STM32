/*
 *  Using GPIO pins to trace what the code is doing and measure timing with 
 *  an oscilloscope 
 *  Very usefull if you need to debug external signals togther with internal behavior.
 *  Have been using this method already in the 198x years.

 *  Copyright (C) 2024 Dieter Fauth
 *
 *  This program is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; either version 2 of the License, or
 *  (at your option) any later version.
 */
#ifdef HW_TRACE

#ifndef HW_TRACE1_PIN
#define HW_TRACE1_PIN 3
#endif

#ifndef HW_TRACE2_PIN
#define HW_TRACE2_PIN 4
#endif

__inline static void HW_Trace1_Init()
{
    gpio_init(HW_TRACE1_PIN);
    gpio_set_dir(HW_TRACE1_PIN, GPIO_OUT);
}

__inline static void HW_Trace1_H()
{
    gpio_put(HW_TRACE1_PIN, 1);
}

__inline static void HW_Trace1_L()
{
    gpio_put(HW_TRACE1_PIN, 0);
}

__inline static void HW_Trace1_PH()
{
    HW_Trace1_H();
    HW_Trace1_L();
}

__inline static void HW_Trace1_PL()
{
    HW_Trace1_L();
    HW_Trace1_H();
}

__inline static void 	HW_Trace2_Init()
{
    gpio_init(HW_TRACE2_PIN);
    gpio_set_dir(HW_TRACE2_PIN, GPIO_OUT);
}

__inline static void HW_Trace2_H()
{
    gpio_put(HW_TRACE2_PIN, 1);
}

__inline static void HW_Trace2_L()
{
    gpio_put(HW_TRACE2_PIN, 0);
}

__inline static void HW_Trace2_PH()
{
    HW_Trace2_H();
    HW_Trace2_L();
}

__inline static void HW_Trace2_PL()
{
    HW_Trace2_L();
    HW_Trace2_H();
}

static void HW_Trace_Init()
{
	HW_Trace1_Init();
	HW_Trace2_Init();
}

#else
__inline static void HW_Trace1_Init() {}
__inline static void HW_Trace1_H() {}
__inline static void HW_Trace1_L() {}
__inline static void HW_Trace1_PH() {}
__inline static void HW_Trace1_PL() {}

__inline static void HW_Trace2_Init() {}
__inline static void HW_Trace2_H() {}
__inline static void HW_Trace2_L() {}
__inline static void HW_Trace2_PH() {}
__inline static void HW_Trace2_PL() {}

static void HW_Trace_Init() {}
#endif