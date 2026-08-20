#pragma once
#ifndef SHADING_HPP
#define SHADING_HPP

#include <common.hpp>
using namespace std;
#include <array>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

// Function declarations for shading functions
Point cross(Point a, Point b);
Point normalize(Point p);
void shade_world(CameraSpace& camera_space, const std::array<LightSource, 10>& light_sources, unsigned char light_sources_count, unsigned char ambient);
#endif // SHADING_HPP