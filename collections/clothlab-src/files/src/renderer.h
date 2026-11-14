// renderer.h - OpenGL 1.1 fixed-pipeline renderer for the cloth scene
#pragma once
#include "math3d.h"
#include "cloth.h"
#include <vector>

struct Camera {
    Vec3 target{0.0f, 0.55f, 0.0f};
    float yaw = 0.55f;    // radians, 0 = looking down -Z
    float pitch = 0.20f;
    float dist = 2.7f;

    Vec3 eye() const {
        return target + Vec3(std::cos(pitch) * std::sin(yaw),
                             std::sin(pitch),
                             std::cos(pitch) * std::cos(yaw)) * dist;
    }
};

struct RenderOptions {
    bool wireframe = false;
    bool showShadow = true;
    bool showGround = true;
    bool showColliders = true;
    bool showClothTexture = true;
};

class Renderer {
public:
    bool init();
    void shutdown();
    void draw(const Cloth& cloth, const std::vector<Collider>& cols, const Camera& cam,
              const RenderOptions& opt, int width, int height);

    static const Vec3 kBgTop;
    static const Vec3 kBgBottom;

private:
    void drawBackground();
    void drawGround();
    void drawColliders(const std::vector<Collider>& cols);
    void drawCloth(const Cloth& cloth, const RenderOptions& opt);
    void drawShadow(const Cloth& cloth);
    void drawSphere(const Vec3& c, float r);

    unsigned clothTex_ = 0, groundTex_ = 0;
    bool ready_ = false;
};
