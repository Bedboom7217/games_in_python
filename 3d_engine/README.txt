This is a CPU-based 3D rendering engine written in C++. This engine has so many other details, so please read the source code that 
gives the clearest account of what the engine does. Here is a file guide if you don't know what each file does:
common.hpp: this is a common file that is used by the rest of the engine, please read the structs inside if you want more details, it 
defines many of the essentials used by the engine.
engine.cpp: this is the core of the engine that unites all the other parts, this is because the files were getting too long and hard 
to work on in one piece.
binding.cpp: this is the source file that uses pybind11 to turn this engine into something that can be used in Python. If you want to 
develop your own games using this engine, this is likely the best instruction manual to the engine.
coordinate_transformation.cpp: this piece of source code is used to turn the models into a common world space, then to camera space
shading.cpp: this contains the shaders of the engine, helps with light sources, no shadows quite yet
project_and_rasterizer.cpp: this is the projection and rasterization phase of the 3D engine, helping turn 3D space into a grid of pixels
that can be displayed on your screen.
*.hpp: these are C++ header files, each one is linked to one .cpp file, look it up if you don't use C++
setup.py: this is a Python file that tells pybind11 what to compile and how to compile it.
pyproject.toml: this is also a file, but in .toml format, that helps with the compilation process. Both it and setup.py are good to
go, but if you want to you can tweak some of the values. I don't recommend decreasing the compiler optimization especially if your 
processor isn't very powerful, I run mine on an AMD Ryzen 5 2600X. 
example.py: this is a minimal example of using the engine, it is a spinning cube rendered in real time
test_render.py: this is a simple test to make sure the engine was working correctly
main.py: this is the main game, it is very simple and not yet a tower, but it will eventually be a zombie-tower game

Setup: I know you are very excited to start using the 3D engine, but there are a few things you need to do first. It is necessary to
install Pygame, pybind11, and NumPy, and also you need to build this engine. Here are the commands you need to run:

pip install pygame, pybind11, numpy
python -m py_compile "d:\ethan\games_in_python\3d_engine\main.py"

To import the engine in Python, use import _engine3d

Also another note: You might notice that this project was pushed to GitHub along with another project called demo_car. I have been working
on this game for quite a while, and I finished before starting this one. However, I had trouble with Git so I couldn't push it earlier.