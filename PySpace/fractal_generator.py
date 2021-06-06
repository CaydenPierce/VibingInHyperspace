#!/usr/bin/env python

import pygame, sys, math, random, os
import numpy as np
import pyspace

from pyspace.coloring import *
from pyspace.fold import *
from pyspace.geo import *
from pyspace.object import *
from pyspace.shader import Shader
from pyspace.camera import Camera

from ctypes import *
from OpenGL.GL import *
from pygame.locals import *

import os
os.environ['SDL_VIDEO_CENTERED'] = '1'

class FractalGen:
    def __init__(self):
        #Size of the window and rendering
        self.win_size = (1280, 720)

        #Maximum frames per second
        self.max_fps = 30

        #Forces an 'up' orientation when True, free-camera when False
        self.gimbal_lock = False

        #Mouse look speed
        self.look_speed = 0.003

        #Use this avoids collisions with the fractal
        self.auto_velocity = True
        self.auto_multiplier = 2.0

        #Maximum velocity of the camera
        self.max_velocity = 2.0

        #Amount of acceleration when moving
        self.speed_accel = 2.0

        #Velocity decay factor when keys are released
        self.speed_decel = 0.6

        self.clicking = False
        self.mouse_pos = None
        self.screen_center = (self.win_size[0]/2, self.win_size[1]/2)
        self.start_pos = [0, 0, 12.0]
        self.vel = np.zeros((3,), dtype=np.float32)
        self.look_x = 0.0
        self.look_y = 0.0

        #----------------------------------------------
        #    When building your own fractals, you can
        # substitute numbers with string placeholders
        # which can be tuned real-time with key bindings.
        #
        # In this example program:
        #    '0'   +Insert  -Delete
        #    '1'   +Home    -End
        #    '2'   +PageUp  -PageDown
        #    '3'   +NumPad7 -NumPad4
        #    '4'   +NumPad8 -NumPad5
        #    '5'   +NumPad9 -NumPad6
        #
        # Hold down left-shift to decrease rate 10x
        # Hold down right-shift to increase rate 10x
        #
        # Set initial values of '0' through '6' below
        #----------------------------------------------
        self.keyvars = [1.5, 1.5, 2.0, 1.0, 1.0, 1.0]

    #----------------------------------------------
    #            Fractal Examples Below
    #----------------------------------------------
    def infinite_spheres(self):
            obj = Object()
            obj.add(FoldRepeatX(2.0))
            obj.add(FoldRepeatY(2.0))
            obj.add(FoldRepeatZ(2.0))
            obj.add(Sphere(0.5, (1.0, 1.0, 1.0), color=(0.9,0.9,0.5)))
            return obj

    def butterweed_hills(self):
            obj = Object()
            obj.add(OrbitInitZero())
            for _ in range(30):
                    obj.add(FoldAbs())
                    obj.add(FoldScaleTranslate(1.5, (-1.0,-0.5,-0.2)))
                    obj.add(OrbitSum((0.5, 0.03, 0.0)))
                    obj.add(FoldRotateX(3.61))
                    obj.add(FoldRotateY(2.03))
            obj.add(Sphere(1.0, color='orbit'))
            return obj

    def mandelbox(self):
            obj = Object()
            obj.add(OrbitInitInf())
            for _ in range(16):
                    obj.add(FoldBox(1.0))
                    obj.add(FoldSphere(0.5, 1.0))
                    obj.add(FoldScaleOrigin(2.0))
                    obj.add(OrbitMinAbs(1.0))
            obj.add(Box(6.0, color='orbit'))
            return obj

    def mausoleum(self):
            obj = Object()
            obj.add(OrbitInitZero())
            for _ in range(8):
                    obj.add(FoldBox(0.34))
                    obj.add(FoldMenger())
                    obj.add(FoldScaleTranslate(3.28, (-5.27,-0.34,0.0)))
                    obj.add(FoldRotateX(math.pi/2))
                    obj.add(OrbitMax((0.42,0.38,0.19)))
            obj.add(Box(2.0, color='orbit'))
            return obj

    def menger(self):
            obj = Object()
            for _ in range(8):
                    obj.add(FoldAbs())
                    obj.add(FoldMenger())
                    obj.add(FoldScaleTranslate(3.0, (-2,-2,0)))
                    obj.add(FoldPlane((0,0,-1), -1))
            obj.add(Box(2.0, color=(.2,.5,1)))
            return obj

    def tree_planet(self):
            obj = Object()
            obj.add(OrbitInitInf())
            for _ in range(30):
                    obj.add(FoldRotateY(0.44))
                    obj.add(FoldAbs())
                    obj.add(FoldMenger())
                    obj.add(OrbitMinAbs((0.24,2.28,7.6)))
                    obj.add(FoldScaleTranslate(1.3, (-2,-4.8,0)))
                    obj.add(FoldPlane((0,0,-1), 0))
            obj.add(Box(4.8, color='orbit'))
            return obj

    def sierpinski_tetrahedron(self):
            obj = Object()
            obj.add(OrbitInitZero())
            for _ in range(9):
                    obj.add(FoldSierpinski())
                    obj.add(FoldScaleTranslate(2, -1))
            obj.add(Tetrahedron(color=(0.8,0.8,0.5)))
            return obj

    def snow_stadium(self):
            obj = Object()
            obj.add(OrbitInitInf())
            for _ in range(30):
                    obj.add(FoldRotateY(3.33))
                    obj.add(FoldSierpinski())
                    obj.add(FoldRotateX(0.15))
                    obj.add(FoldMenger())
                    obj.add(FoldScaleTranslate(1.57, (-6.61, -4.0, -2.42)))
                    obj.add(OrbitMinAbs(1.0))
            obj.add(Box(4.8, color='orbit'))
            return obj

    def test_fractal(self):
            obj = Object()
            obj.add(OrbitInitInf())
            for _ in range(20):
                    obj.add(FoldSierpinski())
                    obj.add(FoldMenger())
                    obj.add(FoldRotateY(math.pi/2))
                    obj.add(FoldAbs())
                    obj.add(FoldRotateZ('0'))
                    obj.add(FoldScaleTranslate(1.89, (-7.10, 0.396, -6.29)))
                    obj.add(OrbitMinAbs((1,1,1)))
            obj.add(Box(6.0, color='orbit'))
            return obj

    # custom fractals ----------------

    def tree_planet_cust(self):
            obj = Object()
            obj.add(OrbitInitInf())
            for _ in range(30):
                    obj.add(FoldRotateY('0'))
                    obj.add(FoldAbs())
                    obj.add(FoldMenger())
                    obj.add(OrbitMinAbs((0.24,2.28,7.6)))
                    obj.add(FoldScaleTranslate('1', (-2,-4.8,0)))
                    obj.add(FoldPlane((0,0,-1), 0))
            obj.add(Box(4.8, color='orbit'))
            return obj

    #----------------------------------------------
    #             Helper Utilities
    #----------------------------------------------
    def interp_data(self, x, f=2.0):
            new_dim = int(x.shape[0]*f)
            output = np.empty((new_dim,) + x.shape[1:], dtype=np.float32)
            for i in range(new_dim):
                    a, b1 = math.modf(float(i) / f)
                    b2 = min(b1 + 1, x.shape[0] - 1)
                    output[i] = x[int(b1)]*(1-a) + x[int(b2)]*a
            return output

    def make_rot(self, angle, axis_ix):
            s = math.sin(angle)
            c = math.cos(angle)
            if axis_ix == 0:
                    return np.array([[ 1,  0,  0],
                                                     [ 0,  c, -s],
                                                     [ 0,  s,  c]], dtype=np.float32)
            elif axis_ix == 1:
                    return np.array([[ c,  0,  s],
                                                     [ 0,  1,  0],
                                                     [-s,  0,  c]], dtype=np.float32)
            elif axis_ix == 2:
                    return np.array([[ c, -s,  0],
                                                     [ s,  c,  0],
                                                     [ 0,  0,  1]], dtype=np.float32)

    def reorthogonalize(self, mat):
            u, s, v = np.linalg.svd(mat)
            return np.dot(u, v)

    # move the cursor back , only if the window is focused
    def center_mouse(self):
            if pygame.key.get_focused():
                    pygame.mouse.set_pos(self.screen_center)

    def fractal_setup(self):
        pygame.init()
        window = pygame.display.set_mode(self.win_size, OPENGL | DOUBLEBUF)
        pygame.mouse.set_visible(False)
        self.center_mouse()

        #======================================================
        #               Change the fractal here
        #======================================================
        obj_render = self.tree_planet_cust()
        #======================================================

        #======================================================
        #             Change camera settings here
        # See pyspace/camera.py for all camera options
        #======================================================
        self.camera = Camera()
        self.camera['ANTIALIASING_SAMPLES'] = 1
        self.camera['AMBIENT_OCCLUSION_STRENGTH'] = 0.01
        #======================================================

        self.shader = Shader(obj_render)
        self.program = shader.compile(camera)
        print("Compiled!")

        self.matID = glGetUniformLocation(self.program, "iMat")
        self.prevMatID = glGetUniformLocation(self.program, "iPrevMat")
        self.resID = glGetUniformLocation(self.program, "iResolution")
        self.ipdID = glGetUniformLocation(self.program, "iIPD")

        glUseProgram(self.program)
        glUniform2fv(self.resID, 1, win_size)
        glUniform1f(self.ipdID, 0.04)

        fullscreen_quad = np.array([-1.0, -1.0, 0.0, 1.0, -1.0, 0.0, -1.0, 1.0, 0.0, 1.0, 1.0, 0.0], dtype=np.float32)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, fullscreen_quad)
        glEnableVertexAttribArray(0)

        self.mat = np.identity(4, np.float32)
        self.mat[3,:3] = np.array(start_pos)
        self.prevMat = np.copy(mat)
        for i in range(len(keyvars)):
            self.shader.set(str(i), keyvars[i])

        self.frame_num = 0
        clock = pygame.time.Clock()

    def gen_fractal_frame():
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                        sys.exit(0)
                elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_c:
                                pygame.image.save(self.window, 'screenshot.png')
                        elif event.key == pygame.K_ESCAPE:
                                sys.exit(0)

        self.mat[3,:3] += self.vel * (clock.get_time() / 1000)

        if auto_velocity:
                de = obj_render.DE(mat[3]) * auto_multiplier
                if not np.isfinite(de):
                        de = 0.0
        else:
                de = 1e20

        all_keys = pygame.key.get_pressed()

        rate = 0.01
        if all_keys[pygame.K_LSHIFT]:   rate *= 0.1
        elif all_keys[pygame.K_RSHIFT]: rate *= 10.0

        if all_keys[pygame.K_INSERT]:   self.keyvars[0] += rate; print(self.keyvars)
        if all_keys[pygame.K_DELETE]:   self.keyvars[0] -= rate; print(self.keyvars)
        if all_keys[pygame.K_HOME]:     self.keyvars[1] += rate; print(self.keyvars)
        if all_keys[pygame.K_END]:      self.keyvars[1] -= rate; print(self.keyvars)
        if all_keys[pygame.K_PAGEUP]:   self.keyvars[2] += rate; print(self.keyvars)
        if all_keys[pygame.K_PAGEDOWN]: self.keyvars[2] -= rate; print(self.keyvars)
        if all_keys[pygame.K_KP7]:      self.keyvars[3] += rate; print(self.keyvars)
        if all_keys[pygame.K_KP4]:      self.keyvars[3] -= rate; print(self.keyvars)
        if all_keys[pygame.K_KP8]:      self.keyvars[4] += rate; print(self.keyvars)
        if all_keys[pygame.K_KP5]:      self.keyvars[4] -= rate; print(self.keyvars)
        if all_keys[pygame.K_KP9]:      self.keyvars[5] += rate; print(self.keyvars)
        if all_keys[pygame.K_KP6]:      self.keyvars[5] -= rate; print(self.keyvars)

        self.prev_mouse_pos = mouse_pos
        self.mouse_pos = pygame.mouse.get_pos()
        dx,dy = 0,0
        if prev_mouse_pos is not None:
                self.center_mouse()
                time_rate = (clock.get_time() / 1000.0) / (1 / self.max_fps)
                dx = (self.mouse_pos[0] - self.screen_center[0]) * time_rate
                dy = (self.mouse_pos[1] - self.screen_center[1]) * time_rate

        if pygame.key.get_focused():
                if self.gimbal_lock:
                        self.look_x += dx * self.look_speed
                        self.look_y += dy * self.look_speed
                        self.look_y = min(max(look_y, -math.pi/2), math.pi/2)

                        rx = make_rot(self.look_x, 1)
                        ry = make_rot(self.look_y, 0)

                        self.mat[:3,:3] = np.dot(ry, rx)
                else:
                        rx = make_rot(dx * self.look_speed, 1)
                        ry = make_rot(dy * self.look_speed, 0)

                        self.mat[:3,:3] = np.dot(ry, np.dot(rx, self.mat[:3,:3]))
                        self.mat[:3,:3] = reorthogonalize(self.mat[:3,:3])

        acc = np.zeros((3,), dtype=np.float32)
        if all_keys[pygame.K_a]:
                acc[0] -= self.speed_accel / self.max_fps
        if all_keys[pygame.K_d]:
                acc[0] += self.speed_accel / self.max_fps
        if all_keys[pygame.K_w]:
                acc[2] -= self.speed_accel / self.max_fps
        if all_keys[pygame.K_s]:
                acc[2] += self.speed_accel / self.max_fps

        if np.dot(acc, acc) == 0.0:
                vel *= self.speed_decel # TODO
        else:
                vel += np.dot(self.mat[:3,:3].T, acc)
                vel_ratio = min(self.max_velocity, de) / (np.linalg.norm(vel) + 1e-12)
                if vel_ratio < 1.0:
                        vel *= vel_ratio
        if all_keys[pygame.K_SPACE]:
                vel *= 10.0

        for i in range(3):
                self.shader.set(str(i), self.keyvars[i])
        self.shader.set('v', np.array(self.keyvars[3:6]))
        self.shader.set('pos', self.mat[3,:3])

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUniformMatrix4fv(self.matID, 1, False, self.mat)
        glUniformMatrix4fv(self.prevMatID, 1, False, self.prevMat)
        self.prevMat = np.copy(self.mat)

        glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)
        pygame.display.flip()
        clock.tick(self.max_fps)
        frame_num += 1
        print("FPS (fractal0: {}".format(clock.get_fps()))

if __name__ == "__main__":
    fractal_gen = FractalGen()
    fractal_gen.fractal_setup()
    while True:
        fractal_gen.gen_fractal_frame()
