// scene.h - scene presets (cloth geometry, pins, colliders, camera)
#pragma once
#include "cloth.h"
#include "renderer.h"
#include <string>
#include <vector>

struct SceneDef {
    const char* id;
    const char* title;
};

const std::vector<SceneDef>& sceneList();

// Build a scene into cloth/colliders/camera. Returns false for an unknown id.
bool buildScene(const std::string& id, Cloth& cloth, std::vector<Collider>& cols,
                Camera& cam, std::string& title);
