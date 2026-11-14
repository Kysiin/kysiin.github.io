#include "capture.h"
#include <GL/gl.h>
#include <cstdio>
#include <cstdlib>
#include <vector>

bool captureTGA(const char* path, int width, int height) {
    if (width <= 0 || height <= 0) return false;
    std::vector<unsigned char> rgb((size_t)width * height * 3);
    glPixelStorei(GL_PACK_ALIGNMENT, 1);
    glReadPixels(0, 0, width, height, GL_RGB, GL_UNSIGNED_BYTE, rgb.data());

    std::vector<unsigned char> bgr(rgb.size());
    for (size_t i = 0; i < rgb.size(); i += 3) {
        bgr[i + 0] = rgb[i + 2];
        bgr[i + 1] = rgb[i + 1];
        bgr[i + 2] = rgb[i + 0];
    }

    unsigned char header[18] = {0};
    header[2] = 2;  // uncompressed true-color
    header[12] = (unsigned char)(width & 0xFF);
    header[13] = (unsigned char)((width >> 8) & 0xFF);
    header[14] = (unsigned char)(height & 0xFF);
    header[15] = (unsigned char)((height >> 8) & 0xFF);
    header[16] = 24;
    header[17] = 0x00;  // bottom-left origin

    FILE* f = fopen(path, "wb");
    if (!f) return false;
    fwrite(header, 1, 18, f);
    fwrite(bgr.data(), 1, bgr.size(), f);
    fclose(f);
    return true;
}

