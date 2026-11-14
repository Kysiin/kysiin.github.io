#include "hud.h"
#include <windows.h>
#include <GL/gl.h>
#include <cstdarg>
#include <cstring>
#include <cstdio>
#include <vector>

bool Hud::init() {
    atlasW_ = 256;
    atlasH_ = 96;
    BITMAPINFO bmi = {};
    bmi.bmiHeader.biSize = sizeof(BITMAPINFOHEADER);
    bmi.bmiHeader.biWidth = atlasW_;
    bmi.bmiHeader.biHeight = -atlasH_;  // top-down
    bmi.bmiHeader.biPlanes = 1;
    bmi.bmiHeader.biBitCount = 32;
    bmi.bmiHeader.biCompression = BI_RGB;

    HDC screen = CreateCompatibleDC(nullptr);
    void* bits = nullptr;
    HBITMAP bmp = CreateDIBSection(screen, &bmi, DIB_RGB_COLORS, &bits, nullptr, 0);
    if (!bmp || !bits) { DeleteDC(screen); return false; }
    HGDIOBJ oldBmp = SelectObject(screen, bmp);
    std::memset(bits, 0, (size_t)atlasW_ * atlasH_ * 4);

    HFONT font = CreateFontA(-15, 0, 0, 0, FW_NORMAL, 0, 0, 0, DEFAULT_CHARSET,
                             OUT_TT_PRECIS, CLIP_DEFAULT_PRECIS, ANTIALIASED_QUALITY,
                             FF_DONTCARE, "Consolas");
    if (!font) font = (HFONT)GetStockObject(ANSI_FIXED_FONT);
    HGDIOBJ oldFont = SelectObject(screen, font);
    SetBkMode(screen, TRANSPARENT);
    SetTextColor(screen, RGB(255, 255, 255));
    for (int c = 32; c < 128; ++c) {
        int cell = c - 32;
        int cx = (cell % 16) * 16;
        int cy = (cell / 16) * 16;
        char ch[2] = {(char)c, 0};
        TextOutA(screen, cx + 1, cy, ch, 1);
    }
    SelectObject(screen, oldFont);
    DeleteObject(font);

    // BGRA -> RGBA (white glyph, alpha from luminance), flipped so v=0 is the bottom row.
    std::vector<unsigned char> rgba((size_t)atlasW_ * atlasH_ * 4);
    const unsigned char* src = (const unsigned char*)bits;
    for (int y = 0; y < atlasH_; ++y) {
        for (int x = 0; x < atlasW_; ++x) {
            const unsigned char* p = src + ((size_t)y * atlasW_ + x) * 4;
            unsigned char a = p[0] > p[1] ? (p[0] > p[2] ? p[0] : p[2])
                                          : (p[1] > p[2] ? p[1] : p[2]);
            size_t dst = ((size_t)(atlasH_ - 1 - y) * atlasW_ + x) * 4;
            rgba[dst + 0] = 255;
            rgba[dst + 1] = 255;
            rgba[dst + 2] = 255;
            rgba[dst + 3] = a;
        }
    }
    if (const char* dumpPath = getenv("CLOTH_DUMP_FONT")) {
        FILE* f = fopen(dumpPath, "wb");
        if (f) {
            unsigned char hdr[18] = {0};
            hdr[2] = 2; hdr[12] = (unsigned char)(atlasW_ & 0xFF); hdr[13] = (unsigned char)(atlasW_ >> 8);
            hdr[14] = (unsigned char)(atlasH_ & 0xFF); hdr[15] = (unsigned char)(atlasH_ >> 8);
            hdr[16] = 24; hdr[17] = 0;
            fwrite(hdr, 1, 18, f);
            for (int y = 0; y < atlasH_; ++y) {
                for (int x = 0; x < atlasW_; ++x) {
                    size_t i = ((size_t)y * atlasW_ + x) * 4;
                    unsigned char bgr[3] = {rgba[i + 3], rgba[i + 3], rgba[i + 3]};
                    fwrite(bgr, 1, 3, f);
                }
            }
            fclose(f);
        }
    }
    glGenTextures(1, &tex_);
    glBindTexture(GL_TEXTURE_2D, tex_);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP);
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, atlasW_, atlasH_, 0, GL_RGBA,
                 GL_UNSIGNED_BYTE, rgba.data());

    SelectObject(screen, oldBmp);
    DeleteObject(bmp);
    DeleteDC(screen);
    return true;
}

void Hud::shutdown() {
    if (tex_) { glDeleteTextures(1, &tex_); tex_ = 0; }
}

void Hud::begin(int w, int h) {
    glMatrixMode(GL_PROJECTION);
    glPushMatrix();
    glLoadIdentity();
    glOrtho(0, w, h, 0, -1, 1);
    glMatrixMode(GL_MODELVIEW);
    glPushMatrix();
    glLoadIdentity();
    glDisable(GL_DEPTH_TEST);
    glDisable(GL_LIGHTING);
    glEnable(GL_BLEND);
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
    glEnable(GL_TEXTURE_2D);
    glBindTexture(GL_TEXTURE_2D, tex_);
    glColor4f(1, 1, 1, 1);
}

void Hud::end() {
    glDisable(GL_TEXTURE_2D);
    glDisable(GL_BLEND);
    glEnable(GL_DEPTH_TEST);
    glMatrixMode(GL_PROJECTION);
    glPopMatrix();
    glMatrixMode(GL_MODELVIEW);
    glPopMatrix();
}

void Hud::text(float x, float y, float scale, const char* s, const Vec3& color) {
    if (!s) return;
    glColor4f(color.x, color.y, color.z, 1.0f);
    float cw = kCell / atlasW_;
    float ch = kCell / atlasH_;
    glBegin(GL_QUADS);
    for (const char* p = s; *p; ++p) {
        int c = (unsigned char)*p;
        if (c < 32 || c >= 128) { x += kAdvance * scale; continue; }
        int cell = c - 32;
        float padU = 1.0f / atlasW_;
        float padV = 1.5f / atlasH_;
        float u0 = (cell % 16) * cw + padU;
        float v1 = 1.0f - (cell / 16) * ch - padV;
        float u1 = u0 + kGlyphW / atlasW_ - padU;
        float v0 = 1.0f - (cell / 16) * ch - ch + padV;
        float x1 = x + kGlyphW * scale;
        float y1 = y + kCell * scale;
        glTexCoord2f(u0, v1); glVertex2f(x, y);
        glTexCoord2f(u1, v1); glVertex2f(x1, y);
        glTexCoord2f(u1, v0); glVertex2f(x1, y1);
        glTexCoord2f(u0, v0); glVertex2f(x, y1);
        x += kAdvance * scale;
    }
    glEnd();
}

void Hud::textf(float x, float y, float scale, const Vec3& color, const char* fmt, ...) {
    char buf[512];
    va_list ap;
    va_start(ap, fmt);
    vsnprintf(buf, sizeof(buf), fmt, ap);
    va_end(ap);
    text(x, y, scale, buf, color);
}

float Hud::width(const char* s, float scale) const {
    return s ? (float)strlen(s) * kAdvance * scale : 0.0f;
}

void Hud::rect(float x, float y, float w, float h, const Vec3& color, float alpha) {
    glDisable(GL_TEXTURE_2D);
    glColor4f(color.x, color.y, color.z, alpha);
    glBegin(GL_QUADS);
    glVertex2f(x, y); glVertex2f(x + w, y); glVertex2f(x + w, y + h); glVertex2f(x, y + h);
    glEnd();
    glEnable(GL_TEXTURE_2D);
}

void Hud::rectOutline(float x, float y, float w, float h, const Vec3& color, float alpha) {
    glDisable(GL_TEXTURE_2D);
    glColor4f(color.x, color.y, color.z, alpha);
    glBegin(GL_LINE_LOOP);
    glVertex2f(x, y); glVertex2f(x + w, y); glVertex2f(x + w, y + h); glVertex2f(x, y + h);
    glEnd();
    glEnable(GL_TEXTURE_2D);
}







