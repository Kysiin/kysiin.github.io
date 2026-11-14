#include "renderer.h"
#include <GL/gl.h>
#include <cstdlib>
#include <cmath>

const Vec3 Renderer::kBgTop{0.135f, 0.155f, 0.195f};
const Vec3 Renderer::kBgBottom{0.048f, 0.055f, 0.070f};

static const Vec3 kLightDir = normalize(Vec3(-0.45f, 1.0f, 0.55f));

static unsigned makeTexture(int w, int h, const unsigned char* rgb) {
    unsigned tex = 0;
    glGenTextures(1, &tex);
    glBindTexture(GL_TEXTURE_2D, tex);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT);
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, w, h, 0, GL_RGB, GL_UNSIGNED_BYTE, rgb);
    return tex;
}

static void buildClothTexture(std::vector<unsigned char>& px, int S) {
    px.assign((size_t)S * S * 3, 0);
    auto put = [&](int x, int y, float r, float g, float b) {
        size_t i = ((size_t)y * S + x) * 3;
        px[i + 0] = (unsigned char)clampf(r * 255.f, 0, 255);
        px[i + 1] = (unsigned char)clampf(g * 255.f, 0, 255);
        px[i + 2] = (unsigned char)clampf(b * 255.f, 0, 255);
    };
    for (int y = 0; y < S; ++y) {
        for (int x = 0; x < S; ++x) {
            float u = (float)x / S, v = (float)y / S;
            // base weave
            float base = 0.88f + 0.006f * std::sin(x * 2.3f + y * 1.7f);
            float r = base * 0.97f, g = base * 0.93f, b = base * 0.84f;

            auto band = [](float t, float center, float width) {
                float d = std::fabs(t - center);
                return d < width ? 0.5f + 0.5f * std::cos(3.14159f * d / width) : 0.0f;
            };
            // red warp stripes
            float a1 = band(u, 0.08f, 0.055f) + band(u, 0.36f, 0.03f) + band(u, 0.64f, 0.055f) + band(u, 0.92f, 0.03f);
            a1 = clampf(a1, 0.f, 1.f) * 0.75f;
            r = r * (1 - a1) + 0.74f * a1;
            g = g * (1 - a1) + 0.13f * a1;
            b = b * (1 - a1) + 0.12f * a1;
            // blue weft stripes
            float a2 = band(v, 0.12f, 0.04f) + band(v, 0.5f, 0.06f) + band(v, 0.86f, 0.025f);
            a2 = clampf(a2, 0.f, 1.f) * 0.7f;
            r = r * (1 - a2) + 0.13f * a2;
            g = g * (1 - a2) + 0.22f * a2;
            b = b * (1 - a2) + 0.52f * a2;
            // thin gold lines
            float a3 = (std::fabs(u - 0.22f) < 0.004f || std::fabs(v - 0.72f) < 0.004f) ? 0.55f : 0.0f;
            r = r * (1 - a3) + 0.85f * a3;
            g = g * (1 - a3) + 0.72f * a3;
            b = b * (1 - a3) + 0.40f * a3;
            put(x, y, r, g, b);
        }
    }
}

static void buildGroundTexture(std::vector<unsigned char>& px, int S) {
    px.assign((size_t)S * S * 3, 0);
    for (int y = 0; y < S; ++y) {
        for (int x = 0; x < S; ++x) {
            int cx = x / (S / 2), cy = y / (S / 2);
            float base = ((cx + cy) & 1) ? 0.165f : 0.205f;
            float n = 0.006f * std::sin(x * 12.9898f + y * 78.233f);
            float c = base + n;
            size_t i = ((size_t)y * S + x) * 3;
            px[i + 0] = (unsigned char)clampf(c * 255.f, 0, 255);
            px[i + 1] = (unsigned char)clampf(c * 1.02f * 255.f, 0, 255);
            px[i + 2] = (unsigned char)clampf(c * 1.12f * 255.f, 0, 255);
        }
    }
}

bool Renderer::init() {
    std::vector<unsigned char> clothPx, groundPx;
    buildClothTexture(clothPx, 512);
    buildGroundTexture(groundPx, 256);
    clothTex_ = makeTexture(512, 512, clothPx.data());
    groundTex_ = makeTexture(256, 256, groundPx.data());

    glEnable(GL_DEPTH_TEST);
    glDepthFunc(GL_LEQUAL);
    glEnable(GL_NORMALIZE);
    glShadeModel(GL_SMOOTH);
    glLightModeli(GL_LIGHT_MODEL_TWO_SIDE, 1);
    glEnable(GL_COLOR_MATERIAL);
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE);

    glEnable(GL_LIGHTING);
    glEnable(GL_LIGHT0);
    glEnable(GL_LIGHT1);

    ready_ = true;
    return true;
}

void Renderer::shutdown() {
    if (clothTex_) glDeleteTextures(1, &clothTex_);
    if (groundTex_) glDeleteTextures(1, &groundTex_);
    clothTex_ = groundTex_ = 0;
    ready_ = false;
}

void Renderer::drawBackground() {
    glMatrixMode(GL_PROJECTION);
    glPushMatrix();
    glLoadIdentity();
    glOrtho(0, 1, 0, 1, -1, 1);
    glMatrixMode(GL_MODELVIEW);
    glPushMatrix();
    glLoadIdentity();
    glDisable(GL_DEPTH_TEST);
    glDisable(GL_LIGHTING);
    glDisable(GL_TEXTURE_2D);
    glDisable(GL_FOG);
    glBegin(GL_QUADS);
    glColor3f(kBgBottom.x, kBgBottom.y, kBgBottom.z);
    glVertex2f(0, 0); glVertex2f(1, 0);
    glColor3f(kBgTop.x, kBgTop.y, kBgTop.z);
    glVertex2f(1, 1); glVertex2f(0, 1);
    glEnd();
    glEnable(GL_DEPTH_TEST);
    glEnable(GL_LIGHTING);
    glMatrixMode(GL_PROJECTION);
    glPopMatrix();
    glMatrixMode(GL_MODELVIEW);
    glPopMatrix();
}

void Renderer::drawGround() {
    glEnable(GL_TEXTURE_2D);
    glBindTexture(GL_TEXTURE_2D, groundTex_);
    glColor3f(1.0f, 1.0f, 1.0f);
    const float S = 18.0f;
    glBegin(GL_QUADS);
    glNormal3f(0, 1, 0);
    const float R = 10.0f;
    glTexCoord2f(0, 0);         glVertex3f(-R, 0, -R);
    glTexCoord2f(S, 0);         glVertex3f(R, 0, -R);
    glTexCoord2f(S, S);         glVertex3f(R, 0, R);
    glTexCoord2f(0, S);         glVertex3f(-R, 0, R);
    glEnd();
    glDisable(GL_TEXTURE_2D);
}

void Renderer::drawSphere(const Vec3& c, float r) {
    const int slices = 40, stacks = 22;
    for (int i = 0; i < stacks; ++i) {
        float t0 = 3.14159265f * (float)i / stacks;
        float t1 = 3.14159265f * (float)(i + 1) / stacks;
        glBegin(GL_QUAD_STRIP);
        for (int j = 0; j <= slices; ++j) {
            float p = 2.0f * 3.14159265f * (float)j / slices;
            auto pv = [&](float t) {
                Vec3 n(std::sin(t) * std::cos(p), std::cos(t), std::sin(t) * std::sin(p));
                glNormal3f(n.x, n.y, n.z);
                glVertex3f(c.x + n.x * r, c.y + n.y * r, c.z + n.z * r);
            };
            pv(t0);
            pv(t1);
        }
        glEnd();
    }
}

void Renderer::drawColliders(const std::vector<Collider>& cols) {
    glEnable(GL_COLOR_MATERIAL);
    for (const Collider& c : cols) {
        if (c.type == COL_SPHERE) {
            glColor3f(0.55f, 0.57f, 0.60f);
            drawSphere(c.center, c.radius);
        } else if (c.type == COL_BOX) {
            glColor3f(0.42f, 0.38f, 0.34f);
            Vec3 h = c.half, p = c.center;
            glBegin(GL_QUADS);
            auto face = [&](Vec3 n, Vec3 a, Vec3 b, Vec3 d, Vec3 e) {
                glNormal3f(n.x, n.y, n.z);
                glVertex3f(a.x, a.y, a.z); glVertex3f(b.x, b.y, b.z);
                glVertex3f(d.x, d.y, d.z); glVertex3f(e.x, e.y, e.z);
            };
            face(Vec3(0, 1, 0), p + Vec3(-h.x, h.y, -h.z), p + Vec3(-h.x, h.y, h.z), p + Vec3(h.x, h.y, h.z), p + Vec3(h.x, h.y, -h.z));
            face(Vec3(0, -1, 0), p + Vec3(-h.x, -h.y, -h.z), p + Vec3(h.x, -h.y, -h.z), p + Vec3(h.x, -h.y, h.z), p + Vec3(-h.x, -h.y, h.z));
            face(Vec3(1, 0, 0), p + Vec3(h.x, -h.y, -h.z), p + Vec3(h.x, -h.y, h.z), p + Vec3(h.x, h.y, h.z), p + Vec3(h.x, h.y, -h.z));
            face(Vec3(-1, 0, 0), p + Vec3(-h.x, -h.y, -h.z), p + Vec3(-h.x, h.y, -h.z), p + Vec3(-h.x, h.y, h.z), p + Vec3(-h.x, -h.y, h.z));
            face(Vec3(0, 0, 1), p + Vec3(-h.x, -h.y, h.z), p + Vec3(-h.x, h.y, h.z), p + Vec3(h.x, h.y, h.z), p + Vec3(h.x, -h.y, h.z));
            face(Vec3(0, 0, -1), p + Vec3(-h.x, -h.y, -h.z), p + Vec3(h.x, -h.y, -h.z), p + Vec3(h.x, h.y, -h.z), p + Vec3(-h.x, h.y, -h.z));
            glEnd();
        }
    }
}

void Renderer::drawCloth(const Cloth& cloth, const RenderOptions& opt) {
    const ClothParams& par = cloth.par;
    glEnable(GL_TEXTURE_2D);
    glBindTexture(GL_TEXTURE_2D, clothTex_);
    if (!opt.showClothTexture || opt.wireframe) {
        glDisable(GL_TEXTURE_2D);
        glColor3f(0.80f, 0.32f, 0.28f);
    } else {
        glColor3f(1, 1, 1);
    }
    const float nx = (float)(par.nx - 1), ny = (float)(par.ny - 1);
    glBegin(GL_TRIANGLES);
    for (int i = 0; i + 1 < par.ny; ++i) {
        for (int j = 0; j + 1 < par.nx; ++j) {
            int a = cloth.idx(i, j), b = cloth.idx(i, j + 1);
            int c = cloth.idx(i + 1, j), d = cloth.idx(i + 1, j + 1);
            if (!cloth.alive[a] || !cloth.alive[b] || !cloth.alive[c] || !cloth.alive[d]) continue;
            float u0 = j / nx, u1 = (j + 1) / nx;
            float v0 = i / ny, v1 = (i + 1) / ny;
            auto vtx = [&](int k, float u, float v) {
                glTexCoord2f(u, v);
                glNormal3f(cloth.nrm[k].x, cloth.nrm[k].y, cloth.nrm[k].z);
                glVertex3f(cloth.pos[k].x, cloth.pos[k].y, cloth.pos[k].z);
            };
            vtx(a, u0, v0); vtx(b, u1, v0); vtx(d, u1, v1);
            vtx(a, u0, v0); vtx(d, u1, v1); vtx(c, u0, v1);
        }
    }
    glEnd();
    glDisable(GL_TEXTURE_2D);
}

void Renderer::drawShadow(const Cloth& cloth) {
    const ClothParams& par = cloth.par;
    glDisable(GL_LIGHTING);
    glDisable(GL_TEXTURE_2D);
    glEnable(GL_BLEND);
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
    glEnable(GL_POLYGON_OFFSET_FILL);
    glPolygonOffset(-2.0f, -2.0f);
    glColor4f(0.0f, 0.0f, 0.0f, 0.32f);
    auto project = [&](int k) {
        Vec3 p = cloth.pos[k];
        float t = p.y / kLightDir.y;
        return Vec3(p.x - kLightDir.x * t, 0.002f, p.z - kLightDir.z * t);
    };
    glBegin(GL_TRIANGLES);
    for (int i = 0; i + 1 < par.ny; ++i) {
        for (int j = 0; j + 1 < par.nx; ++j) {
            int a = cloth.idx(i, j), b = cloth.idx(i, j + 1);
            int c = cloth.idx(i + 1, j), d = cloth.idx(i + 1, j + 1);
            if (!cloth.alive[a] || !cloth.alive[b] || !cloth.alive[c] || !cloth.alive[d]) continue;
            Vec3 A = project(a), B = project(b), D = project(d), Cc = project(c);
            glVertex3f(A.x, A.y, A.z); glVertex3f(B.x, B.y, B.z); glVertex3f(D.x, D.y, D.z);
            glVertex3f(A.x, A.y, A.z); glVertex3f(D.x, D.y, D.z); glVertex3f(Cc.x, Cc.y, Cc.z);
        }
    }
    glEnd();
    glDisable(GL_POLYGON_OFFSET_FILL);
    glDisable(GL_BLEND);
    glEnable(GL_LIGHTING);
}

void Renderer::draw(const Cloth& cloth, const std::vector<Collider>& cols, const Camera& cam,
                    const RenderOptions& opt, int width, int height) {
    if (!ready_) return;
    glViewport(0, 0, width, height);
    glClearColor(kBgBottom.x, kBgBottom.y, kBgBottom.z, 1.0f);
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    drawBackground();

    Mat4 P = Mat4::perspective(45.0f, (float)width / (float)std::max(1, height), 0.05f, 60.0f);
    Mat4 V = Mat4::lookAt(cam.eye(), cam.target, Vec3(0, 1, 0));
    glMatrixMode(GL_PROJECTION);
    glLoadMatrixf(P.m);
    glMatrixMode(GL_MODELVIEW);
    glLoadMatrixf(V.m);

    GLfloat l0pos[4] = {kLightDir.x, kLightDir.y, kLightDir.z, 0.0f};
    GLfloat l0dif[4] = {1.0f, 0.97f, 0.91f, 1.0f};
    GLfloat l0amb[4] = {0.26f, 0.27f, 0.30f, 1.0f};
    GLfloat l0spec[4] = {0.45f, 0.45f, 0.45f, 1.0f};
    glLightfv(GL_LIGHT0, GL_POSITION, l0pos);
    glLightfv(GL_LIGHT0, GL_DIFFUSE, l0dif);
    glLightfv(GL_LIGHT0, GL_AMBIENT, l0amb);
    glLightfv(GL_LIGHT0, GL_SPECULAR, l0spec);

    GLfloat l1pos[4] = {0.6f, 0.25f, -0.7f, 0.0f};
    GLfloat l1dif[4] = {0.22f, 0.24f, 0.30f, 1.0f};
    GLfloat l1amb[4] = {0.0f, 0.0f, 0.0f, 1.0f};
    glLightfv(GL_LIGHT1, GL_POSITION, l1pos);
    glLightfv(GL_LIGHT1, GL_DIFFUSE, l1dif);
    glLightfv(GL_LIGHT1, GL_AMBIENT, l1amb);

    GLfloat matSpec[4] = {0.12f, 0.12f, 0.12f, 1.0f};
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, matSpec);
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 20.0f);
    glLightModeli(GL_LIGHT_MODEL_TWO_SIDE, 1);

    glEnable(GL_FOG);
    glFogi(GL_FOG_MODE, GL_EXP2);
    glFogf(GL_FOG_DENSITY, 0.055f);
    GLfloat fogCol[4] = {kBgBottom.x, kBgBottom.y, kBgBottom.z, 1.0f};
    glFogfv(GL_FOG_COLOR, fogCol);

    if (opt.showGround) drawGround();
    if (opt.showShadow) drawShadow(cloth);
    if (opt.showColliders) drawColliders(cols);
    drawCloth(cloth, opt);

    if (opt.wireframe) {
        glDisable(GL_LIGHTING);
        glDisable(GL_TEXTURE_2D);
        glDisable(GL_FOG);
        glColor4f(0.05f, 0.06f, 0.07f, 0.55f);
        glEnable(GL_BLEND);
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
        glBegin(GL_LINES);
        for (int i = 0; i < cloth.par.ny; ++i) {
            for (int j = 0; j + 1 < cloth.par.nx; ++j) {
                int a = cloth.idx(i, j), b = cloth.idx(i, j + 1);
                if (!cloth.alive[a] || !cloth.alive[b]) continue;
                glVertex3f(cloth.pos[a].x, cloth.pos[a].y, cloth.pos[a].z);
                glVertex3f(cloth.pos[b].x, cloth.pos[b].y, cloth.pos[b].z);
            }
        }
        for (int j = 0; j < cloth.par.nx; ++j) {
            for (int i = 0; i + 1 < cloth.par.ny; ++i) {
                int a = cloth.idx(i, j), b = cloth.idx(i + 1, j);
                if (!cloth.alive[a] || !cloth.alive[b]) continue;
                glVertex3f(cloth.pos[a].x, cloth.pos[a].y, cloth.pos[a].z);
                glVertex3f(cloth.pos[b].x, cloth.pos[b].y, cloth.pos[b].z);
            }
        }
        glEnd();
        glDisable(GL_BLEND);
        glEnable(GL_LIGHTING);
    }
    glDisable(GL_FOG);
}




