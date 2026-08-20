import pygame, sys
import numpy as np
import _engine3d as engine # A custom C++ 3D engine I made, which is imported as a Python module
# A minimal example to make sure the engine is working.

def main():
    pygame.init()
    display = pygame.display.set_mode((1600, 900))
    pygame.display.set_caption("3D Engine Test")
    clock = pygame.time.Clock()
    running = True
    point1 = engine.Point()
    point1.x = -200
    point1.y = -200
    point1.z = -200
    point2 = engine.Point()
    point2.x = -200
    point2.y = -200
    point2.z = 200
    point3 = engine.Point()
    point3.x = -200
    point3.y = 200
    point3.z = -200
    point4 = engine.Point()
    point4.x = -200
    point4.y = 200
    point4.z = 200
    point5 = engine.Point()
    point5.x = 200
    point5.y = -200
    point5.z = -200
    point6 = engine.Point()
    point6.x = 200
    point6.y = -200
    point6.z = 200
    point7 = engine.Point()
    point7.x = 200
    point7.y = 200
    point7.z = -200
    point8 = engine.Point()
    point8.x = 200
    point8.y = 200
    point8.z = 200
    trigs = [
        engine.Triangle(point1, point2, point3, (255, 0, 0)),
        engine.Triangle(point2, point3, point4, (0, 255, 0)),
        engine.Triangle(point4, point2, point6, (0, 0, 255)),
        engine.Triangle(point4, point6, point8, (255, 255, 0)),
        engine.Triangle(point5, point6, point8, (0, 255, 255)),
        engine.Triangle(point5, point7, point8, (255, 0, 255)),
        engine.Triangle(point1, point2, point5, (255, 255, 255)),
        engine.Triangle(point2, point5, point6, (128, 128, 128)),
        engine.Triangle(point3, point4, point8, (255, 128, 0)),
        engine.Triangle(point3, point7, point8, (0, 128, 255)),
        engine.Triangle(point1, point3, point7, (128, 0, 255)),
        engine.Triangle(point1, point5, point7, (0, 255, 128))]
    running = True
    new_rotation_degrees = 1
    model = engine.Model(trigs, (0, 0, 0), (0, 0, 0))
    engine.add_model(model) # 0 is the ID and the index in the list
    light_source = engine.LightSource((0, -200, -200), (0, 0, -200), 250, 100)
    engine.add_light_source(light_source) # 0 is the ID and the index in the list
    engine.update_ambient_light(0)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        clock.tick(60)
        display.fill((0, 0, 0))
        new_rotation_degrees += 1
        engine.update_ambient_light((new_rotation_degrees % 256)) # Update ambient light to create a pulsing effect
        model = engine.Model(trigs, (new_rotation_degrees, new_rotation_degrees, new_rotation_degrees), (0, 0, 0))
        engine.update_model(0, model) # 0 is the ID and the index in the list
        camera = engine.Camera((0, 0, -1000), (0, 0, 0), 105)
        engine.update_camera(camera)
        frame = engine.render()
        frame = np.transpose(frame)  # Convert from (900, 1600) to (1600, 900)
        pygame.surfarray.blit_array(display, frame)
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()