// hud.h - minimal 2D text/overlay renderer (font atlas built with GDI at startup)
#pragma once
#include "math3d.h"

class Hud {
public:
    bool init();
    void shutdown();

    void begin(int screenW, int screenH);
    void end();

    void text(float x, float y, float scale, const char* s, const Vec3& color);
    void textf(float x, float y, float scale, const Vec3& color, const char* fmt, ...);
    float width(const char* s, float scale) const;
    void rect(float x, float y, float w, float h, const Vec3& color, float alpha);
    void rectOutline(float x, float y, float w, float h, const Vec3& color, float alpha);

    static constexpr float kCell = 16.0f;
    static constexpr float kGlyphW = 10.0f;
    static constexpr float kAdvance = 10.0f;

private:
    unsigned tex_ = 0;
    int atlasW_ = 256, atlasH_ = 96;
};

