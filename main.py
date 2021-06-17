import numpy as np
from TriMesh import TriMesh


def test1(mayavi=None, mayavi=None, mayavi=None):
    contour = [[0.0, 0.0],
               [1.0, 0.0],
               [1.0, 1.0],
               [0.0, 1.0],
               ]
    facets = [[0, 1], [1, 2], [2, 3], [3, 0]]
    max_volume = 0.1

    # Создание триангуляционной сетки
    tri_mesh = TriMesh.from_contour(contour, facets, max_volume)

    # вывод элементов(треугольников) и узлов сетки
    print(tri_mesh.elements)
    print(tri_mesh.nodes)

    # Взятие топологии
    topology = tri_mesh.get_topology()

    # topology.faces: Грани элементов (стороны треугольников).
    # topology.faces_indices : Элементы, состоящие из граней.
    # topology.elements_indices : Индексы элементов.
    # topology.faces2elements : Соответствие грани элементам, которым она принадлежит.
    # topology.act_elements_indices : Индексы активных элементов.

    # визуализация триангуляции
    from mayavi import mlab
    mlab.triangular_mesh(tri_mesh.nodes[:, 0], tri_mesh.nodes[:, 1], np.array([0] * len(tri_mesh.nodes)),
                         tri_mesh.elements, representation='wireframe')

    mlab.show()


if __name__ == '__main__':
    test1()
    print('Finished')
