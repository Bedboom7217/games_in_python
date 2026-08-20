#pragma once
#ifndef PROJECT_AND_RASTERIZER_HPP
#define PROJECT_AND_RASTERIZER_HPP

#include <common.hpp>
using namespace std;
#include <array>
#include <vector>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <limits>

// Function declarations for project_and_rasterizer functions
Point2D project_point(Point point, float focalLength, float aspect);
std::vector<uint32_t> project_rasterize_triangles(const CameraSpace& camera_space, unsigned char fov);

#endif // PROJECT_AND_RASTERIZER_HPP