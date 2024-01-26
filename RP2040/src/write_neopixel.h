
void InitNeopixel(int len, bool is_rgbw);
void ResetNeopixel(int len);
void WriteNeopixel(int len, unsigned long *buf);

// The HID report could carry 14, but then we need to implement DMA.
// With 8 all fits into the fifo to the PIO.
#define MAX_NEOPIXEL 8
