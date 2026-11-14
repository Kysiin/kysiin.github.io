#include "scene.h"
#include <cmath>

static const std::vector<SceneDef> kScenes = {
    {"flag", "Flag in the wind"},
    {"drape", "Cloth draping over a sphere"},
    {"table", "Tablecloth on a box"},
    {"tear", "Tearing cloth"},
    {"spheres", "Cloth over two spheres"},
    {"slide", "Friction on a 30 deg slope"},
};

const std::vector<SceneDef>& sceneList() { return kScenes; }

static void pinColumn(Cloth& c, int j) {
    for (int i = 0; i < c.par.ny; ++i) c.pinned[c.idx(i, j)] = 1;
}

bool buildScene(const std::string& id, Cloth& cloth, std::vector<Collider>& cols,
                Camera& cam, std::string& title) {
    cloth = Cloth();
    cols.clear();
    cam = Camera();

    if (id == "flag") {
        cloth.build(51, 31, 1.4f, 0.9f, Vec3(-0.7f, 0.10f, 0.0f), Vec3(1, 0, 0), Vec3(0, 1, 0));
        pinColumn(cloth, 0);
        cloth.par.windDir = Vec3(1, 0, 0.15f);
        cloth.par.windStrength = 9.0f;
        cloth.par.turbulence = 2.2f;
        cam.target = Vec3(0.10f, 0.50f, 0.10f);
        cam.yaw = 0.22f; cam.pitch = 0.13f; cam.dist = 3.0f;
        title = kScenes[0].title;
    } else if (id == "drape") {
        cloth.build(41, 41, 1.3f, 1.3f, Vec3(-0.65f, 1.30f, -0.65f), Vec3(1, 0, 0), Vec3(0, 0, 1));
        cols.push_back(Collider::sphere(Vec3(0.0f, 0.42f, 0.0f), 0.40f));
        cols.push_back(Collider::plane(Vec3(0, 1, 0), 0.0f));
        cam.target = Vec3(0.0f, 0.55f, 0.0f);
        cam.yaw = 0.65f; cam.pitch = 0.22f; cam.dist = 3.2f;
        title = kScenes[1].title;
    } else if (id == "table") {
        cloth.build(51, 51, 1.7f, 1.7f, Vec3(-0.85f, 0.92f, -0.85f), Vec3(1, 0, 0), Vec3(0, 0, 1));
        cols.push_back(Collider::box(Vec3(0.0f, 0.34f, 0.0f), Vec3(0.50f, 0.34f, 0.50f)));
        cols.push_back(Collider::plane(Vec3(0, 1, 0), 0.0f));
        cam.target = Vec3(0.0f, 0.5f, 0.0f);
        cam.yaw = 0.62f; cam.pitch = 0.20f; cam.dist = 3.3f;
        title = kScenes[2].title;
    } else if (id == "tear") {
        cloth.build(41, 41, 1.2f, 1.2f, Vec3(-0.6f, 0.10f, 0.0f), Vec3(1, 0, 0), Vec3(0, 1, 0));
        pinColumn(cloth, 0);
        cloth.par.windDir = Vec3(0, 0, 1);
        cloth.par.windStrength = 12.0f;
        cloth.par.turbulence = 1.6f;
        cloth.par.tearRatio = 1.10f;
        cam.target = Vec3(0.0f, 0.62f, 0.35f);
        cam.yaw = 0.50f; cam.pitch = 0.16f; cam.dist = 3.1f;
        title = kScenes[3].title;
    } else if (id == "spheres") {
        cloth.build(51, 51, 1.5f, 1.5f, Vec3(-0.75f, 1.15f, -0.75f), Vec3(1, 0, 0), Vec3(0, 0, 1));
        cols.push_back(Collider::sphere(Vec3(-0.33f, 0.30f, 0.0f), 0.28f));
        cols.push_back(Collider::sphere(Vec3(0.33f, 0.30f, 0.0f), 0.28f));
        cols.push_back(Collider::plane(Vec3(0, 1, 0), 0.0f));
        cam.target = Vec3(0.0f, 0.5f, 0.0f);
        cam.yaw = 0.75f; cam.pitch = 0.24f; cam.dist = 3.3f;
        title = kScenes[4].title;
    } else if (id == "slide") {
        const float a = 3.14159265f / 6.0f;
        Vec3 n(std::sin(a), std::cos(a), 0.0f);
        Vec3 u(std::cos(a), -std::sin(a), 0.0f);
        Vec3 v(0, 0, 1);
        Vec3 center = n * 0.55f;
        Vec3 origin = center - u * 0.6f - v * 0.6f;
        cloth.build(31, 31, 1.2f, 1.2f, origin, u, v);
        cols.push_back(Collider::plane(n, 0.0f));
        cam.target = Vec3(0.0f, 0.25f, 0.0f);
        cam.yaw = 0.30f; cam.pitch = 0.32f; cam.dist = 3.4f;
        title = kScenes[5].title;
    } else {
        return false;
    }
    cloth.reset();
    return true;
}





