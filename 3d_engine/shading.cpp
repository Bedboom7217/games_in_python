#include <common.hpp>
using namespace std;
#include <array>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <shading.hpp>

Point cross(Point a, Point b) {
    Point new_point;
    new_point.x = a.y*b.z - a.z*b.y;
    new_point.y = a.z*b.x - a.x*b.z;
    new_point.z = a.x*b.y - a.y*b.x;
    return new_point;
}

Point normalize(Point p) {
    float len = sqrt(dot(p, p));
    if (len == 0.0f) len = 1.0f;
    Point out;
    out.x = p.x / len;
    out.y = p.y / len;
    out.z = p.z / len;
    return out;
}

void shade_world(CameraSpace& camera_space, const std::array<LightSource, 10>& light_sources, unsigned char light_sources_count, unsigned char ambient) {
    // initialize ambient shading for all triangles
    for (long j = 0; j < camera_space.triangle_count; j++) {
        camera_space.triangles[j].shading = ambient;
    }
    for (unsigned char i = 0; i < light_sources_count; i++) {
        const LightSource &light = light_sources[i];
        for (long j = 0; j < camera_space.triangle_count; j++) {
            // skip triangles behind camera (simple check)
            if (camera_space.triangles[j].v1.z <= 0 && camera_space.triangles[j].v2.z <= 0 && camera_space.triangles[j].v3.z <= 0) continue;
            // triangle centroid
            float cx = (camera_space.triangles[j].v1.x + camera_space.triangles[j].v2.x + camera_space.triangles[j].v3.x) / 3.0f;
            float cy = (camera_space.triangles[j].v1.y + camera_space.triangles[j].v2.y + camera_space.triangles[j].v3.y) / 3.0f;
            float cz = (camera_space.triangles[j].v1.z + camera_space.triangles[j].v2.z + camera_space.triangles[j].v3.z) / 3.0f;

            // triangle normal
            Point e1, e2, n;
            e1.x = camera_space.triangles[j].v2.x - camera_space.triangles[j].v1.x;
            e1.y = camera_space.triangles[j].v2.y - camera_space.triangles[j].v1.y;
            e1.z = camera_space.triangles[j].v2.z - camera_space.triangles[j].v1.z;
            e2.x = camera_space.triangles[j].v3.x - camera_space.triangles[j].v1.x;
            e2.y = camera_space.triangles[j].v3.y - camera_space.triangles[j].v1.y;
            e2.z = camera_space.triangles[j].v3.z - camera_space.triangles[j].v1.z;
            n = cross(e1, e2);
            n = normalize(n);

            // Light direction:
            // - positional light: from triangle centroid to the light source
            // - directional light: use the light rotation vector as a constant direction
            Point ldir;
            float falloff = 1.0f;
            bool is_directional_light = (light.location[0] == 0 && light.location[1] == 0 && light.location[2] == 0);

            if (is_directional_light) {
                ldir.x = (float)light.rotation[0];
                ldir.y = (float)light.rotation[1];
                ldir.z = (float)light.rotation[2];
                if (dot(ldir, ldir) == 0.0f) continue;
                ldir = normalize(ldir);
            } else {
                float dx = (float)light.location[0] - cx;
                float dy = (float)light.location[1] - cy;
                float dz = (float)light.location[2] - cz;
                float dist2 = dx*dx + dy*dy + dz*dz;
                float radius2 = (float)light.intensity * (float)light.intensity * 64.0f;
                if (dist2 >= radius2) continue;

                ldir.x = dx;
                ldir.y = dy;
                ldir.z = dz;
                ldir = normalize(ldir);

                falloff = 1.0f - (dist2 / radius2);
                if (falloff < 0.0f) falloff = 0.0f;
            }

            float d = dot(n, ldir);
            float cutoff = cos((float)light.degrees * M_PI / 180.0f);
            if (d <= cutoff) continue;
            float intensity = d; // basic Lambertian
            float contrib = intensity * falloff * (float)light.intensity;
            int add = (int)contrib;
            int current = (int)camera_space.triangles[j].shading;
            int updated = current + add;
            if (updated > 255) updated = 255;
            camera_space.triangles[j].shading = (unsigned char)updated;
        }
    }
}