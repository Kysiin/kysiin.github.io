#include "cloth.h"
#include <cstring>
#include <cmath>

// Aerodynamic coefficient (per unit area, per unit normal velocity).
static const float kWind = 9000.0f;
static const float kTangDrag = 220.0f;

void Cloth::build(int nx_, int ny_, float width_, float height_, const Vec3& origin,
                  const Vec3& uAxis, const Vec3& vAxis) {
    par.nx = nx_;
    par.ny = ny_;
    par.width = width_;
    par.height = height_;

    const int n = nx_ * ny_;
    pos.assign(n, Vec3());
    prev.assign(n, Vec3());
    vel.assign(n, Vec3());
    restPos.assign(n, Vec3());
    nrm.assign(n, Vec3(0, 1, 0));
    windAcc.assign(n, Vec3());
    invMass.assign(n, 1.0f / par.mass);
    pinned.assign(n, 0);
    alive.assign(n, 1);

    Vec3 u = normalize(uAxis);
    Vec3 v = normalize(vAxis);
    for (int i = 0; i < ny_; ++i) {
        for (int j = 0; j < nx_; ++j) {
            float s = nx_ > 1 ? (float)j / (nx_ - 1) : 0.0f;
            float t = ny_ > 1 ? (float)i / (ny_ - 1) : 0.0f;
            Vec3 p = origin + u * (width_ * s) + v * (height_ * t);
            int k = idx(i, j);
            pos[k] = prev[k] = restPos[k] = p;
        }
    }
    buildSprings();
    computeNormals();
}

void Cloth::buildSprings() {
    springs.clear();
    springs.reserve(par.nx * par.ny * 4);
    auto add = [&](int a, int b, SpringType t) {
        Spring s;
        s.a = a; s.b = b; s.type = (uint8_t)t;
        s.rest = length(restPos[a] - restPos[b]);
        springs.push_back(s);
    };
    const int nx = par.nx, ny = par.ny;
    for (int i = 0; i < ny; ++i) {
        for (int j = 0; j < nx; ++j) {
            if (j + 1 < nx) add(idx(i, j), idx(i, j + 1), SPR_STRUCT);
            if (i + 1 < ny) add(idx(i, j), idx(i + 1, j), SPR_STRUCT);
            if (j + 1 < nx && i + 1 < ny) {
                add(idx(i, j), idx(i + 1, j + 1), SPR_SHEAR);
                add(idx(i + 1, j), idx(i, j + 1), SPR_SHEAR);
            }
            if (j + 2 < nx) add(idx(i, j), idx(i, j + 2), SPR_BEND);
            if (i + 2 < ny) add(idx(i, j), idx(i + 2, j), SPR_BEND);
        }
    }
}

void Cloth::reset() {
    pos = restPos;
    prev = restPos;
    vel.assign(pos.size(), Vec3());
    windAcc.assign(pos.size(), Vec3());
    for (size_t i = 0; i < pos.size(); ++i) {
        alive[i] = 1;
        invMass[i] = pinned[i] ? 0.0f : 1.0f / par.mass;
        nrm[i] = Vec3(0, 1, 0);
    }
    for (auto& s : springs) s.broken = false;
    grabIndex = -1;
    blownUp = false;
    time = 0.0f;
    stepsDone = 0;
    maxPenetration = 0; contactCount = 0; brokenSprings = 0; deadParticles = 0;
    maxStretch = 1.0f; meanStretch = 0.0f; kinetic = 0.0f;
    computeNormals();
}

void Cloth::step(float dt) {
    if (pos.empty() || blownUp) return;
    const int sub = std::max(1, par.substeps);
    const float h = dt / (float)sub;
    maxPenetration = 0.0f;
    contactCount = 0;
    time += dt;
    stepsDone++;

    computeNormals();
    computeWindAcc(dt);

    for (int s = 0; s < sub; ++s) {
        if (par.solver == 1) solveEuler(h);
        else solvePBD(h);
    }

    if (grabIndex >= 0 && grabIndex < (int)pos.size()) {
        pos[grabIndex] = grabTarget;
        prev[grabIndex] = grabTarget;
    }

    if (par.tearRatio > 0.0f) applyTear();

    computeNormals();
    updateMetrics(dt);
}

void Cloth::clearWind() { windAcc.assign(pos.size(), Vec3()); }

void Cloth::computeWindAcc(float /*dt*/) {
    clearWind();
    if (par.windStrength <= 0.0f && par.turbulence <= 0.0f) return;
    const int nx = par.nx, ny = par.ny;
    const Vec3 base = normalize(par.windDir) * par.windStrength;
    const float gust = 1.0f + 0.25f * std::sin(time * 1.7f) + 0.12f * std::sin(time * 4.3f + 1.0f);

    auto addTri = [&](int a, int b, int c) {
        if (!alive[a] || !alive[b] || !alive[c]) return;
        Vec3 e1 = pos[b] - pos[a];
        Vec3 e2 = pos[c] - pos[a];
        Vec3 cr = cross(e1, e2);
        float area = 0.5f * length(cr);
        if (area < 1e-12f) return;
        Vec3 n = cr / (2.0f * area);
        Vec3 cen = (pos[a] + pos[b] + pos[c]) / 3.0f;
        Vec3 vc = (vel[a] + vel[b] + vel[c]) / 3.0f;

        Vec3 w = base * gust;
        if (par.turbulence > 0.0f) {
            float ph = time * 2.1f + cen.y * 3.1f + cen.x * 1.7f + cen.z * 1.3f;
            w += Vec3(std::sin(ph * 1.3f), 0.45f * std::sin(ph * 0.7f + 1.1f),
                      std::cos(ph)) * par.turbulence;
        }
        Vec3 rel = w - vc;
        float vn = dot(n, rel);
        Vec3 f = n * (vn * area * kWind);
        Vec3 tang = rel - n * vn;
        f += tang * (area * kTangDrag);
        Vec3 acc = f * (invMass[a] / 3.0f);
        windAcc[a] += acc;
        windAcc[b] += acc;
        windAcc[c] += acc;
    };

    for (int i = 0; i + 1 < ny; ++i) {
        for (int j = 0; j + 1 < nx; ++j) {
            int a = idx(i, j), b = idx(i, j + 1), c = idx(i + 1, j), d = idx(i + 1, j + 1);
            addTri(a, b, d);
            addTri(a, d, c);
        }
    }
}

void Cloth::solvePBD(float h) {
    const float h2 = h * h;
    for (size_t i = 0; i < pos.size(); ++i) {
        if (!alive[i] || invMass[i] <= 0.0f) continue;
        Vec3 v = (pos[i] - prev[i]) * par.damping;
        prev[i] = pos[i];
        pos[i] += v + (par.gravity + windAcc[i]) * h2;
    }
    applyConstraints(par.iterations);
}

void Cloth::applyConstraints(int iters) {
    float keff[3];
    for (int t = 0; t < 3; ++t) {
        float k = clampf(par.stiffness[t], 0.0f, 1.0f);
        keff[t] = 1.0f - std::pow(1.0f - k, 1.0f / (float)std::max(1, iters));
    }
    for (int it = 0; it < iters; ++it) {
        for (const Spring& s : springs) {
            if (s.broken) continue;
            int a = s.a, b = s.b;
            if (!alive[a] || !alive[b]) continue;
            float wa = invMass[a], wb = invMass[b];
            float wsum = wa + wb;
            if (wsum <= 1e-9f) continue;
            Vec3 d = pos[a] - pos[b];
            float len = length(d);
            if (len < 1e-9f) continue;
            float diff = (len - s.rest) / len * keff[s.type];
            pos[a] -= d * (diff * wa / wsum);
            pos[b] += d * (diff * wb / wsum);
        }
        collidePBD(false);
    }
    collidePBD(true);
}

void Cloth::collidePBD(bool finalPass) {
    const int n = (int)pos.size();
    for (int i = 0; i < n; ++i) {
        if (!alive[i] || invMass[i] <= 0.0f) continue;
        for (const Collider& c : colliders) {
            Vec3 nn; float depth;
            if (pushOut(pos[i], c, par.thickness, nn, depth)) {
                if (depth > maxPenetration) maxPenetration = depth;
                if (finalPass) {
                    contactCount++;
                    Vec3 dlt = pos[i] - prev[i];
                    float vn = dot(dlt, nn);
                    Vec3 tang = dlt - nn * vn;
                    prev[i] = pos[i] - tang * (1.0f - clampf(par.friction, 0.0f, 1.0f));
                }
            }
        }
    }
}

void Cloth::solveEuler(float h) {
    const int n = (int)pos.size();
    std::vector<Vec3> force(n, Vec3());
    for (size_t i = 0; i < force.size(); ++i) {
        if (alive[i] && invMass[i] > 0.0f) force[i] = (par.gravity + windAcc[i]) / invMass[i];
    }
    for (const Spring& s : springs) {
        if (s.broken) continue;
        int a = s.a, b = s.b;
        if (!alive[a] || !alive[b]) continue;
        Vec3 d = pos[a] - pos[b];
        float len = length(d);
        if (len < 1e-9f) continue;
        Vec3 dir = d / len;
        float relV = dot(vel[a] - vel[b], dir);
        float k = par.eulerK[s.type] * clampf(par.stiffness[s.type], 0.0f, 1.0f);
        float f = -(k * (len - s.rest) + par.eulerDamp * relV);
        Vec3 F = dir * f;
        force[a] += F;
        force[b] -= F;
    }
    for (int i = 0; i < n; ++i) {
        if (!alive[i] || invMass[i] <= 0.0f) continue;
        vel[i] += force[i] * (invMass[i] * h);
        vel[i] *= par.damping;
        pos[i] += vel[i] * h;
    }
    collideEuler(h);
}

void Cloth::collideEuler(float /*h*/) {
    for (size_t i = 0; i < pos.size(); ++i) {
        if (!alive[i] || invMass[i] <= 0.0f) continue;
        for (const Collider& c : colliders) {
            Vec3 nn; float depth;
            if (pushOut(pos[i], c, par.thickness, nn, depth)) {
                if (depth > maxPenetration) maxPenetration = depth;
                contactCount++;
                float vn = dot(vel[i], nn);
                vel[i] -= nn * vn;
                Vec3 tang = vel[i] - nn * dot(vel[i], nn);
                vel[i] = tang * (1.0f - clampf(par.friction, 0.0f, 1.0f));
            }
        }
    }
}

void Cloth::applyTear() {
    brokenSprings = 0;
    deadParticles = 0;
    for (auto& s : springs) {
        if (s.broken) { ++brokenSprings; continue; }
        if (s.type != SPR_STRUCT) continue;
        if (!alive[s.a] || !alive[s.b]) continue;
        float len = length(pos[s.a] - pos[s.b]);
        if (len > s.rest * par.tearRatio) {
            s.broken = true;
            ++brokenSprings;
        }
    }
    // A particle with no intact structural link is detached: remove it.
    std::vector<uint8_t> hasLink(pos.size(), 0);
    for (const auto& s : springs) {
        if (s.broken || s.type != SPR_STRUCT) continue;
        hasLink[s.a] = 1;
        hasLink[s.b] = 1;
    }
    for (size_t i = 0; i < pos.size(); ++i) {
        if (alive[i] && !hasLink[i]) {
            alive[i] = 0;
            invMass[i] = 0.0f;
        }
        if (!alive[i]) ++deadParticles;
    }
}

void Cloth::computeNormals() {
    const int n = (int)pos.size();
    for (int i = 0; i < n; ++i) nrm[i] = Vec3(0, 0, 0);
    for (int i = 0; i + 1 < par.ny; ++i) {
        for (int j = 0; j + 1 < par.nx; ++j) {
            int a = idx(i, j), b = idx(i, j + 1), c = idx(i + 1, j), d = idx(i + 1, j + 1);
            if (!alive[a] || !alive[b] || !alive[c] || !alive[d]) continue;
            Vec3 f1 = cross(pos[b] - pos[a], pos[d] - pos[a]);
            Vec3 f2 = cross(pos[d] - pos[a], pos[c] - pos[a]);
            nrm[a] += f1; nrm[b] += f1; nrm[d] += f1;
            nrm[a] += f2; nrm[d] += f2; nrm[c] += f2;
        }
    }
    for (int i = 0; i < n; ++i) {
        float l = length(nrm[i]);
        if (l > 1e-12f) nrm[i] = nrm[i] / l;
        else nrm[i] = Vec3(0, 1, 0);
    }
}

void Cloth::updateMetrics(float frameDt) {
    maxStretch = 1.0f;
    meanStretch = 0.0f;
    kinetic = 0.0f;
    for (size_t i = 0; i < pos.size(); ++i) {
        if (!std::isfinite(pos[i].x) || !std::isfinite(pos[i].y) || !std::isfinite(pos[i].z)) {
            blownUp = true;
            maxStretch = 99.0f;
            return;
        }
    }
    int cnt = 0;
    for (const Spring& s : springs) {
        if (s.broken || s.type != SPR_STRUCT) continue;
        if (!alive[s.a] || !alive[s.b]) continue;
        float len = length(pos[s.a] - pos[s.b]);
        float r = len / s.rest;
        if (r > maxStretch) maxStretch = r;
        meanStretch += std::fabs(len - s.rest) / s.rest;
        ++cnt;
    }
    if (cnt) meanStretch /= (float)cnt;
    const float h = frameDt / (float)std::max(1, par.substeps);
    for (size_t i = 0; i < pos.size(); ++i) {
        if (!alive[i] || invMass[i] <= 0.0f) continue;
        Vec3 v = (par.solver == 0) ? (pos[i] - prev[i]) / std::max(1e-7f, h) : vel[i];
        kinetic += 0.5f * par.mass * dot(v, v);
    }
}

float Cloth::avgLinkLength() const {
    if (springs.empty()) return 0.0f;
    float s = 0.0f;
    int c = 0;
    for (const auto& sp : springs) {
        if (sp.type == SPR_STRUCT) { s += sp.rest; ++c; }
    }
    return c ? s / c : 0.0f;
}



