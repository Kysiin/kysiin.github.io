// collision.h - analytic colliders (sphere / plane / axis-aligned box)
#pragma once
#include "math3d.h"
#include <vector>

enum ColliderType { COL_SPHERE = 0, COL_PLANE = 1, COL_BOX = 2 };

struct Collider {
    ColliderType type = COL_SPHERE;
    Vec3 center{0, 0, 0};
    float radius = 0.5f;
    Vec3 normal{0, 1, 0};   // plane: outward normal
    float offset = 0.0f;    // plane: keep points with dot(n,p) >= offset
    Vec3 half{0.5f, 0.5f, 0.5f}; // box half extents

    static Collider sphere(const Vec3& c, float r) {
        Collider col; col.type = COL_SPHERE; col.center = c; col.radius = r; return col;
    }
    static Collider plane(const Vec3& n, float d) {
        Collider col; col.type = COL_PLANE; col.normal = normalize(n); col.offset = d; return col;
    }
    static Collider box(const Vec3& c, const Vec3& half) {
        Collider col; col.type = COL_BOX; col.center = c; col.half = half; return col;
    }
};

// Push point p out of collider c. Returns true when a correction happened.
// n receives the outward contact normal, depth the penetration depth.
inline bool pushOut(Vec3& p, const Collider& c, float thickness, Vec3& n, float& depth) {
    switch (c.type) {
    case COL_SPHERE: {
        Vec3 d = p - c.center;
        float len = length(d);
        float r = c.radius + thickness;
        if (len < r) {
            n = len > 1e-6f ? d / len : Vec3(0, 1, 0);
            depth = r - len;
            p = c.center + n * r;
            return true;
        }
        return false;
    }
    case COL_PLANE: {
        float d = dot(c.normal, p) - c.offset - thickness;
        if (d < 0.0f) {
            n = c.normal;
            depth = -d;
            p -= c.normal * d;
            return true;
        }
        return false;
    }
    case COL_BOX: {
        Vec3 l = p - c.center;
        if (std::fabs(l.x) < c.half.x + thickness &&
            std::fabs(l.y) < c.half.y + thickness &&
            std::fabs(l.z) < c.half.z + thickness) {
            // choose the axis with the smallest penetration
            float px = c.half.x + thickness - std::fabs(l.x);
            float py = c.half.y + thickness - std::fabs(l.y);
            float pz = c.half.z + thickness - std::fabs(l.z);
            if (px <= py && px <= pz) {
                n = Vec3(l.x >= 0 ? 1.f : -1.f, 0, 0);
                depth = px;
                p.x = c.center.x + n.x * (c.half.x + thickness);
            } else if (py <= pz) {
                n = Vec3(0, l.y >= 0 ? 1.f : -1.f, 0);
                depth = py;
                p.y = c.center.y + n.y * (c.half.y + thickness);
            } else {
                n = Vec3(0, 0, l.z >= 0 ? 1.f : -1.f);
                depth = pz;
                p.z = c.center.z + n.z * (c.half.z + thickness);
            }
            return true;
        }
        return false;
    }
    }
    return false;
}
