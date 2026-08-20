#pragma once
#ifndef BINDING_HPP
#define BINDING_HPP

#include <common.hpp>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <array>
#include <vector>
#include <algorithm>
// Function declarations for binding functions
void add_model(Model model);
void add_big_model(BigModel model);
void add_base_plate(BasePlate base_plate);
void update_model(unsigned char id, Model new_model);
void update_big_model(unsigned char id, BigModel new_model);
void update_camera(Camera camera);
void add_light_source(LightSource light_source);
void update_light_source(unsigned char id, LightSource new_light_source);
void update_ambient_light(unsigned char new_ambient_light);
void add_hitbox(Hitbox hitbox);
void update_hitbox(unsigned char id, Hitbox new_hitbox);
std::vector<uint32_t> render();
void check_hitscan(const std::vector<Hitbox>& hitboxes, const Camera& camera, std::vector<unsigned char>& results);
#endif // BINDING_HPP