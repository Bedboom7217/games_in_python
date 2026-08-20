#include "common.hpp"
#include "coordinate_transformation.hpp"
#include "shading.hpp"
#include "project_and_rasterizer.hpp"
using namespace std;
#include <pybind11/pybind11.h>
#include <array>
#include <memory>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <limits>

// Global state for the 3D engine
std::array<Model, 50> global_models;
unsigned char global_model_count;
std::array<BigModel, 25> global_big_models;
std::array<Hitbox, 75> global_hitboxes;
unsigned char global_hitbox_count = 0;
unsigned char global_big_model_count;
namespace py = pybind11;
Camera primary_camera;
BasePlate global_base_plate;
unsigned char global_ambient_light;
std::array<LightSource, 10> global_light_sources;
unsigned char global_light_source_count;

void add_model(Model model) {
    if (model.triangle_count > MAX_MODEL_TRIANGLES) {
        fprintf(stderr, "Engine: Model passed too big\n");
        exit(MODEL_TOO_BIG);
    }
    model.id = global_model_count;
    global_models[global_model_count++] = model;
}

void add_big_model(BigModel model) {
    if (model.triangle_count > MAX_BIG_MODEL_TRIANGLES) {
        fprintf(stderr, "Engine: Big model passed too big\n");
        exit(MODEL_TOO_BIG);
    }
    model.id = global_big_model_count;
    global_big_models[global_big_model_count++] = model;
}

void add_base_plate(BasePlate base_plate) {
    global_base_plate = base_plate;
}

void update_model(unsigned char id, Model new_model) {
    global_models[id] = new_model;
}

void update_big_model(unsigned char id, BigModel new_model) {
    global_big_models[id] = new_model;
}

void update_camera(Camera camera) {
    primary_camera = camera;
}

void add_light_source(LightSource light_source) {
    light_source.id = global_light_source_count;
    global_light_sources[global_light_source_count++] = light_source;
}

void update_light_source(unsigned char id, LightSource new_light_source) {
    global_light_sources[id] = new_light_source;
}

void update_ambient_light(unsigned char new_ambient_light) {
    global_ambient_light = new_ambient_light;
}

void add_hitbox(Hitbox hitbox) {
    hitbox.id = global_hitbox_count;
    global_hitboxes[global_hitbox_count++] = hitbox;
}

void update_hitbox(unsigned char id, Hitbox new_hitbox) {
    global_hitboxes[id] = new_hitbox;
}

void check_hitscan(const std::vector<Hitbox>& hitboxes, const Camera& camera, std::vector<unsigned char>& results) {
    HitboxSpace hitbox_space;
    create_hitbox_space(camera, hitboxes, hitboxes.size(), hitbox_space);
    results = hitscan_checker(hitbox_space);
}

std::vector<uint32_t> render() {
    auto world = std::make_unique<WorldModel>();
    create_world_model(global_models, global_model_count, global_big_models, global_big_model_count, global_base_plate, *world);
    auto camera_space = std::make_unique<CameraSpace>();
    create_camera_space(primary_camera, *world, *camera_space);
    shade_world(*camera_space, global_light_sources, global_light_source_count, global_ambient_light);
    return project_rasterize_triangles(*camera_space, primary_camera.fov);
}