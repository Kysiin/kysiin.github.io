// cloth.h - mass-spring cloth with two solvers (PBD/Verlet and explicit Euler)
#pragma once
#include "math3d.h"
#include "collision.h"
#include <vector>
#include <string>
#include <cstdint>

enum SpringType { SPR_STRUCT = 0, SPR_SHEAR = 1, SPR_BEND = 2 };

struct Spring {
    int a = 0, b = 0;
    float rest = 0.0f;
    uint8_t type = SPR_STRUCT;
    bool broken = false;
};

struct ClothParams {
    // geometry / material
    int nx = 41, ny = 41;
    float width = 1.4f, height = 1.4f;
    float mass = 1.0f;
    float thickness = 0.004f;
    float friction = 0.35f;

    // solver
    int solver = 0;                 // 0 = PBD/Verlet, 1 = explicit Euler
    int iterations = 6;             // PBD constraint iterations
    int substeps = 6;               // substeps per frame
    float damping = 0.995f;         // velocity damping per substep
    float stiffness[3] = {1.0f, 0.75f, 0.12f};   // PBD normalized stiffness
    float eulerK[3] = {120000.f, 60000.f, 6000.f}; // N/m for the explicit solver
    float eulerDamp = 120.0f;       // spring damping coefficient

    // environment
    Vec3 gravity{0.0f, -9.8f, 0.0f};
    Vec3 windDir{0.0f, 0.0f, 1.0f};
    float windStrength = 0.0f;      // m/s
    float turbulence = 0.0f;

    // extras
    float tearRatio = 0.0f;         // 0 = tearing disabled
    bool selfCollide = false;
};

class Cloth {
public:
    ClothParams par;
    std::vector<Vec3> pos, prev, vel, restPos, nrm;
    std::vector<Vec3> windAcc;
    std::vector<float> invMass;
    std::vector<uint8_t> pinned, alive;
    std::vector<Spring> springs;
    std::vector<Collider> colliders;

    // interaction
    int grabIndex = -1;
    Vec3 grabTarget;

    // metrics of the last frame
    float maxStretch = 1.0f;
    float meanStretch = 0.0f;
    float kinetic = 0.0f;
    float maxPenetration = 0.0f;
    int contactCount = 0;
    int brokenSprings = 0;
    int deadParticles = 0;

    bool blownUp = false;
    float time = 0.0f;
    int stepsDone = 0;

    void build(int nx_, int ny_, float width_, float height_, const Vec3& origin,
               const Vec3& uAxis, const Vec3& vAxis);
    void reset();
    void step(float dt);

    int idx(int i, int j) const { return i * par.nx + j; }
    bool valid() const { return !pos.empty(); }
    float avgLinkLength() const;

    void computeNormals();
    void clearWind();
    void computeWindAcc(float dt);

private:
    void buildSprings();
    void solvePBD(float dt);
    void solveEuler(float dt);
    void applyConstraints(int iterations);
    void collidePBD(bool finalPass);
    void collideEuler(float h);
    void applyTear();
    void updateMetrics(float frameDt);
};





