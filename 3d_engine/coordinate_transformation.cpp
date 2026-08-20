#include <common.hpp>
using namespace std;
#include <array>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <coordinate_transformation.hpp>

// This is the implementation. The .hpp file is very empty and contains only declarations.

Point rotate_point(Point p, Point origin, std::array<float, 3> cosTable, std::array<float, 3> sinTable) {
    // Rotation specified in counterclockwise degrees
    Point2D xy, xz, yz;
    xy.x = p.x - origin.x;
    xy.y = p.y - origin.y;
    xz.x = p.x - origin.x;
    xz.y = p.z - origin.z;
    yz.x = p.y - origin.y;
    yz.y = p.z - origin.z;
    //rotate xy
    Point result;
    result.x = (xy.x * cosTable[0] - xy.y * sinTable[0]) + origin.x;
    result.y = (xy.x * sinTable[0] + xy.y * cosTable[0]) + origin.y;
    result.z = p.z;
    //rotate xz
    float oldX = result.x - origin.x;
    float oldZ = result.z - origin.z;
    result.x = (oldX * cosTable[1] - oldZ * sinTable[1]) + origin.x;
    result.z = (oldX * sinTable[1] + oldZ * cosTable[1]) + origin.z;
    //rotate yz
    float oldY = result.y - origin.y;
    oldZ = result.z - origin.z;
    result.y = (oldY * cosTable[2] - oldZ * sinTable[2]) + origin.y;
    result.z = (oldY * sinTable[2] + oldZ * cosTable[2]) + origin.z;
    return result;
}

Model rotate_model(Model model) {
    if (model.triangle_count > MAX_MODEL_TRIANGLES) {
        fprintf(stderr, "Engine: Too many triangles\n");
        exit(MODEL_TOO_BIG);
    }
    Model result = model;
    Point origin;
    origin.x = 0;
    origin.y = 0;
    origin.z = 0;
    float xycos = cos(model.rotation[0] * M_PI / 180);
    float xysin = sin(model.rotation[0] * M_PI / 180);
    float xzcos = cos(model.rotation[1] * M_PI / 180);
    float xzsin = sin(model.rotation[1] * M_PI / 180);
    float yzcos = cos(model.rotation[2] * M_PI / 180);
    float yzsin = sin(model.rotation[2] * M_PI / 180);
    std::array<float, 3> cosTable = {xycos, xzcos, yzcos};
    std::array<float, 3> sinTable = {xysin, xzsin, yzsin};
    for (int i=0; i<model.triangle_count; i++) {
        result.triangles[i].v1 = rotate_point(model.triangles[i].v1, origin, cosTable, sinTable);
        result.triangles[i].v2 = rotate_point(model.triangles[i].v2, origin, cosTable, sinTable);
        result.triangles[i].v3 = rotate_point(model.triangles[i].v3, origin, cosTable, sinTable);
    }
    return result;
}

BigModel rotate_big_model(BigModel model) {
    if (model.triangle_count > MAX_BIG_MODEL_TRIANGLES) {
        fprintf(stderr, "Engine: Too many triangles\n");
        exit(MODEL_TOO_BIG);
    }
    BigModel result = model;
    Point origin;
    origin.x = 0;
    origin.y = 0;
    origin.z = 0;
    float xycos = cos(model.rotation[0] * M_PI / 180);
    float xysin = sin(model.rotation[0] * M_PI / 180);
    float xzcos = cos(model.rotation[1] * M_PI / 180);
    float xzsin = sin(model.rotation[1] * M_PI / 180);
    float yzcos = cos(model.rotation[2] * M_PI / 180);
    float yzsin = sin(model.rotation[2] * M_PI / 180);
    std::array<float, 3> cosTable = {xycos, xzcos, yzcos};
    std::array<float, 3> sinTable = {xysin, xzsin, yzsin};
    for (int i=0; i<model.triangle_count; i++) {
        result.triangles[i].v1 = rotate_point(model.triangles[i].v1, origin, cosTable, sinTable);
        result.triangles[i].v2 = rotate_point(model.triangles[i].v2, origin, cosTable, sinTable);
        result.triangles[i].v3 = rotate_point(model.triangles[i].v3, origin, cosTable, sinTable);
    }
    return result;
}

Hitbox rotate_hitbox(Hitbox hitbox, std::array<int, 3> rotation) {
    Point origin;
    origin.x = 0;
    origin.y = 0;
    origin.z = 0;
    float xycos = cos(rotation[0] * M_PI / 180);
    float xysin = sin(rotation[0] * M_PI / 180);
    float xzcos = cos(rotation[1] * M_PI / 180);
    float xzsin = sin(rotation[1] * M_PI / 180);
    float yzcos = cos(rotation[2] * M_PI / 180);
    float yzsin = sin(rotation[2] * M_PI / 180);
    std::array<float, 3> cosTable = {xycos, xzcos, yzcos};
    std::array<float, 3> sinTable = {xysin, xzsin, yzsin};
    Hitbox result = hitbox;
    for (int i=0; i<8; i++) {
        result.vertices[i] = rotate_point(hitbox.vertices[i], origin, cosTable, sinTable);
    }
    return result;
}

void create_world_model(const std::array<Model, 50>& models, unsigned char model_count, const std::array<BigModel, 25>& big_models, unsigned char big_model_count, const BasePlate& base_plate, WorldModel& out_world) {
    long x1, y1, z1, x2, y2, z2, x3, y3, z3;
    out_world.triangle_count = 0;
    for (int i=0; i<model_count; i++) {
        Model new_model = rotate_model(models[i]);
        for (int j=0; j<models[i].triangle_count; j++) {
            x1 = new_model.location[0] + new_model.triangles[j].v1.x;
            y1 = new_model.location[1] + new_model.triangles[j].v1.y;
            z1 = new_model.location[2] + new_model.triangles[j].v1.z;
            x2 = new_model.location[0] + new_model.triangles[j].v2.x;
            y2 = new_model.location[1] + new_model.triangles[j].v2.y;
            z2 = new_model.location[2] + new_model.triangles[j].v2.z;
            x3 = new_model.location[0] + new_model.triangles[j].v3.x;
            y3 = new_model.location[1] + new_model.triangles[j].v3.y;
            z3 = new_model.location[2] + new_model.triangles[j].v3.z;
            Triangle triangle;
            triangle.v1.x = x1; triangle.v1.y = y1; triangle.v1.z = z1;
            triangle.v2.x = x2; triangle.v2.y = y2; triangle.v2.z = z2;
            triangle.v3.x = x3; triangle.v3.y = y3; triangle.v3.z = z3;
            triangle.color = new_model.triangles[j].color;
            triangle.shading = new_model.triangles[j].shading;
            if (out_world.triangle_count < 100000) 
                out_world.triangles[out_world.triangle_count++] = triangle;
            else {
                fprintf(stderr, "Engine: Too many triangles in world\n");
                exit(TOO_MANY_TRIANGLES_IN_WORLD);
            }
        }
    }
    for (int i=0; i<big_model_count; i++) {
        BigModel new_model = rotate_big_model(big_models[i]);
        for (int j=0; j<big_models[i].triangle_count; j++) {
            x1 = new_model.location[0] + new_model.triangles[j].v1.x;
            y1 = new_model.location[1] + new_model.triangles[j].v1.y;
            z1 = new_model.location[2] + new_model.triangles[j].v1.z;
            x2 = new_model.location[0] + new_model.triangles[j].v2.x;
            y2 = new_model.location[1] + new_model.triangles[j].v2.y;
            z2 = new_model.location[2] + new_model.triangles[j].v2.z;
            x3 = new_model.location[0] + new_model.triangles[j].v3.x;
            y3 = new_model.location[1] + new_model.triangles[j].v3.y;
            z3 = new_model.location[2] + new_model.triangles[j].v3.z;
            Triangle triangle;
            triangle.v1.x = x1; triangle.v1.y = y1; triangle.v1.z = z1;
            triangle.v2.x = x2; triangle.v2.y = y2; triangle.v2.z = z2;
            triangle.v3.x = x3; triangle.v3.y = y3; triangle.v3.z = z3;
            triangle.color = new_model.triangles[j].color;
            triangle.shading = new_model.triangles[j].shading;
            if (out_world.triangle_count < 100000) 
                out_world.triangles[out_world.triangle_count++] = triangle;
            else {
                fprintf(stderr, "Engine: Too many triangles in world\n");
                exit(TOO_MANY_TRIANGLES_IN_WORLD);
            }
        }
    }
    for (int i=0; i<base_plate.triangles.size(); i++) {
        x1 = base_plate.triangles[i].v1.x;
        y1 = base_plate.triangles[i].v1.y;
        z1 = base_plate.triangles[i].v1.z;
        x2 = base_plate.triangles[i].v2.x;
        y2 = base_plate.triangles[i].v2.y;
        z2 = base_plate.triangles[i].v2.z;
        x3 = base_plate.triangles[i].v3.x;
        y3 = base_plate.triangles[i].v3.y;
        z3 = base_plate.triangles[i].v3.z;
        Triangle triangle;
        triangle.v1.x = x1; triangle.v1.y = y1; triangle.v1.z = z1;
        triangle.v2.x = x2; triangle.v2.y = y2; triangle.v2.z = z2;
        triangle.v3.x = x3; triangle.v3.y = y3; triangle.v3.z = z3;
        triangle.color = base_plate.triangles[i].color;
        triangle.shading = base_plate.triangles[i].shading;
        if (out_world.triangle_count < 100000) 
            out_world.triangles[out_world.triangle_count++] = triangle;
        else {
            fprintf(stderr, "Engine: Too many triangles in world\n");
            exit(TOO_MANY_TRIANGLES_IN_WORLD);
        }
    }
}

void create_camera_space(const Camera& camera, const WorldModel& world, CameraSpace& out_camera_space) {
    out_camera_space.camera = camera;
    out_camera_space.triangle_count = 0;
    float xycos = cos(camera.rotation[0] * M_PI / 180);
    float xysin = sin(camera.rotation[0] * M_PI / 180);
    float xzcos = cos(camera.rotation[1] * M_PI / 180);
    float xzsin = sin(camera.rotation[1] * M_PI / 180);
    float yzcos = cos(camera.rotation[2] * M_PI / 180);
    float yzsin = sin(camera.rotation[2] * M_PI / 180);
    std::array<float, 3> cosTable = {xycos, xzcos, yzcos};
    std::array<float, 3> sinTable = {xysin, xzsin, yzsin};
    Point origin;
    origin.x = origin.y = origin.z = 0;
    for (int i=0; i<world.triangle_count; i++) {
        Triangle triangle = world.triangles[i];
        Triangle new_triangle;
        new_triangle.v1.x = triangle.v1.x - camera.location[0];
        new_triangle.v1.y = triangle.v1.y - camera.location[1];
        new_triangle.v1.z = triangle.v1.z - camera.location[2];
        new_triangle.v2.x = triangle.v2.x - camera.location[0];
        new_triangle.v2.y = triangle.v2.y - camera.location[1];
        new_triangle.v2.z = triangle.v2.z - camera.location[2];
        new_triangle.v3.x = triangle.v3.x - camera.location[0];
        new_triangle.v3.y = triangle.v3.y - camera.location[1];
        new_triangle.v3.z = triangle.v3.z - camera.location[2];
        new_triangle.v1 = rotate_point(new_triangle.v1, origin, cosTable, sinTable);
        new_triangle.v2 = rotate_point(new_triangle.v2, origin, cosTable, sinTable);
        new_triangle.v3 = rotate_point(new_triangle.v3, origin, cosTable, sinTable);
        new_triangle.color = triangle.color;
        new_triangle.shading = triangle.shading;
        out_camera_space.triangles[out_camera_space.triangle_count++] = new_triangle;
    }
}

void create_hitbox_space(const Camera& camera, const std::vector<Hitbox>& hitboxes, unsigned char hitbox_count, HitboxSpace& out_hitbox_space) {
    out_hitbox_space.camera = camera;
    out_hitbox_space.hitbox_count = hitbox_count;
    for (unsigned char i=0; i<hitbox_count; i++) {
        for (int j=0; j<8; j++) {
            out_hitbox_space.hitboxes[i].vertices[j].x = hitboxes[i].vertices[j].x - camera.location[0];
            out_hitbox_space.hitboxes[i].vertices[j].y = hitboxes[i].vertices[j].y - camera.location[1];
            out_hitbox_space.hitboxes[i].vertices[j].z = hitboxes[i].vertices[j].z - camera.location[2];
        }
        out_hitbox_space.hitboxes[i] = rotate_hitbox(out_hitbox_space.hitboxes[i], camera.rotation);
        out_hitbox_space.hitboxes[i].id = hitboxes[i].id;
    }
}

std::vector<unsigned char> hitscan_checker(const HitboxSpace& hitbox_space) {
    std::vector<unsigned char> hit_results(75);
    for (unsigned char i=0; i<hitbox_space.hitbox_count; i++) {
        float min_x = INF; float max_x = -INF; float min_y = INF; float max_y = -INF;
        for (int j=0; j<8; j++) {
            if (hitbox_space.hitboxes[i].vertices[j].z <= 0) continue;
            if (hitbox_space.hitboxes[i].vertices[j].x < min_x) min_x = hitbox_space.hitboxes[i].vertices[j].x;
            if (hitbox_space.hitboxes[i].vertices[j].x > max_x) max_x = hitbox_space.hitboxes[i].vertices[j].x;
            if (hitbox_space.hitboxes[i].vertices[j].y < min_y) min_y = hitbox_space.hitboxes[i].vertices[j].y;
            if (hitbox_space.hitboxes[i].vertices[j].y > max_y) max_y = hitbox_space.hitboxes[i].vertices[j].y;
        }
        hit_results[i] = (min_x <= 0 && max_x >= 0 && min_y <= 0 && max_y >= 0) ? 1 : 0;
    }
    return hit_results;
}