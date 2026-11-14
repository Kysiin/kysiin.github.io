// main.cpp - ClothLab: real-time mass-spring cloth animation with collision response
#define NOMINMAX
#include <windows.h>
#include <GL/gl.h>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <cmath>

#include "math3d.h"
#include "cloth.h"
#include "scene.h"
#include "renderer.h"
#include "hud.h"
#include "capture.h"
#include "bench.h"

static const float kFixedDt = 1.0f / 60.0f;

struct App {
    HWND hwnd = nullptr;
    HDC hdc = nullptr;
    HGLRC rc = nullptr;
    int width = 1280, height = 800;

    Renderer renderer;
    Hud hud;
    Cloth cloth;
    std::vector<Collider> cols;
    Camera cam;
    RenderOptions opt;
    std::string sceneId = "flag";
    std::string title;

    bool running = true;
    bool paused = false;
    bool stepOnce = false;
    bool showPanel = true;
    bool console = false;

    bool orbit = false;
    int lastX = 0, lastY = 0;

    bool grabbing = false;
    float grabDepth = 0.0f;
    Vec3 grabOffset;

    bool record = false;
    std::string recordDir;
    int recordFrame = 0;

    int frameLimit = -1;
    int frameCount = 0;
    std::string shotPath;
    std::string benchPath;

    float accum = 0.0f;
    float fps = 0.0f;
    double lastTime = 0.0;
    double qpcFreq = 0.0;

    int shotCounter = 0;

    // CLI overrides, applied after the scene has been built
    int cliIter = -1, cliSub = -1, cliSolver = -1;
    float cliK = -1.0f, cliWind = -1.0f;
};

static App g;

static double nowSeconds() {
    LARGE_INTEGER t;
    QueryPerformanceCounter(&t);
    return (double)t.QuadPart / g.qpcFreq;
}

static LRESULT CALLBACK wndProc(HWND h, UINT msg, WPARAM wp, LPARAM lp);

static bool initWindow() {
    WNDCLASSA wc = {};
    wc.style = CS_OWNDC;
    wc.lpfnWndProc = wndProc;
    wc.hInstance = GetModuleHandleA(nullptr);
    wc.lpszClassName = "ClothLabWindow";
    wc.hCursor = LoadCursor(nullptr, IDC_ARROW);
    wc.hbrBackground = nullptr;
    if (!RegisterClassA(&wc)) return false;

    RECT r = {0, 0, g.width, g.height};
    AdjustWindowRect(&r, WS_OVERLAPPEDWINDOW, FALSE);
    g.hwnd = CreateWindowA("ClothLabWindow", "ClothLab - Mass-Spring Cloth Animation",
                           WS_OVERLAPPEDWINDOW, CW_USEDEFAULT, CW_USEDEFAULT,
                           r.right - r.left, r.bottom - r.top,
                           nullptr, nullptr, wc.hInstance, nullptr);
    if (!g.hwnd) return false;

    g.hdc = GetDC(g.hwnd);
    PIXELFORMATDESCRIPTOR pfd = {};
    pfd.nSize = sizeof(pfd);
    pfd.nVersion = 1;
    pfd.dwFlags = PFD_DRAW_TO_WINDOW | PFD_SUPPORT_OPENGL | PFD_DOUBLEBUFFER;
    pfd.iPixelType = PFD_TYPE_RGBA;
    pfd.cColorBits = 32;
    pfd.cDepthBits = 24;
    pfd.iLayerType = PFD_MAIN_PLANE;
    int pf = ChoosePixelFormat(g.hdc, &pfd);
    if (!pf || !SetPixelFormat(g.hdc, pf, &pfd)) return false;
    g.rc = wglCreateContext(g.hdc);
    if (!g.rc || !wglMakeCurrent(g.hdc, g.rc)) return false;

    ShowWindow(g.hwnd, SW_SHOW);
    return true;
}

static void resetScene(bool rebuild) {
    std::string t;
    if (rebuild || g.cloth.pos.empty()) {
        buildScene(g.sceneId, g.cloth, g.cols, g.cam, t);
        g.title = t;
    } else {
        g.cloth.reset();
    }
    g.accum = 0.0f;
    g.paused = false;
    g.stepOnce = false;
}

static void screenshot(const std::string& path) {
    if (captureTGA(path.c_str(), g.width, g.height)) {
        printf("screenshot: %s\n", path.c_str());
    } else {
        printf("screenshot failed: %s\n", path.c_str());
    }
}

static void doGrab(int mx, int my) {
    Ray ray = screenRay((float)mx, (float)my, g.width, g.height, g.cam.eye(), g.cam.target, 45.0f);
    float best = 1e9f;
    int bestIdx = -1;
    float bestT = 0.0f;
    for (size_t i = 0; i < g.cloth.pos.size(); ++i) {
        if (!g.cloth.alive[i]) continue;
        Vec3 d = g.cloth.pos[i] - ray.o;
        float t = dot(d, ray.d);
        if (t <= 0.0f) continue;
        Vec3 closest = ray.o + ray.d * t;
        float dist = length(g.cloth.pos[i] - closest);
        float limit = 0.10f * (g.cam.dist / 3.0f);
        if (dist < limit && dist < best) {
            best = dist;
            bestIdx = (int)i;
            bestT = t;
        }
    }
    if (bestIdx >= 0) {
        g.grabbing = true;
        g.grabDepth = bestT;
        g.grabOffset = g.cloth.pos[bestIdx] - (ray.o + ray.d * bestT);
        g.cloth.grabIndex = bestIdx;
        g.cloth.grabTarget = g.cloth.pos[bestIdx];
    }
}

static void updateGrab(int mx, int my) {
    if (!g.grabbing || g.cloth.grabIndex < 0) return;
    Ray ray = screenRay((float)mx, (float)my, g.width, g.height, g.cam.eye(), g.cam.target, 45.0f);
    g.cloth.grabTarget = ray.o + ray.d * g.grabDepth + g.grabOffset;
}

static void handleKey(WPARAM key) {
    switch (key) {
    case VK_ESCAPE: g.running = false; break;
    case ' ': g.paused = !g.paused; break;
    case 'N': g.stepOnce = true; break;
    case 'R': resetScene(true); break;
    case 'T':
        g.cloth.par.solver = g.cloth.par.solver == 0 ? 1 : 0;
        g.cloth.par.substeps = g.cloth.par.solver == 0 ? 6 : 32;
        g.cloth.reset();
        break;
    case 'W': g.opt.wireframe = !g.opt.wireframe; break;
    case 'G': g.opt.showShadow = !g.opt.showShadow; break;
    case 'C': g.opt.showColliders = !g.opt.showColliders; break;
    case 'H': g.showPanel = !g.showPanel; break;
    case 'P': {
        char buf[64];
        snprintf(buf, sizeof(buf), "shot_%03d.tga", g.shotCounter++);
        screenshot(buf);
        break;
    }
    case 'F':
        g.record = !g.record;
        if (g.record) {
            if (g.recordDir.empty()) g.recordDir = "frames";
            CreateDirectoryA(g.recordDir.c_str(), nullptr);
            g.recordFrame = 0;
            printf("recording to %s\n", g.recordDir.c_str());
        }
        break;
    case 'J':
        g.cloth.par.stiffness[0] = clampf(g.cloth.par.stiffness[0] - 0.05f, 0.05f, 1.0f);
        break;
    case 'K':
        g.cloth.par.stiffness[0] = clampf(g.cloth.par.stiffness[0] + 0.05f, 0.05f, 1.0f);
        break;
    case 'U':
        g.cloth.par.iterations = (std::max)(1, g.cloth.par.iterations - 1);
        break;
    case 'I':
        g.cloth.par.iterations = (std::min)(20, g.cloth.par.iterations + 1);
        break;
    case '[':
        g.cloth.par.windStrength = (std::max)(0.0f, g.cloth.par.windStrength - 1.0f);
        break;
    case ']':
        g.cloth.par.windStrength = (std::min)(20.0f, g.cloth.par.windStrength + 1.0f);
        break;
    case '1': g.sceneId = "flag"; resetScene(true); break;
    case '2': g.sceneId = "drape"; resetScene(true); break;
    case '3': g.sceneId = "table"; resetScene(true); break;
    case '4': g.sceneId = "tear"; resetScene(true); break;
    case '5': g.sceneId = "spheres"; resetScene(true); break;
    case '6': g.sceneId = "slide"; resetScene(true); break;
    default: break;
    }
}

static LRESULT CALLBACK wndProc(HWND h, UINT msg, WPARAM wp, LPARAM lp) {
    switch (msg) {
    case WM_CLOSE:
    case WM_DESTROY:
        g.running = false;
        return 0;
    case WM_ERASEBKGND:
        return 1;
    case WM_SIZE:
        g.width = (std::max)(1, (int)LOWORD(lp));
        g.height = (std::max)(1, (int)HIWORD(lp));
        return 0;
    case WM_KEYDOWN:
        if (!(lp & (1 << 30))) handleKey(wp);
        return 0;
    case WM_LBUTTONDOWN:
        g.lastX = (int)(short)LOWORD(lp);
        g.lastY = (int)(short)HIWORD(lp);
        doGrab(g.lastX, g.lastY);
        if (!g.grabbing) g.orbit = true;
        SetCapture(h);
        return 0;
    case WM_LBUTTONUP:
        g.orbit = false;
        g.grabbing = false;
        g.cloth.grabIndex = -1;
        ReleaseCapture();
        return 0;
    case WM_MOUSEMOVE: {
        int mx = (int)(short)LOWORD(lp), my = (int)(short)HIWORD(lp);
        if (g.grabbing) {
            updateGrab(mx, my);
        } else if (g.orbit) {
            g.cam.yaw -= (mx - g.lastX) * 0.008f;
            g.cam.pitch = clampf(g.cam.pitch + (my - g.lastY) * 0.006f, -1.4f, 1.4f);
        }
        g.lastX = mx;
        g.lastY = my;
        return 0;
    }
    case WM_MOUSEWHEEL: {
        int dz = (int)(short)HIWORD(wp);
        g.cam.dist = clampf(g.cam.dist * (dz > 0 ? 0.9f : 1.1f), 0.6f, 12.0f);
        return 0;
    }
    }
    return DefWindowProcA(h, msg, wp, lp);
}

static void render() {
    g.renderer.draw(g.cloth, g.cols, g.cam, g.opt, g.width, g.height);

    g.hud.begin(g.width, g.height);
    const Vec3 white(0.88f, 0.90f, 0.93f);
    const Vec3 dim(0.62f, 0.66f, 0.72f);
    const Vec3 accent(0.95f, 0.72f, 0.32f);
    const Vec3 red(0.95f, 0.35f, 0.30f);

    if (g.showPanel) {
        g.hud.rect(10, 10, 630, 186, Vec3(0, 0, 0), 0.42f);
        g.hud.rectOutline(10, 10, 630, 186, Vec3(0.3f, 0.35f, 0.42f), 0.5f);
        float y = 18;
        g.hud.textf(20, y, 1.15f, accent, "ClothLab  |  %s", g.title.c_str());
        y += 24;
        const char* solver = g.cloth.par.solver == 0 ? "PBD / Verlet" : "explicit Euler";
        g.hud.textf(20, y, 1.0f, white, "solver: %s   iters: %d   substeps: %d   fps: %.0f",
                    solver, g.cloth.par.iterations, g.cloth.par.substeps, g.fps);
        y += 18;
        g.hud.textf(20, y, 1.0f, white, "grid: %d x %d   (%d points, %d springs)",
                    g.cloth.par.nx, g.cloth.par.ny, (int)g.cloth.pos.size(),
                    (int)g.cloth.springs.size());
        y += 18;
        g.hud.textf(20, y, 1.0f, white, "stiffness: %.2f / %.2f / %.2f   wind: %.1f m/s",
                    g.cloth.par.stiffness[0], g.cloth.par.stiffness[1],
                    g.cloth.par.stiffness[2], g.cloth.par.windStrength);
        y += 18;
        g.hud.textf(20, y, 1.0f, white, "stretch: %.3f   penetration: %.2f mm   contacts: %d",
                    g.cloth.maxStretch, g.cloth.maxPenetration * 1000.0f, g.cloth.contactCount);
        y += 24;
        g.hud.text(20, y, 0.95f, "[1-6] scene  [Space] pause  [N] step  [R] reset  [T] solver", dim);
        y += 16;
        g.hud.text(20, y, 0.95f, "[W] wireframe  [G] shadow  [C] colliders  [H] panel", dim);
        y += 16;
        g.hud.text(20, y, 0.95f, "[J/K] stiffness  [U/I] iterations  [ [ / ] ] wind", dim);
        y += 16;
        g.hud.text(20, y, 0.95f, "[P] screenshot  [F] record frames  [Esc] quit", dim);

        if (g.paused) {
            g.hud.text(g.width - 120.0f, 20.0f, 1.2f, "PAUSED", accent);
        }
        if (g.record) {
            g.hud.rect((float)g.width - 118.0f, 44.0f, 14, 14, red, 1.0f);
            g.hud.textf((float)g.width - 98.0f, 44.0f, 1.0f, red, "REC %d", g.recordFrame);
        }
    }    g.hud.end();
}

static void simulate() {
    g.cloth.colliders = g.cols;
    if (g.paused && !g.stepOnce) return;
    if (g.stepOnce) {
        g.cloth.step(kFixedDt);
        g.stepOnce = false;
        return;
    }
    g.cloth.step(kFixedDt);
}

static void parseArgs(int argc, char** argv) {
    for (int i = 1; i < argc; ++i) {
        std::string a = argv[i];
        auto next = [&](const char* def) -> std::string {
            if (i + 1 < argc) return argv[++i];
            return def;
        };
        if (a == "--scene") g.sceneId = next("flag");
        else if (a == "--width") g.width = atoi(next("1280").c_str());
        else if (a == "--height") g.height = atoi(next("800").c_str());
        else if (a == "--frames") g.frameLimit = atoi(next("-1").c_str());
        else if (a == "--shot") g.shotPath = next("");
        else if (a == "--record") g.recordDir = next("frames");
        else if (a == "--solver") {
            std::string s = next("pbd");
            g.cliSolver = (s == "euler") ? 1 : 0;
        } else if (a == "--iter") g.cliIter = atoi(next("6").c_str());
        else if (a == "--substeps") g.cliSub = atoi(next("6").c_str());
        else if (a == "--k") g.cliK = (float)atof(next("1.0").c_str());
        else if (a == "--wind") g.cliWind = (float)atof(next("7").c_str());
        else if (a == "--bench") g.benchPath = next("bench.csv");
        else if (a == "--wire") g.opt.wireframe = true;
        else if (a == "--no-hud") g.showPanel = false;
        else if (a == "--console") g.console = true;
    }
}

int main(int argc, char** argv) {
    SetProcessDPIAware();
    parseArgs(argc, argv);

    if (!g.console) {
        HWND con = GetConsoleWindow();
        if (con) ShowWindow(con, SW_HIDE);
    }

    if (!g.benchPath.empty()) {
        return runBench(g.benchPath) ? 0 : 1;
    }

    LARGE_INTEGER f;
    QueryPerformanceFrequency(&f);
    g.qpcFreq = (double)f.QuadPart;

    if (!initWindow()) {
        printf("failed to create window / GL context\n");
        MessageBoxA(nullptr, "Failed to create the OpenGL window.", "ClothLab", MB_ICONERROR);
        return 1;
    }
    if (!g.renderer.init()) {
        printf("renderer init failed\n");
        return 1;
    }
    if (!g.hud.init()) {
        printf("hud init failed\n");
        return 1;
    }

    // Command line overrides must survive the scene reset.
    resetScene(true);
    if (g.cliIter > 0) g.cloth.par.iterations = g.cliIter;
    if (g.cliSub > 0) g.cloth.par.substeps = g.cliSub;
    if (g.cliSolver >= 0) g.cloth.par.solver = g.cliSolver;
    if (g.cliK > 0.0f) g.cloth.par.stiffness[0] = g.cliK;
    if (g.cliWind >= 0.0f) g.cloth.par.windStrength = g.cliWind;

    if (!g.recordDir.empty()) {
        g.record = true;
        CreateDirectoryA(g.recordDir.c_str(), nullptr);
        printf("recording to %s\n", g.recordDir.c_str());
    }

    g.lastTime = nowSeconds();
    MSG msg;
    while (g.running) {
        while (PeekMessageA(&msg, nullptr, 0, 0, PM_REMOVE)) {
            if (msg.message == WM_QUIT) g.running = false;
            TranslateMessage(&msg);
            DispatchMessageA(&msg);
        }
        if (!g.running) break;

        double t = nowSeconds();
        float dt = (float)(t - g.lastTime);
        g.lastTime = t;
        if (dt > 0.25f) dt = 0.25f;
        if (dt > 0.0f) g.fps = (g.fps > 0.0f) ? (g.fps * 0.9f + (1.0f / dt) * 0.1f) : (1.0f / dt);

        if (g.frameLimit > 0) {
            if (!g.paused || g.stepOnce) simulate();
        } else {
            g.accum += dt;
            int guard = 0;
            while (g.accum >= kFixedDt && guard < 6) {
                if (!g.paused || g.stepOnce) simulate();
                g.accum -= kFixedDt;
                ++guard;
            }
        }

        render();

        if (g.record) {
            char buf[512];
            snprintf(buf, sizeof(buf), "%s\\frame_%05d.tga", g.recordDir.c_str(), g.recordFrame++);
            captureTGA(buf, g.width, g.height);
        }

        SwapBuffers(g.hdc);
        ++g.frameCount;

        if (g.frameLimit > 0 && g.frameCount >= g.frameLimit) {
            if (!g.shotPath.empty()) screenshot(g.shotPath);
            break;
        }
    }

    if (!g.shotPath.empty() && g.frameLimit <= 0) screenshot(g.shotPath);

    g.hud.shutdown();
    g.renderer.shutdown();
    wglMakeCurrent(nullptr, nullptr);
    if (g.rc) wglDeleteContext(g.rc);
    if (g.hdc) ReleaseDC(g.hwnd, g.hdc);
    if (g.hwnd) DestroyWindow(g.hwnd);
    return 0;
}









