#pragma once
#ifndef COORDINATE_TRANSFORMATION_HPP
#define COORDINATE_TRANSFORMATION_HPP 

#include <common.hpp>
using namespace std;
#include <array>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

// Function declarations for coordinate transformation functions
Point rotate_point(Point p, Point origin, std::array<float, 3> cosTable, std::array<float, 3> sinTable);
Model rotate_model(Model model);
BigModel rotate_big_model(BigModel model);
void create_world_model(const std::array<Model, 50>& models, unsigned char model_count, const std::array<BigModel, 25>& big_models, unsigned char big_model_count, const BasePlate& base_plate, WorldModel& out_world);
void create_camera_space(const Camera& camera, const WorldModel& world, CameraSpace& out_camera_space);
void create_hitbox_space(const Camera& camera, const std::vector<Hitbox>& hitboxes, unsigned char hitbox_count, HitboxSpace& out_hitbox_space);
std::vector<unsigned char> hitscan_checker(const HitboxSpace& hitbox_space);

#endif // COORDINATE_TRANSFORMATION_HPP