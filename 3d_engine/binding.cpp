#include "common.hpp"
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include <array>
#include <vector>
#include <algorithm>
#include <binding.hpp>

namespace py = pybind11;

// Forward declarations of engine functions defined in engine.cpp
extern void add_model(Model model);
extern void add_big_model(BigModel model);
extern void add_base_plate(BasePlate base_plate);
extern void update_model(unsigned char id, Model new_model);
extern void update_big_model(unsigned char id, BigModel new_model);
extern void update_camera(Camera camera);
extern void add_light_source(LightSource light_source);
extern void update_light_source(unsigned char id, LightSource new_light_source);
extern void update_ambient_light(unsigned char new_ambient_light);
extern std::vector<uint32_t> render();

PYBIND11_MODULE(_engine3d, m) {
    py::class_<Point>(m, "Point")
        .def(py::init<>())
        .def_readwrite("x", &Point::x)
        .def_readwrite("y", &Point::y)
        .def_readwrite("z", &Point::z);

    py::class_<Triangle>(m, "Triangle")
        .def(py::init([] (const Point& v1, const Point& v2, const Point& v3, const std::vector<unsigned char>& color) {
            if (color.size() != 3) {
                throw std::runtime_error("Color must have exactly 3 elements");
            }
            Triangle triangle;
            triangle.v1 = v1;
            triangle.v2 = v2;
            triangle.v3 = v3;
            std::copy(color.begin(), color.end(), triangle.color.begin());
            return triangle;
        }))
        .def_readwrite("v1", &Triangle::v1)
        .def_readwrite("v2", &Triangle::v2)
        .def_readwrite("v3", &Triangle::v3)
        .def_readwrite("color", &Triangle::color)
        .def_readwrite("shading", &Triangle::shading);

    py::class_<Model>(m, "Model")
        .def(py::init([](const std::vector<Triangle>& tris, const std::vector<int>& rotation,
                        const std::vector<long>& location) {
            Model model;
            if (tris.size() > MAX_MODEL_TRIANGLES) {
                throw std::runtime_error("Too many triangles for Model");
            }
            model.triangle_count = static_cast<int>(tris.size());
            std::copy(tris.begin(), tris.end(), model.triangles);
            if (rotation.size() != 3 || location.size() != 3) {
                throw std::runtime_error("Rotation and location must have exactly 3 elements");
            }
            std::copy(rotation.begin(), rotation.end(), model.rotation.begin());
            std::copy(location.begin(), location.end(), model.location.begin());
            return model;
        }));

    py::class_<BigModel>(m, "BigModel")
        .def(py::init([](const std::vector<Triangle>& tris, const std::vector<int>& rotation,
                        const std::vector<long>& location) {
            BigModel model;
            if (tris.size() > MAX_BIG_MODEL_TRIANGLES) {
                throw std::runtime_error("Too many triangles for BigModel");
            }
            model.triangle_count = static_cast<int>(tris.size());
            std::copy(tris.begin(), tris.end(), model.triangles);
            if (rotation.size() != 3 || location.size() != 3) {
                throw std::runtime_error("Rotation and location must have exactly 3 elements");
            }
            std::copy(rotation.begin(), rotation.end(), model.rotation.begin());
            std::copy(location.begin(), location.end(), model.location.begin());
            return model;
        }));

    py::class_<BasePlate>(m, "BasePlate")
        .def(py::init<>())
        .def_readwrite("length", &BasePlate::length)
        .def_readwrite("width", &BasePlate::width)
        .def_readwrite("triangles", &BasePlate::triangles);

    py::class_<Camera>(m, "Camera")
        .def(py::init([](const std::array<long, 3>& location, const std::array<int, 3>& rotation, int fov) {
            Camera camera;
            camera.location = location;
            camera.rotation = rotation;
            camera.fov = fov;
            return camera;
        }));

    py::class_<LightSource>(m, "LightSource")
        .def(py::init([](const std::array<long, 3>& location, const std::array<int, 3>& rotation, int intensity, int degrees) {
            LightSource light;
            light.location = location;
            light.rotation = rotation;
            light.intensity = intensity;
            light.degrees = degrees;
            return light;
        }));

    py::class_<Hitbox>(m, "Hitbox")
        .def(py::init([](const std::vector<Point>& vertices) {
            if (vertices.size() != 8) {
                throw std::runtime_error("Hitbox must have exactly 8 vertices");
            }
            Hitbox hitbox;
            std::copy(vertices.begin(), vertices.end(), hitbox.vertices.begin());
            return hitbox;
        }));

    m.doc() = "Bindings for simple CPU 3D engine";
    m.def("add_model", &add_model, "Add a Model to the engine");
    m.def("add_big_model", &add_big_model, "Add a BigModel to the engine");
    m.def("add_base_plate", &add_base_plate, "Set the base plate");
    m.def("add_hitbox", &add_hitbox, "Add a Hitbox to the engine");
    m.def("update_hitbox", &update_hitbox, "Update a hitbox by id");
    m.def("update_model", &update_model, "Update a model by id");
    m.def("update_big_model", &update_big_model, "Update a big model by id");
    m.def("update_camera", &update_camera, "Update the primary camera");
    m.def("add_light_source", &add_light_source, "Add a light source to the engine");
    m.def("update_light_source", &update_light_source, "Update a light source by id");
    m.def("update_ambient_light", &update_ambient_light, "Update the ambient light level");
    m.def("render", [](){
        auto buf = ::render();
        uint32_t* heap_buf = new uint32_t[SCREEN_HEIGHT * SCREEN_WIDTH];
        std::copy(buf.begin(), buf.end(), heap_buf);
        return py::array_t<uint32_t>(
            {SCREEN_HEIGHT, SCREEN_WIDTH},
            {SCREEN_WIDTH * sizeof(uint32_t), sizeof(uint32_t)},
            heap_buf,
            py::capsule(heap_buf, [](void *p) { delete [] reinterpret_cast<uint32_t*>(p); })
        );
    }, "Render the current scene and return a NumPy array framebuffer");
    m.def("check_hitscan", [](const std::vector<Hitbox>& hitboxes, const Camera& camera) {
        std::vector<unsigned char> results;
        check_hitscan(hitboxes, camera, results);
        return results;
    }, "Check hitscan against hitboxes and return results");
}
