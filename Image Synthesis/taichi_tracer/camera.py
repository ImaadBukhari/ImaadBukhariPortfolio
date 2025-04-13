import taichi as ti
import taichi.math as tm
import numpy as np

from .ray import Ray


@ti.data_oriented
class Camera:

    def __init__(self, width: int = 128, height: int = 128) -> None:

        # Camera pixel width and height are fixed
        self.width = width
        self.height = height

        # Camera parameters that can be modified are stored as fields
        self.eye = ti.Vector.field(n=3, shape=(), dtype=float)
        self.at = ti.Vector.field(n=3, shape=(), dtype=float)
        self.up = ti.Vector.field(n=3, shape=(), dtype=float)
        self.fov = ti.field(shape=(), dtype=float)

        self.x = ti.Vector.field(n=3, shape=(), dtype=float)
        self.y = ti.Vector.field(n=3, shape=(), dtype=float)
        self.z = ti.Vector.field(n=3, shape=(), dtype=float)

        self.camera_to_world = ti.Matrix.field(n=4, m=4, shape=(), dtype=float)

        # Initialize with some default params
        self.set_camera_parameters(
            eye=tm.vec3([0, 0, 5]),
            at=tm.vec3([0, 0, 0]),
            up=tm.vec3([0, 1, 0]),
            fov=60.
            )


    def set_camera_parameters(
        self, 
        eye: tm.vec3 = None, 
        at: tm.vec3 = None, 
        up: tm.vec3 = None, 
        fov: float = None
        ) -> None:

        if eye: self.eye[None] = eye
        if at: self.at[None] = at
        if up: self.up[None] = up
        if fov: self.fov[None] = fov
        self.compute_matrix()


    @ti.kernel
    def compute_matrix(self):

        z_cam = (self.eye[None] - self.at[None]).normalized()  
        x_cam = self.up[None].cross(z_cam).normalized() 
        y_cam = z_cam.cross(x_cam) 

        self.x[None] = x_cam
        self.y[None] = y_cam
        self.z[None] = z_cam

        self.camera_to_world[None] = ti.Matrix([
            [x_cam[0], y_cam[0], z_cam[0], self.eye[None][0]],
            [x_cam[1], y_cam[1], z_cam[1], self.eye[None][1]],
            [x_cam[2], y_cam[2], z_cam[2], self.eye[None][2]],
            [0.0, 0.0, 0.0, 1.0]
        ])


    @ti.func
    def generate_ray(self, pixel_x: int, pixel_y: int, jitter: bool = False) -> Ray:
        
        ndc_coords = self.generate_ndc_coords(pixel_x, pixel_y, jitter)
        world_coords = self.camera_to_world[None] @ self.generate_camera_coords(ndc_coords)     
        
        print(self.eye[None][0], self.eye[None][1], self.eye[None][2])
        ray = Ray()
        ray.origin = self.eye[None] 
        ray.direction = (world_coords.xyz - ray.origin).normalized()
        return ray


    @ti.func
    def generate_ndc_coords(self, pixel_x: int, pixel_y: int, jitter: bool = False) -> tm.vec2:
        
        ndc_x = (2.0 * (pixel_x + 0.5) / self.width) - 1.0
        ndc_y = (2.0 * (pixel_y + 0.5) / self.height) - 1.0 
        return tm.vec2([ndc_x, ndc_y])

    @ti.func
    def generate_camera_coords(self, ndc_coords: tm.vec2) -> tm.vec4:
        
        ratio = self.width / self.height
        scale = ti.tan(0.5 * self.fov[None] * (tm.pi / 180.0))

        cam_x = ndc_coords.x * ratio * scale
        cam_y = ndc_coords.y * scale
        cam_z = -1.0 

        return tm.vec4([cam_x, cam_y, cam_z, 1.0])