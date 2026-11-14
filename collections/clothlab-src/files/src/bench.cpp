#include "bench.h"
#include "cloth.h"
#include "scene.h"

#include <windows.h>
#include <cstdio>
#include <cmath>
#include <string>
#include <vector>

struct Case {
    std::string exp;
    std::string label;
    std::string scene;
    int solver = 0;
    int substeps = 6;
    int iters = 6;
    float k = 1.0f;
    float friction = 0.35f;
    float wind = -1.0f;
    float tear = -1.0f;
    int grid = 0;       // 0 = scene default
    int frames = 240;
};

static double qpcNow(double freq) {
    LARGE_INTEGER t;
    QueryPerformanceCounter(&t);
    return (double)t.QuadPart / freq;
}

struct Row {
    double ms = 0;
    double stretch = 0, meanStretch = 0, pen = 0;
    double contacts = 0, kinetic = 0, overhang = 0;
    int diverged = 0;
};

static Row runCase(const Case& c, double freq) {
    Cloth cloth;
    std::vector<Collider> cols;
    Camera cam;
    std::string title;
    buildScene(c.scene, cloth, cols, cam, title);
    cloth.colliders = cols;

    if (c.grid > 0) {
        cloth.build(c.grid, c.grid, 1.3f, 1.3f, Vec3(-0.65f, 1.30f, -0.65f),
                    Vec3(1, 0, 0), Vec3(0, 0, 1));
        cloth.reset();
    }

    cloth.par.solver = c.solver;
    cloth.par.substeps = c.substeps;
    cloth.par.iterations = c.iters;
    cloth.par.stiffness[0] = c.k;
    cloth.par.friction = c.friction;
    if (c.wind >= 0.0f) cloth.par.windStrength = c.wind;
    if (c.tear >= 0.0f) cloth.par.tearRatio = c.tear;

    const int warmup = 60;
    for (int f = 0; f < warmup; ++f) cloth.step(1.0f / 60.0f);

    const bool isSlide = (c.scene == "slide");
    Vec3 mean0(0, 0, 0);
    for (size_t i = 0; i < cloth.pos.size(); ++i) mean0 += cloth.pos[i];
    mean0 = mean0 / (float)std::max<size_t>(1, cloth.pos.size());

    Row r;
    int measured = 0;
    double t0 = qpcNow(freq);
    double maxOverhang = 0.0;
    for (int f = 0; f < c.frames; ++f) {
        cloth.step(1.0f / 60.0f);
        r.stretch += cloth.maxStretch;
        r.meanStretch += cloth.meanStretch;
        r.pen += cloth.maxPenetration;
        r.contacts += cloth.contactCount;
        ++measured;
        if (!std::isfinite(cloth.maxStretch) || cloth.maxStretch > 5.0) r.diverged = 1;
        for (size_t i = 0; i < cloth.pos.size(); ++i) {
            if (!cloth.alive[i]) continue;
            float ax = std::fabs(cloth.pos[i].x);
            if (ax > maxOverhang) maxOverhang = ax;
        }
    }
    double t1 = qpcNow(freq);
    r.ms = (t1 - t0) * 1000.0 / (double)std::max(1, measured);
    r.stretch /= (double)measured;
    r.meanStretch /= (double)measured;
    r.pen /= (double)measured;
    r.contacts /= (double)measured;
    r.kinetic = cloth.kinetic;
    if (isSlide) {
        Vec3 mean1(0, 0, 0);
        for (size_t i = 0; i < cloth.pos.size(); ++i) mean1 += cloth.pos[i];
        mean1 = mean1 / (float)std::max<size_t>(1, cloth.pos.size());
        const float a = 3.14159265f / 6.0f;
        Vec3 u(std::cos(a), -std::sin(a), 0.0f);
        r.overhang = dot(mean1 - mean0, u);
    } else {
        r.overhang = maxOverhang;
    }
    if (cloth.blownUp) r.diverged = 1;
    return r;
}

bool runBench(const std::string& outPath) {
    LARGE_INTEGER f;
    QueryPerformanceFrequency(&f);
    double freq = (double)f.QuadPart;

    std::vector<Case> cases;
    auto add = [&](const char* exp, const std::string& label, const char* scene) {
        Case c;
        c.exp = exp;
        c.label = label;
        c.scene = scene;
        cases.push_back(c);
        return cases.size() - 1;
    };

    // E1: solver stability vs substeps (flag scene)
    for (int s : {2, 4, 6, 8, 12, 16, 24, 32}) {
        size_t i = add("E1_stability", "pbd_sub" + std::to_string(s), "flag");
        cases[i].solver = 0;
        cases[i].substeps = s;
        cases[i].k = 1.0f;
        i = add("E1_stability", "euler_sub" + std::to_string(s), "flag");
        cases[i].solver = 1;
        cases[i].substeps = s;
        cases[i].k = 1.0f;
    }
    // E2: PBD iterations vs stiffness of the cloth (flag scene)
    for (int it : {1, 2, 3, 4, 6, 8, 12, 16, 20}) {
        size_t i = add("E2_iterations", "iter" + std::to_string(it), "flag");
        cases[i].iters = it;
    }
    // E3: substeps vs penetration when draping over a sphere
    for (int s : {1, 2, 3, 4, 6, 8, 12}) {
        size_t i = add("E3_substeps_pen", "sub" + std::to_string(s), "drape");
        cases[i].substeps = s;
        cases[i].frames = 180;
    }
    // E4: friction vs sliding on the table
    for (float mu : {0.0f, 0.1f, 0.2f, 0.3f, 0.5f, 0.7f, 0.9f}) {
        char buf[32];
        snprintf(buf, sizeof(buf), "mu%.2f", mu);
        size_t i = add("E4_friction", buf, "slide");
        cases[i].friction = mu;
        cases[i].frames = 180;
    }
    // E5: grid resolution vs cost (drape scene, square grid)
    for (int n : {21, 31, 41, 51, 61, 71, 81}) {
        size_t i = add("E5_resolution", "n" + std::to_string(n), "drape");
        cases[i].grid = n;
        cases[i].frames = 120;
    }
    // E6: default scenes
    for (const char* sc : {"flag", "drape", "table", "spheres", "tear"}) {
        size_t i = add("E6_scenes", sc, sc);
        cases[i].frames = 180;
    }

    FILE* fp = fopen(outPath.c_str(), "wb");
    if (!fp) return false;
    fprintf(fp, "exp,label,scene,solver,substeps,iters,k,friction,frames,ms_per_frame,"
                "max_stretch,mean_stretch,pen_mm,contacts,kinetic,overhang,diverged\n");

    for (const Case& c : cases) {
        Row r = runCase(c, freq);
        fprintf(fp, "%s,%s,%s,%s,%d,%d,%.3f,%.2f,%d,%.3f,%.5f,%.5f,%.4f,%.1f,%.3f,%.4f,%d\n",
                c.exp.c_str(), c.label.c_str(), c.scene.c_str(),
                c.solver == 0 ? "pbd" : "euler", c.substeps, c.iters, c.k, c.friction,
                c.frames, r.ms, r.stretch, r.meanStretch, r.pen * 1000.0, r.contacts,
                r.kinetic, r.overhang, r.diverged);
        fflush(fp);
        printf("bench %-18s %-12s ms=%7.2f stretch=%.4f pen=%.3fmm div=%d\n",
               c.exp.c_str(), c.label.c_str(), r.ms, r.stretch, r.pen * 1000.0, r.diverged);
    }
    fclose(fp);
    printf("bench written to %s\n", outPath.c_str());
    return true;
}



