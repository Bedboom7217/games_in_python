import math
import numpy as np
import pygame
import sys, os
import random
import time
import copy
import _engine3d as engine # A custom C++ 3D engine I made, which is imported as a Python module
from enum import Enum

pygame.init()
# Global variables 
dead = False
models = {}
# Placeholder model
def make_pz_placeholder(rotation, location):
    if hasattr(location, 'x') and hasattr(location, 'y') and hasattr(location, 'z'):
        location = [int(location.x), int(location.y), int(location.z)]
    point1 = engine.Point()
    point1.x = -10
    point1.y = -25
    point1.z = -10
    point2 = engine.Point()
    point2.x = -10
    point2.y = -25
    point2.z = 10
    point3 = engine.Point()
    point3.x = -10
    point3.y = 25
    point3.z = -10
    point4 = engine.Point()
    point4.x = -10
    point4.y = 25
    point4.z = 10
    point5 = engine.Point()
    point5.x = 10
    point5.y = -25
    point5.z = -10
    point6 = engine.Point()
    point6.x = 10
    point6.y = -25
    point6.z = 10
    point7 = engine.Point()
    point7.x = 10
    point7.y = 25
    point7.z = -10
    point8 = engine.Point()
    point8.x = 10
    point8.y = 25
    point8.z = 10
    trigs = [
        engine.Triangle(point1, point2, point3, (255, 0, 255)),
        engine.Triangle(point2, point3, point4, (0, 0, 0)),
        engine.Triangle(point4, point2, point6, (255, 0, 255)),
        engine.Triangle(point4, point6, point8, (0, 0, 0)),
        engine.Triangle(point5, point6, point8, (255, 0, 255)),
        engine.Triangle(point5, point7, point8, (0, 0, 0)),
        engine.Triangle(point1, point2, point5, (255, 0, 255)),
        engine.Triangle(point2, point5, point6, (0, 0, 0)),
        engine.Triangle(point3, point4, point8, (255, 0, 255)),
        engine.Triangle(point3, point7, point8, (0, 0, 0)),
        engine.Triangle(point1, point3, point7, (255, 0, 255)),
        engine.Triangle(point1, point5, point7, (0, 0, 0))]
    return engine.Model(trigs, rotation, location)

def make_weapon_placeholder(rotation, location):
    if hasattr(location, 'x') and hasattr(location, 'y') and hasattr(location, 'z'):
        location = [int(location.x), int(location.y), int(location.z)]
    point1 = engine.Point()
    point1.x = -5
    point1.y = -5
    point1.z = -5
    point2 = engine.Point()
    point2.x = -5
    point2.y = -5
    point2.z = 5
    point3 = engine.Point()
    point3.x = -5
    point3.y = 5
    point3.z = -5
    point4 = engine.Point()
    point4.x = -5
    point4.y = 5
    point4.z = 5
    point5 = engine.Point()
    point5.x = 5
    point5.y = -5
    point5.z = -5
    point6 = engine.Point()
    point6.x = 5
    point6.y = -5
    point6.z = 5
    point7 = engine.Point()
    point7.x = 5
    point7.y = 5
    point7.z = -5
    point8 = engine.Point()
    point8.x = 5
    point8.y = 5
    point8.z = 5
    trigs = [
        engine.Triangle(point1, point2, point3, (255, 0, 255)),
        engine.Triangle(point2, point3, point4, (0, 0, 0)),
        engine.Triangle(point4, point2, point6, (255, 0, 255)),
        engine.Triangle(point4, point6, point8, (0, 0, 0)),
        engine.Triangle(point5, point6, point8, (255, 0, 255)),
        engine.Triangle(point5, point7, point8, (0, 0, 0)),
        engine.Triangle(point1, point2, point5, (255, 0, 255)),
        engine.Triangle(point2, point5, point6, (0, 0, 0)),
        engine.Triangle(point3, point4, point8, (255, 0, 255)),
        engine.Triangle(point3, point7, point8, (0, 0, 0)),
        engine.Triangle(point1, point3, point7, (255, 0, 255)),
        engine.Triangle(point1, point5, point7, (0, 0, 0))]
    return engine.Model(trigs, rotation, location)

zombie_model = make_pz_placeholder([0, 0, 0], [0, 0, 0])
player_model = make_pz_placeholder([0, 0, 0], [0, 0, 0])
weapon_model = make_weapon_placeholder([0, 0, 0], [0, 0, 0])

class Direction(Enum):
    FORWARD = 1
    BACKWARD = 2
    LEFT = 3
    RIGHT = 4
    UP = 5
    DOWN = 6

class Player:
    def __init__(self):
        self.position = engine.Point()
        self.position.x = 0
        self.position.y = 25
        self.position.z = 0
        self.health = 150 
        self.primary_weapon = None
        self.secondary_weapon = None
        self.melee_weapon = None
        self.utility_weapon = None
        self.crouching = False
        self.remaining_jump_height = 0
        self.hitbox = None
        self.hitbox_width = 20
        self.hitbox_height = 50
        self.hitbox_depth = 20
        self.create_hitbox()
        self.rotation = [45, 0, 0]
        self.curr_weapon = None
        self.aiming = False
        self.fall_speed = 0
        self.update_camera()
    
    def create_hitbox(self):
        width = 20
        height = 50 if not self.crouching else 25
        depth = 20
        self.hitbox_width = width
        self.hitbox_height = height
        self.hitbox_depth = depth
        point1 = engine.Point()
        point1.x = self.position.x - width / 2
        point1.y = self.position.y - height / 2
        point1.z = self.position.z - depth / 2
        point2 = engine.Point()
        point2.x = self.position.x - width / 2
        point2.y = self.position.y - height / 2
        point2.z = self.position.z + depth / 2
        point3 = engine.Point()
        point3.x = self.position.x - width / 2
        point3.y = self.position.y + height / 2
        point3.z = self.position.z - depth / 2
        point4 = engine.Point()
        point4.x = self.position.x - width / 2
        point4.y = self.position.y + height / 2
        point4.z = self.position.z + depth / 2
        point5 = engine.Point()
        point5.x = self.position.x + width / 2
        point5.y = self.position.y - height / 2
        point5.z = self.position.z - depth / 2
        point6 = engine.Point()
        point6.x = self.position.x + width / 2
        point6.y = self.position.y - height / 2
        point6.z = self.position.z + depth / 2
        point7 = engine.Point()
        point7.x = self.position.x + width / 2
        point7.y = self.position.y + height / 2
        point7.z = self.position.z - depth / 2
        point8 = engine.Point()
        point8.x = self.position.x + width / 2
        point8.y = self.position.y + height / 2
        point8.z = self.position.z + depth / 2
        hitbox = engine.Hitbox([point1, point2, point3, point4, point5, point6, point7, point8])
        self.hitbox = hitbox

    def update_camera(self):
        camera_position = [int(self.position.x), int(self.position.y), int(self.position.z)]
        self.camera = engine.Camera(camera_position, self.rotation, 105)
        engine.update_camera(self.camera)

    def walk(self, distance, direction):
        rad_yaw = self.rotation[1] * (3.14159265 / 180)  # Convert degrees to radians
        speed_factor = 1 + self.curr_weapon.move_speed / 100
        if direction == Direction.FORWARD:
            self.position.x += distance * speed_factor * math.sin(rad_yaw)
            self.position.z += distance * speed_factor * math.cos(rad_yaw)
        elif direction == Direction.BACKWARD:
            self.position.x -= distance * speed_factor * math.sin(rad_yaw)
            self.position.z -= distance * speed_factor * math.cos(rad_yaw)
        elif direction == Direction.LEFT:
            self.position.x -= distance * speed_factor * math.cos(rad_yaw)
            self.position.z -= distance * speed_factor * math.sin(rad_yaw)
        elif direction == Direction.RIGHT:
            self.position.x += distance * speed_factor * math.cos(rad_yaw)
            self.position.z += distance * speed_factor * math.sin(rad_yaw)

    def jump(self, height, speed, initiate):
        if initiate and self.remaining_jump_height <= 0:
            self.remaining_jump_height = height
            self.fall_speed = 0
        elif self.remaining_jump_height > 0:
            self.position.y += speed
            self.remaining_jump_height -= speed

    def fall(self):
        if self.remaining_jump_height <= 0: 
            if self.position.y > 25:
                if self.fall_speed < 1:
                    self.fall_speed += 0.00333
                self.position.y -= self.fall_speed
            else:
                self.fall_speed = 0
                self.position.y = 25

    def shoot(self):
        if self.curr_weapon is not None:
            self.curr_weapon.shoot(self)
    
    def aim(self):
        if self.curr_weapon is not None:
            unaim = self.curr_weapon.aim()
            self.aiming = unaim # Some weapons cannot aim and the aim button does an ability or nothing at all

    def take_damage(self, amount):
        if amount < 0:
            amount = -amount
        self.health -= amount
        if self.health <= 0:
            self.health = 0
            self.die()

    def die(self):
        global dead
        dead = True

class Zombie:
    def __init__(self, position):
        self.position = engine.Point()
        self.position.x = position[0]
        self.position.y = position[1]
        self.position.z = position[2]
        self.health = 75
        self.hitbox = None
        self.create_hitbox()
        self.rotation = [0, 0, 0]
        self.dead = False
        self.dead_time = None # To avoid model overload, zombies disappear 5 seconds after they die
        self.last_attack_time = 0
        self.active = False

    def create_hitbox(self):
            width = 20
            height = 50
            depth = 20
            point1 = engine.Point()
            point1.x = self.position.x - width / 2
            point1.y = self.position.y - height / 2
            point1.z = self.position.z - depth / 2
            point2 = engine.Point()
            point2.x = self.position.x - width / 2
            point2.y = self.position.y - height / 2
            point2.z = self.position.z + depth / 2
            point3 = engine.Point()
            point3.x = self.position.x - width / 2
            point3.y = self.position.y + height / 2
            point3.z = self.position.z - depth / 2
            point4 = engine.Point()
            point4.x = self.position.x - width / 2
            point4.y = self.position.y + height / 2
            point4.z = self.position.z + depth / 2
            point5 = engine.Point()
            point5.x = self.position.x + width / 2
            point5.y = self.position.y - height / 2
            point5.z = self.position.z - depth / 2
            point6 = engine.Point()
            point6.x = self.position.x + width / 2
            point6.y = self.position.y - height / 2
            point6.z = self.position.z + depth / 2
            point7 = engine.Point()
            point7.x = self.position.x + width / 2
            point7.y = self.position.y + height / 2
            point7.z = self.position.z - depth / 2
            point8 = engine.Point()
            point8.x = self.position.x + width / 2
            point8.y = self.position.y + height / 2
            point8.z = self.position.z + depth / 2
            hitbox = engine.Hitbox([point1, point2, point3, point4, point5, point6, point7, point8])
            self.hitbox = hitbox

    def move(self, player):
        if self.dead:
            return
        dx = self.position.x - player.position.x
        dy = self.position.y - player.position.y
        dz = self.position.z - player.position.z
        dist2 = dx*dx + dy*dy + dz*dz
        range2 = 25000000
        if dist2 <= range2 or self.active:
            self.active = True
            direction = engine.Point()
            direction.x = player.position.x - self.position.x
            direction.y = player.position.y - self.position.y
            direction.z = player.position.z - self.position.z
            length = math.sqrt(direction.x**2 + direction.y**2 + direction.z**2)
            if length > 0:
                direction.x /= length
                direction.y /= length
                direction.z /= length
            dt = 0.016
            speed = 80
            self.position.x += direction.x * speed * dt
            self.position.z += direction.z * speed * dt

    def attack(self, player):
        if self.dead:
            return
        now = time.time()
        if now - self.last_attack_time < 1.0:
            return
        dx = self.position.x - player.position.x
        dy = self.position.y - player.position.y
        dz = self.position.z - player.position.z
        dist2 = dx*dx + dy*dy + dz*dz
        range2 = 324
        if dist2 <= range2:
            player.take_damage(25)
            self.last_attack_time = now

    def take_damage(self, amount):
        if amount < 0:
            amount = -amount
        self.health -= amount
        if self.health <= 0:
            self.health = 0
            self.die()

    def die(self):
        self.dead_time = time.time()
        self.dead = True

#class Projectile:
#    def __init__(self, speed, gravity_affected, width, spread_width, direction, damage):
#        self.direction = direction
#        self.speed = speed
#        self.gravity_affected = gravity_affected
#        self.width = width
#        self.spread_width = spread_width
#        self.damage = damage

class PrimaryWeapon:
    def __init__(self):
        self.damage = 0
        self.move_speed = 0
        self.max_magazine = 0
        self.max_ammo_reserve = 0
        self.magazine = 0
        self.ammo_reserve = 0
        self.reload_time = 0
        self.burst = False
        self.cooldown = 0
        self.burst_cooldown = None
        self.auto = False
        self.projectile = False
        self.gravity_affected = False
        self.projectiles = []
        self.projectile_speed = 0
        self.projectile_width = 0
        self.projectile_spread_width = 0
        self.last_reload_time = 0
        self.last_shot_time = 0
        self.in_burst = False
        self.burst_shots_remaining = 0

    def shoot(self, player):
        if self.magazine == 0:
            self.reload()
        elif not self.projectile and self.last_reload_time + self.reload_time < time.time() and self.last_shot_time + self.cooldown < time.time():
            self.magazine -= 1
            self.last_shot_time = time.time()
            closest_dist2 = float("inf")
            closest_obj = None
            for key in models:
                if not models[key]:
                    continue
                target_obj = key[0] if isinstance(key, (tuple, list)) else key
                if not hasattr(target_obj, "position"):
                    continue
                dx = player.position.x - target_obj.position.x
                dy = player.position.y - target_obj.position.y
                dz = player.position.z - target_obj.position.z
                dist2 = dx*dx + dy*dy + dz*dz
                if dist2 < closest_dist2:
                    closest_dist2 = dist2
                    closest_obj = target_obj
            if closest_obj is not None and isinstance(closest_obj, Zombie):
                closest_obj.take_damage(self.damage)

    def reload(self):
        self.last_reload_time = time.time()
        if self.ammo_reserve >= self.max_magazine:
            self.ammo_reserve -= self.max_magazine
            self.ammo_reserve += self.magazine
            self.magazine = self.max_magazine
        else:
            self.magazine = self.ammo_reserve
            self.ammo_reserve = 0

class DevPrimary(PrimaryWeapon):
    def __init__(self):
        super().__init__()
        self.damage = 12
        self.move_speed = -10
        self.max_magazine = 20
        self.max_ammo_reserve = 100
        self.ammo_reserve = self.max_ammo_reserve
        self.magazine = self.max_magazine
        self.cooldown = 0.15
        self.auto = True


class SecondaryWeapon:
    pass

class MeleeWeapon:
    pass

class UtilityWeapon:
    pass

class Wall:
    def __init__(self, position, width, height, rotation, color):
        # Minor lift keeps the wall from sitting exactly on the floor plane, which can cause
        # coplanar depth-fighting with the base plate.
        self.position = engine.Point()
        self.position.x = position[0]
        self.position.y = position[1] + 0.5
        self.position.z = position[2]
        self.width = width
        self.height = height
        self.depth = 20
        self.rotation = rotation
        self.color = color

        # Build a closed box wall (12 triangles) rather than a 2-triangle slab.
        # This prevents back-side bleed-through and the "see through wall" effect.
        self.p1 = engine.Point(); self.p1.x =  self.width / 2; self.p1.y =  self.height / 2; self.p1.z =  self.depth / 2
        self.p2 = engine.Point(); self.p2.x = -self.width / 2; self.p2.y =  self.height / 2; self.p2.z =  self.depth / 2
        self.p3 = engine.Point(); self.p3.x = -self.width / 2; self.p3.y = -self.height / 2; self.p3.z =  self.depth / 2
        self.p4 = engine.Point(); self.p4.x =  self.width / 2; self.p4.y = -self.height / 2; self.p4.z =  self.depth / 2
        self.p5 = engine.Point(); self.p5.x =  self.width / 2; self.p5.y =  self.height / 2; self.p5.z = -self.depth / 2
        self.p6 = engine.Point(); self.p6.x = -self.width / 2; self.p6.y =  self.height / 2; self.p6.z = -self.depth / 2
        self.p7 = engine.Point(); self.p7.x = -self.width / 2; self.p7.y = -self.height / 2; self.p7.z = -self.depth / 2
        self.p8 = engine.Point(); self.p8.x =  self.width / 2; self.p8.y = -self.height / 2; self.p8.z = -self.depth / 2

        self.t1 = engine.Triangle(self.p1, self.p2, self.p3, self.color)
        self.t2 = engine.Triangle(self.p1, self.p3, self.p4, self.color)
        self.t3 = engine.Triangle(self.p5, self.p8, self.p7, self.color)
        self.t4 = engine.Triangle(self.p5, self.p7, self.p6, self.color)
        self.t5 = engine.Triangle(self.p1, self.p5, self.p6, self.color)
        self.t6 = engine.Triangle(self.p1, self.p6, self.p2, self.color)
        self.t7 = engine.Triangle(self.p3, self.p7, self.p8, self.color)
        self.t8 = engine.Triangle(self.p3, self.p8, self.p4, self.color)
        self.t9 = engine.Triangle(self.p2, self.p6, self.p7, self.color)
        self.t10 = engine.Triangle(self.p2, self.p7, self.p3, self.color)
        self.t11 = engine.Triangle(self.p1, self.p4, self.p8, self.color)
        self.t12 = engine.Triangle(self.p1, self.p8, self.p5, self.color)

        self.model = engine.Model([
            self.t1, self.t2, self.t3, self.t4,
            self.t5, self.t6, self.t7, self.t8,
            self.t9, self.t10, self.t11, self.t12
        ], self.rotation, [int(self.position.x), int(self.position.y), int(self.position.z)])

    def check_collisions(self, player, direction):
        if player.hitbox is None:
            return False

        player_min_x = player.position.x - player.hitbox_width / 2
        player_max_x = player.position.x + player.hitbox_width / 2
        player_min_y = player.position.y - player.hitbox_height / 2
        player_max_y = player.position.y + player.hitbox_height / 2
        player_min_z = player.position.z - player.hitbox_depth / 2
        player_max_z = player.position.z + player.hitbox_depth / 2

        wall_min_x = self.position.x - self.width / 2
        wall_max_x = self.position.x + self.width / 2
        wall_min_y = self.position.y - self.height / 2
        wall_max_y = self.position.y + self.height / 2
        wall_min_z = self.position.z - self.depth / 2
        wall_max_z = self.position.z + self.depth / 2

        if player_max_x < wall_min_x or player_min_x > wall_max_x:
            return False
        if player_max_y < wall_min_y or player_min_y > wall_max_y:
            return False
        if player_max_z < wall_min_z or player_min_z > wall_max_z:
            return False

        return True

class Floor:
    def __init__(self, position, width, depth, rotation, color):
        self.position = engine.Point()
        self.position.x = position[0]
        self.position.y = position[1]
        self.position.z = position[2]
        self.width = width
        self.depth = depth
        self.rotation = rotation
        self.color = color
        self.t1 = engine.Triangle()
        self.t2 = engine.Triangle()
        self.p1 = engine.Point()
        self.p2 = engine.Point()
        self.p3 = engine.Point()
        self.p4 = engine.Point()
        self.p1.x = self.width / 2
        self.p1.y = 0
        self.p1.z = self.depth / 2
        self.p2.x = -self.width / 2
        self.p2.y = 0
        self.p2.z = self.depth / 2
        self.p3.x = -self.width / 2
        self.p3.y = 0
        self.p3.z = -self.depth / 2
        self.p4.x = self.width / 2
        self.p4.y = 0
        self.p4.z = -self.depth / 2
        self.t1.p1 = self.p1
        self.t1.p2 = self.p2
        self.t1.p3 = self.p3
        self.t1.color = self.color
        self.t2.p1 = self.p1
        self.t2.p2 = self.p3
        self.t2.p3 = self.p4
        self.t2.color = self.color

    def check_collisions(self, player):
        if player.hitbox is None:
            return False
        if player.position.y - player.hitbox.height / 2 <= self.position.y + 0.1 and player.position.y + player.hitbox.height / 2 >= self.position.y - 0.1:
            if player.position.x + player.hitbox.width / 2 >= self.position.x - self.width / 2 and player.position.x - player.hitbox.width / 2 <= self.position.x + self.width / 2:
                if player.position.z + player.hitbox.depth / 2 >= self.position.z - self.depth / 2 and player.position.z - player.hitbox.depth / 2 <= self.position.z + self.depth / 2:
                    return True
        return False

class Ladder:
    def __init__(self, position, width, height, rotation):
        self.position = engine.Point()
        self.position.x = position[0]
        self.position.y = position[1]
        self.position.z = position[2]
        self.width = width
        self.height = height
        self.rotation = rotation
        self.t1 = engine.Triangle()
        self.t2 = engine.Triangle()
        self.p1 = engine.Point()
        self.p2 = engine.Point()
        self.p3 = engine.Point()
        self.p4 = engine.Point()
        self.p1.x = self.width / 2
        self.p1.y = self.height / 2
        self.p1.z = 0
        self.p2.x = -self.width / 2
        self.p2.y = self.height / 2
        self.p2.z = 0
        self.p3.x = -self.width / 2
        self.p3.y = -self.height / 2
        self.p3.z = 0
        self.p4.x = self.width / 2
        self.p4.y = -self.height / 2
        self.p4.z = 0
        self.t1.p1 = self.p1
        self.t1.p2 = self.p2
        self.t1.p3 = self.p3
        self.t2.p1 = self.p1
        self.t2.p2 = self.p3
        self.t2.p3 = self.p4
        self.t1.color = (0, 0, 0)
        self.t2.color = (255, 0, 255)
        self.model = engine.Model([self.t1, self.t2], self.rotation, [self.position.x, self.position.y, self.position.z])

    def check_collisions(self, player):
        if player.hitbox is None:
            return False
        if player.position.y - player.hitbox.height / 2 <= self.position.y + self.height / 2 and player.position.y + player.hitbox.height / 2 >= self.position.y - self.height / 2:
            if player.position.x + player.hitbox.width / 2 >= self.position.x - self.width / 2 and player.position.x - player.hitbox.width / 2 <= self.position.x + self.width / 2:
                if player.position.z + player.hitbox.depth / 2 >= self.position.z - 0.1 and player.position.z - player.hitbox.depth / 2 <= self.position.z + 0.1:
                    return True
        return False

class Game:
    def __init__(self):
        self.player = Player()
        self.player.primary_weapon = DevPrimary()
        self.player.curr_weapon = self.player.primary_weapon
        dead = False
        self.spawn_zombies()
        self.place_walls()
        self.walking_direction = None
        self.shooting = False
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)
        self.dx = 0
        self.dy = 0

    def spawn_zombies(self):
        z1 = Zombie((3000, 25, 1000))
        z2 = Zombie((1000, 25, 2000))
        z3 = Zombie((2000, 25, 2000))
        hitboxes = [z1.hitbox, z2.hitbox, z3.hitbox]
        results = engine.check_hitscan(hitboxes, self.player.camera)
        models[(z1, zombie_model)] = results[0]
        models[(z2, zombie_model)] = results[1]
        models[(z3, zombie_model)] = results[2]

    def place_walls(self):
        wall1 = Wall((0, 50, 1000), 2000, 100, [0, 0, 0], (0, 0, 255))
        wall2 = Wall((1000, 50, 2000), 2000, 100, [0, 90, 0], (0, 0, 255))
        wall3 = Wall((2000, 50, 1000), 2000, 100, [0, 180, 0], (0, 0, 255))
        wall4 = Wall((1000, 50, -1000), 2000, 100, [0, 270, 0], (0, 0, 255))
        models[(wall1, None)] = True
        models[(wall2, None)] = True
        models[(wall3, None)] = True
        models[(wall4, None)] = True

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    self.walking_direction = Direction.FORWARD
                elif event.key == pygame.K_s:
                    self.walking_direction = Direction.BACKWARD
                elif event.key == pygame.K_a:
                    self.walking_direction = Direction.LEFT
                elif event.key == pygame.K_d:
                    self.walking_direction = Direction.RIGHT
                elif event.key == pygame.K_SPACE:
                    self.player.jump(30, 0.5, True)
                elif event.key == pygame.K_c:
                    self.player.crouching = not self.player.crouching
                elif event.key == pygame.K_r:
                    self.player.primary_weapon.reload()
            elif event.type == pygame.KEYUP:
                if event.key in [pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d]:
                    self.walking_direction = None
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.player.shoot()
                if self.player.primary_weapon.auto:
                    self.shooting = True
            elif event.type == pygame.MOUSEBUTTONUP:
                self.shooting = False
            elif event.type == pygame.MOUSEMOTION:
                self.dx += event.rel[0]
                self.dy += event.rel[1]

    def update(self):
        global models
        self.handle_input()
        if not dead:
            keys = []
            hitboxes = []
            new_models = models.copy()
            for key in models:
                new_models.pop(key)
                key = list(key)
                if type(key[0]) == Zombie:
                    if getattr(key[0], "dead", False):
                        # Remove zombie from rendering after 5 seconds of being dead
                        if key[0].dead_time is not None and time.time() - key[0].dead_time > 5:
                            continue  # Don't add back to models, effectively removing it
                        # If recently dead, keep rendering the corpse for a short time
                        continue
                    key[0].move(self.player)
                    key[0].attack(self.player)
                    key[0].create_hitbox()
                    key[1] = make_pz_placeholder(key[0].rotation, key[0].position)
                    key = tuple(key)
                    keys.append(key)
                    hitboxes.append(key[0].hitbox)
                elif type(key[0]) == Player:
                    key[0].create_hitbox()
                    key[1] = make_pz_placeholder(key[0].rotation, key[0].position)
                    key = tuple(key)
                    keys.append(key)
                    hitboxes.append(key[0].hitbox)
                elif type(key[0]) == DevPrimary:
                    key[1] = make_weapon_placeholder(key[0].rotation, key[0].position)
                    key = tuple(key)
                    keys.append(key)
                    hitboxes.append(key[0].hitbox)
                elif type(key[0]) == Wall:
                    keys.append((key[0], key[0].model))
                elif type(key[0]) == Floor:
                    keys.append(key)
                    if key[0].check_collisions(self.player):
                        self.player.position.y = key[0].position.y + 25 if not self.player.crouching else key[0].position.y + 12.5
                elif type(key[0]) == Ladder:
                    keys.append(key)
                    if key[0].check_collisions(self.player):
                        if self.walking_direction == Direction.FORWARD:
                            self.player.position.y += 1.5
                            self.player.position.x -= 1.5 * math.sin(self.player.rotation[1] * (3.14159265 / 180))
                            self.player.position.z -= 1.5 * math.cos(self.player.rotation[1] * (3.14159265 / 180))
                        elif self.walking_direction == Direction.BACKWARD:
                            self.player.position.y -= 1.5
                            self.player.position.x += 1.5 * math.sin(self.player.rotation[1] * (3.14159265 / 180))
                            self.player.position.z += 1.5 * math.cos(self.player.rotation[1] * (3.14159265 / 180))
                        elif self.walking_direction == Direction.LEFT:
                            self.player.position.x += 1.5 * math.cos(self.player.rotation[1] * (3.14159265 / 180))
                            self.player.position.z -= 1.5 * math.sin(self.player.rotation[1] * (3.14159265 / 180))
                        elif self.walking_direction == Direction.RIGHT:
                            self.player.position.x -= 1.5 * math.cos(self.player.rotation[1] * (3.14159265 / 180))
                            self.player.position.z += 1.5 * math.sin(self.player.rotation[1] * (3.14159265 / 180))
            models = new_models
            self.player.rotation = [0, self.dx//4, -self.dy//4]
            self.player.update_camera()
            results = engine.check_hitscan(hitboxes, self.player.camera)
            for a, key in enumerate(keys):
                models[tuple(key)] = results[a]
            if self.shooting:
                self.player.shoot()
            if self.walking_direction is not None:
                test_player = copy.copy(self.player)
                test_player.position = engine.Point()
                test_player.position.x = self.player.position.x
                test_player.position.y = self.player.position.y
                test_player.position.z = self.player.position.z
                test_player.walk(1.5, self.walking_direction)
                can_move = True
                for key in list(models.keys()):
                    obj = key[0] if isinstance(key, (tuple, list)) else key
                    if isinstance(obj, Wall) and obj.check_collisions(test_player, self.walking_direction):
                        can_move = False
                        break
                if can_move:
                    self.player.walk(1.5, self.walking_direction)
            self.player.jump(0, 0.5, False)
            self.player.fall()
            self.player.create_hitbox()

class View:
    def __init__(self, game):
        self.screen = pygame.display.set_mode((1600, 900))
        pygame.display.set_caption("Zombie Tower")
        self.game = game
        self.models = []
        self.models_created = 0
        engine.update_ambient_light(255)
        base_plate = engine.BasePlate()
        p1 = engine.Point()
        p1.x = 5000
        p1.y = 0
        p1.z = 5000
        p2 = engine.Point()
        p2.x = -5000
        p2.y = 0
        p2.z = 5000
        p3 = engine.Point()
        p3.x = 5000
        p3.y = 0
        p3.z = -5000
        p4 = engine.Point()
        p4.x = -5000
        p4.y = 0
        p4.z = -5000
        t1 = engine.Triangle(p1, p2, p3, [128, 128, 128])
        t2 = engine.Triangle(p2, p3, p4, [64, 64, 64])
        base_plate.length = 0
        base_plate.width = 0
        base_plate.triangles = [t1, t2]
        engine.add_base_plate(base_plate)

    def update_models(self):
        self.models = []
        for model in models:
            self.models.append(model[1])
        weapon_location = engine.Point()
        weapon_location.x = int(self.game.player.position.x)
        weapon_location.y = int(self.game.player.position.y) + 5
        weapon_location.z = int(self.game.player.position.z)
        rad_yaw = self.game.player.rotation[1] * (3.14159265 / 180)  # Convert degrees to radians
        weapon_location.x += 10 * -1 * math.sin(rad_yaw)
        weapon_location.z += 10 * -1 * math.cos(rad_yaw)
        self.models.append(make_weapon_placeholder(self.game.player.rotation, weapon_location))
        for i, model in enumerate(self.models):
            if self.models_created < i+1:
                engine.add_model(model)
                self.models_created += 1
            else:
                engine.update_model(i, model)

    def render_3d(self):
        frame = engine.render()
        frame = np.transpose(frame)  # Convert from (900, 1600) to (1600, 900)
        pygame.surfarray.blit_array(self.screen, frame)
        
    def draw_hud(self):
        crosshair_size = 16
        if self.game.walking_direction != None:
            crosshair_size += 4
        elif self.game.player.crouching:
            crosshair_size -= 8
        center_dot = pygame.Rect(800, 450, 2, 2)
        left_bar = pygame.Rect(800-crosshair_size-6, 450, 6, 2)
        right_bar = pygame.Rect(800+crosshair_size, 450, 6, 2)
        top_bar = pygame.Rect(800, 450-crosshair_size-6, 2, 6)
        bottom_bar = pygame.Rect(800, 450+crosshair_size, 2, 6)
        pygame.draw.rect(self.screen, (255, 255, 255), center_dot)
        pygame.draw.rect(self.screen, (255, 255, 255), left_bar)
        pygame.draw.rect(self.screen, (255, 255, 255), right_bar)
        pygame.draw.rect(self.screen, (255, 255, 255), top_bar)
        pygame.draw.rect(self.screen, (255, 255, 255), bottom_bar)
        ammo_font = pygame.font.Font(os.path.join("D:/ethan/games_in_python/3d_engine/fonts/HyliaSerifBeta-Regular.otf"), 48)
        reserve_font = pygame.font.Font(os.path.join("D:/ethan/games_in_python/3d_engine/fonts/HyliaSerifBeta-Regular.otf"), 24)
        health_font = pygame.font.Font(os.path.join("D:/ethan/games_in_python/3d_engine/fonts/HyliaSerifBeta-Regular.otf"), 24)
        ammo_surface = ammo_font.render(str(self.game.player.primary_weapon.magazine), False, (255, 255, 255))
        reserve_surface = reserve_font.render(str(self.game.player.primary_weapon.ammo_reserve), False, (255, 255, 255))
        health_surface = health_font.render(f"{self.game.player.health} HP", False, (255, 255, 255))
        ammo_rect = ammo_surface.get_rect(center=(1400, 700))
        reserve_rect = reserve_surface.get_rect(center=(1450, 800))
        health_rect = health_surface.get_rect(center=(50, 800))
        self.screen.blit(ammo_surface, ammo_rect)
        self.screen.blit(reserve_surface, reserve_rect)
        self.screen.blit(health_surface, health_rect)

    def render(self):
        self.screen.fill((0, 0, 0))
        # ensure models are (re)uploaded to the native engine before rendering
        try:
            self.update_models()
        except Exception:
            pass
        self.render_3d()
        self.draw_hud()
        pygame.display.flip()

def main():
    game = Game()
    view = View(game)
    while True:
        game.update()
        view.render()

if __name__ == "__main__":
    main()