// math3d.h - minimal vector / matrix helpers (no external dependencies)
#pragma once
#include <cmath>
#include <algorithm>

struct Vec3 {
    float x = 0, y = 0, z = 0;
    Vec3() = default;
    Vec3(float x_, float y_, float z_) : x(x_), y(y_), z(z_) {}
    Vec3 operator+(const Vec3& o) const { return {x + o.x, y + o.y, z + o.z}; }
    Vec3 operator-(const Vec3& o) const { return {x - o.x, y - o.y, z - o.z}; }
    Vec3 operator*(float s) const { return {x * s, y * s, z * s}; }
    Vec3 operator/(float s) const { return {x / s, y / s, z / s}; }
    Vec3& operator+=(const Vec3& o) { x += o.x; y += o.y; z += o.z; return *this; }
    Vec3& operator-=(const Vec3& o) { x -= o.x; y -= o.y; z -= o.z; return *this; }
    Vec3& operator*=(float s) { x *= s; y *= s; z *= s; return *this; }
    float& operator[](int i) { return (&x)[i]; }
    float operator[](int i) const { return (&x)[i]; }
};

inline Vec3 operator*(float s, const Vec3& v) { return v * s; }
inline float dot(const Vec3& a, const Vec3& b) { return a.x * b.x + a.y * b.y + a.z * b.z; }
inline Vec3 cross(const Vec3& a, const Vec3& b) {
    return {a.y * b.z - a.z * b.y, a.z * b.x - a.x * b.z, a.x * b.y - a.y * b.x};
}
inline float length(const Vec3& v) { return std::sqrt(dot(v, v)); }
inline Vec3 normalize(const Vec3& v) {
    float l = length(v);
    return l > 1e-12f ? v / l : Vec3(0, 0, 0);
}
inline Vec3 lerp(const Vec3& a, const Vec3& b, float t) { return a + (b - a) * t; }
inline Vec3 vmin(const Vec3& a, const Vec3& b) { return {std::min(a.x,b.x), std::min(a.y,b.y), std::min(a.z,b.z)}; }
inline Vec3 vmax(const Vec3& a, const Vec3& b) { return {std::max(a.x,b.x), std::max(a.y,b.y), std::max(a.z,b.z)}; }
inline float clampf(float v, float lo, float hi) { return v < lo ? lo : (v > hi ? hi : v); }

// Column-major 4x4 matrix, directly usable with glLoadMatrixf.
struct Mat4 {
    float m[16] = {1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1};

    static Mat4 perspective(float fovyDeg, float aspect, float zn, float zf) {
        Mat4 r;
        float f = 1.0f / std::tan(fovyDeg * 3.14159265358979f / 360.0f);
        for (int i = 0; i < 16; ++i) r.m[i] = 0;
        r.m[0] = f / aspect;
        r.m[5] = f;
        r.m[10] = (zf + zn) / (zn - zf);
        r.m[11] = -1.0f;
        r.m[14] = 2.0f * zf * zn / (zn - zf);
        return r;
    }

    static Mat4 lookAt(const Vec3& eye, const Vec3& center, const Vec3& up) {
        Vec3 f = normalize(center - eye);
        Vec3 s = normalize(cross(f, up));
        Vec3 u = cross(s, f);
        Mat4 r;
        r.m[0] = s.x;  r.m[4] = s.y;  r.m[8]  = s.z;  r.m[12] = -dot(s, eye);
        r.m[1] = u.x;  r.m[5] = u.y;  r.m[9]  = u.z;  r.m[13] = -dot(u, eye);
        r.m[2] = -f.x; r.m[6] = -f.y; r.m[10] = -f.z; r.m[14] = dot(f, eye);
        r.m[3] = 0;    r.m[7] = 0;    r.m[11] = 0;    r.m[15] = 1;
        return r;
    }
};

// Ray from camera through a screen pixel, used for mouse picking.
struct Ray { Vec3 o, d; };

inline Ray screenRay(float mx, float my, int w, int h, const Vec3& eye,
                     const Vec3& target, float fovyDeg) {
    Vec3 f = normalize(target - eye);
    Vec3 s = normalize(cross(f, Vec3(0, 1, 0)));
    Vec3 u = cross(s, f);
    float aspect = (float)w / (float)h;
    float ndcX = (2.0f * mx / w - 1.0f) * std::tan(fovyDeg * 3.14159265358979f / 360.0f) * aspect;
    float ndcY = (1.0f - 2.0f * my / h) * std::tan(fovyDeg * 3.14159265358979f / 360.0f);
    Ray r;
    r.o = eye;
    r.d = normalize(f + s * ndcX + u * ndcY);
    return r;
}
