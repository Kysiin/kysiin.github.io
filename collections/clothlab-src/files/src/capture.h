// capture.h - framebuffer capture to TGA (no external image library)
#pragma once

// Reads the current back buffer and writes an uncompressed 24-bit TGA.
bool captureTGA(const char* path, int width, int height);
