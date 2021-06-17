# -*- coding: utf-8 -*-
import numpy as np
from NMesh import NMesh


class TriMesh(NMesh):
    @classmethod
    def from_contour(cls, contour, facets, max_square):
        import meshpy.triangle as triag

        # Build mesh
        mesh = triag.MeshInfo()
        mesh.set_points(contour)
        mesh.set_facets(facets)

        mesh_result = triag.build(mesh, max_volume=max_square)

        elements = np.array(mesh_result.elements)
        nodes = np.array(mesh_result.points)

        return cls(nodes, elements)

    def get_baricentric_coords(self, points, elements):
        squares = np.nan + np.ones((len(points), 3))

        for point_index, point in enumerate(points):
            element_index = elements[point_index]

            if element_index == -1:
                continue

            # координаты вершин
            element_nodes = self.nodes[self.elements[element_index]]

            # переносим систему координат в точку
            element_nodes[:, 0] -= point[0]
            element_nodes[:, 1] -= point[1]
            # element_nodes[:, 2] -= point[2]

            for n, [i, j] in enumerate([[1, 2], [2, 0], [0, 1]]):
                dx1, dy1 = element_nodes[i]
                dx2, dy2 = element_nodes[j]

                # смешанные произведения
                squares[point_index, n] = dx1 * dy2 - dx2 * dy1

        return squares
