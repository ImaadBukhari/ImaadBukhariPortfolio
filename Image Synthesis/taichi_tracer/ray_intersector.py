from abc import ABC, abstractmethod

import taichi as ti
import taichi.math as tm

from .geometry import Geometry
from .materials import Material
from .ray import Ray, HitData


@ti.data_oriented
class RayIntersector(ABC):

    def __init__(self, geometry: Geometry):
        self.EPSILON = 1e-7
        self.geometry = geometry


    @abstractmethod
    @ti.func
    def query_ray(ray: Ray) -> HitData:
        pass


    @ti.func
    def intersect_triangle(self, ray: Ray, triangle_id: int) -> HitData:

        hit_data = HitData()

        # Grab Vertices
        vert_ids = self.geometry.triangle_vertex_ids[triangle_id-1] - 1  # Vertices are indexed from 1
        v0 = self.geometry.vertices[vert_ids[0]]
        v1 = self.geometry.vertices[vert_ids[1]]
        v2 = self.geometry.vertices[vert_ids[2]]

        # Normals at each vertex
        normal_indices = self.geometry.triangle_normal_ids[triangle_id-1]-1

        normal_0 = self.geometry.normals[normal_indices[0]]
        normal_1 = self.geometry.normals[normal_indices[1]]
        normal_2 = self.geometry.normals[normal_indices[2]]

        # Material of the triangle
        material_id = self.geometry.triangle_material_ids[triangle_id-1]


        e1 = v1 - v0
        e2 = v2 - v0

        thing = ray.direction.cross(e2)
        det = e1.dot(thing)

        if ti.abs(det) < self.EPSILON:
            hit_data.is_hit = False
        else:
            inv = 1.0 / det

            ori = ray.origin - v0
            u = inv * ori.dot(thing)

            if u < 0.0 or u > 1.0:
                hit_data.is_hit = False
            else:
                vec = ori.cross(e1)
                v = inv * ray.direction.dot(vec)

                if v < 0.0 or u + v > 1.0:
                    hit_data.is_hit = False
                else:
                    t = inv * e2.dot(vec)

                    if t >= self.EPSILON:
                        hit_data.is_hit = True
                        hit_data.distance = t
                        is_backfacing = det < 0

                        normal = (1.0 - u - v) * normal_0 + u * normal_1 + v * normal_2
                        normal = normal.normalized()

                        if is_backfacing:
                            normal = -normal 

                        hit_data.is_hit = True
                        hit_data.is_backfacing = is_backfacing
                        hit_data.triangle_id = triangle_id
                        hit_data.barycentric_coords = tm.vec2(u, v)
                        hit_data.normal = normal
                        hit_data.material_id = material_id

        return hit_data


@ti.data_oriented
class BruteForceRayIntersector(RayIntersector):

    def __init__(self, geometry: Geometry) -> None:
        super().__init__(geometry)


    @ti.func
    def query_ray(self, ray: Ray) -> HitData:

        closest_hit = HitData()
        for triangle_id in range(1, self.geometry.n_triangles + 1):
            hit_data = self.intersect_triangle(ray, triangle_id)

            if hit_data.is_hit:
                if (hit_data.distance < closest_hit.distance) or (not closest_hit.is_hit):
                    closest_hit = hit_data

        return closest_hit