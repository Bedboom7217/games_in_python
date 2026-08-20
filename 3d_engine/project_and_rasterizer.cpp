#include <common.hpp>
using namespace std;
#include <array>
#include <cmath>
#include <vector>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <limits>
#include <algorithm>
#include <project_and_rasterizer.hpp>

Point2D project_point(Point point, float focalLength, float aspect) {
    Point2D new_point;
    new_point.x = (point.x / point.z) * focalLength + SCREEN_WIDTH / 2.0f;
    new_point.y = (-point.y / point.z) * focalLength * aspect + SCREEN_HEIGHT / 2.0f;
    return new_point;
}

inline float edge(Point2D a, Point2D b, Point2D p) {
    return (p.x-a.x) * (b.y-a.y) - (p.y-a.y) * (b.x-a.x);
}

inline bool is_front_facing_camera_space(const Triangle& tri) {
    Point a = tri.v1;
    Point b = tri.v2;
    Point c = tri.v3;
    float ux = b.x - a.x;
    float uy = b.y - a.y;
    float uz = b.z - a.z;
    float vx = c.x - a.x;
    float vy = c.y - a.y;
    float vz = c.z - a.z;
    float nx = uy * vz - uz * vy;
    float ny = uz * vx - ux * vz;
    float nz = ux * vy - uy * vx;
    return nz < 0.0f;
}

std::vector<uint32_t> project_rasterize_triangles(const CameraSpace& camera_space, unsigned char fov) {
    float fovRadians = fov * M_PI / 180.0f;
    float focalLength = (SCREEN_WIDTH/2.0f) / tan(fovRadians/2.0f);
    float aspect = SCREEN_WIDTH / (float)SCREEN_HEIGHT;
    std::vector<float> z_buffer(SCREEN_WIDTH * SCREEN_HEIGHT, INF);
    std::vector<uint32_t> framebuffer(SCREEN_WIDTH * SCREEN_HEIGHT, 0u);
    Point2D ppoint;

    struct VisibleTriangle {
        const Triangle* tri;
        float avgDepth;
    };

    std::vector<VisibleTriangle> visible;
    visible.reserve(camera_space.triangle_count);

    for (long i = 0; i < camera_space.triangle_count; i++) {
        const Triangle& tri = camera_space.triangles[i];
        // reject triangles that are entirely behind the camera
        if (tri.v1.z <= 0 && tri.v2.z <= 0 && tri.v3.z <= 0) continue;
        // back-face culling
        if (!is_front_facing_camera_space(tri)) continue;
        float avgDepth = (tri.v1.z + tri.v2.z + tri.v3.z) / 3.0f;
        visible.push_back({ &tri, avgDepth });
    }

    // sort triangles by average depth (farther triangles first)
    std::sort(visible.begin(), visible.end(), [](const VisibleTriangle& a, const VisibleTriangle& b) {
        return a.avgDepth > b.avgDepth;
    });

    for (const auto& item : visible) {
        const Triangle& tri = *item.tri;
        Triangle2D t;
        ppoint = project_point(tri.v1, focalLength, aspect);
        t.v1 = ppoint;
        ppoint = project_point(tri.v2, focalLength, aspect);
        t.v2 = ppoint;
        ppoint = project_point(tri.v3, focalLength, aspect);
        t.v3 = ppoint;
        // skip triangles with invalid projected coordinates (avoid INF/NaN from divide-by-zero)
        if (!std::isfinite(t.v1.x) || !std::isfinite(t.v1.y) ||
            !std::isfinite(t.v2.x) || !std::isfinite(t.v2.y) ||
            !std::isfinite(t.v3.x) || !std::isfinite(t.v3.y)) continue;
        float area = edge(t.v1, t.v2, t.v3);
        if (area == 0.0f) continue;
        int minX = (int)floor(min(min(t.v1.x, t.v2.x), t.v3.x));
        int minY = (int)floor(min(min(t.v1.y, t.v2.y), t.v3.y));
        int maxX = (int)ceil(max(max(t.v1.x, t.v2.x), t.v3.x));
        int maxY = (int)ceil(max(max(t.v1.y, t.v2.y), t.v3.y));
        // clamp to screen bounds to avoid huge iteration ranges
        if (minX < 0) minX = 0;
        if (minY < 0) minY = 0;
        if (maxX >= SCREEN_WIDTH) maxX = SCREEN_WIDTH - 1;
        if (maxY >= SCREEN_HEIGHT) maxY = SCREEN_HEIGHT - 1;
        for (int x = minX; x <= maxX; x++) {
            for (int y = minY; y <= maxY; y++) {
                if (x < 0 || x >= SCREEN_WIDTH || y < 0 || y >= SCREEN_HEIGHT) continue;
                Point2D p = { (float)x + 0.5f, (float)y + 0.5f };
                float w0 = edge(t.v2, t.v3, p);
                float w1 = edge(t.v3, t.v1, p);
                float w2 = edge(t.v1, t.v2, p);
                if ((w0 >= 0 && w1 >= 0 && w2 >= 0) || (w0 <= 0 && w1 <= 0 && w2 <= 0)) {
                    w0 /= area; w1 /= area; w2 /= area;
                    float z = w0 * tri.v1.z + w1 * tri.v2.z + w2 * tri.v3.z;
                    long index = (long)y * SCREEN_WIDTH + x;
                    if (z < z_buffer[index]) {
                        z_buffer[index] = z;
                        const auto &col = tri.color;
                        unsigned char shading = tri.shading;
                        unsigned char r = (col[0] * shading) / 255;
                        unsigned char g = (col[1] * shading) / 255;
                        unsigned char b = (col[2] * shading) / 255;
                        framebuffer[index] = (0xFFu << 24) | (uint32_t(r) << 16) | (uint32_t(g) << 8) | uint32_t(b);
                    }
                }
            }
        }
    }
    return framebuffer;
}
