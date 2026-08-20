#pragma once
using namespace std;
#include <pybind11/pybind11.h>
#include <array>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <limits>
#define MAX_MODEL_TRIANGLES 500
#define MAX_BIG_MODEL_TRIANGLES 1500
#define SCREEN_HEIGHT 900
#define SCREEN_WIDTH 1600
#define FOV 105
#define dot(a, b) (a.x*b.x + a.y*b.y + a.z*b.z)
#define max(a, b) ((a)>(b)?(a):(b))
#define min(a, b) ((a)>(b)?(b):(a))
#define INF std::numeric_limits<float>::infinity()
#define M_PI 3.1415926f

enum EngineError {
    MODEL_TOO_BIG,
    TOO_MANY_TRIANGLES_IN_WORLD,
    INVALID_MODEL_DATA
};

struct Point2D {
    float x, y;
};

struct Point {
    float x, y, z;
};

struct Triangle {
    Point v1, v2, v3;
    std::array<unsigned char, 3> color;
    unsigned char shading = 0;
};

struct Triangle2D {
    Point2D v1, v2, v3;
    std::array<unsigned char, 3> color;
};

struct Model {
    Triangle triangles[MAX_MODEL_TRIANGLES];
    unsigned char id;
    int triangle_count=0;
    std::array<int, 3> rotation;
    std::array<long, 3> location;
};


struct BigModel {
    Triangle triangles[MAX_BIG_MODEL_TRIANGLES];
    unsigned char id;
    int triangle_count=0;
    std::array<int, 3> rotation;
    std::array<long, 3> location;
};

struct WorldModel {
    std::array<Triangle, 100000> triangles;
    long triangle_count=0;
};

struct BasePlate {
    std::array<Triangle, 2> triangles;
    long length;
    long width;
};

struct Camera {
    std::array<long, 3> location;
    std::array<int, 3> rotation;
    int fov;
};

struct CameraSpace {
    Camera camera;
    std::array<Triangle, 100000> triangles;
    long triangle_count=0;
};

struct LightSource {
    std::array<long, 3> location;
    std::array<int, 3> rotation;
    int intensity;
    int degrees;
    unsigned char id;
};

struct Hitbox {
    std::array<Point, 8> vertices;
    unsigned char id;
};

struct HitboxSpace {
    // Essentially camera space but for hitboxes, used for collision detection
    Camera camera;
    std::array<Hitbox, 75> hitboxes;
    unsigned char hitbox_count=0;
};