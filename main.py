import numpy as np
from TriMesh import TriMesh

def test1():
    global vrem
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

    print(topology.elements_indices)
    print(topology.faces2elements)
    # topology.faces: Грани элементов (стороны треугольников).
    # topology.faces_indices : Элементы, состоящие из граней.
    # topology.elements_indices : Индексы элементов.
    # topology.faces2elements : Соответствие грани элементам, которым она принадлежит.
    # topology.act_elements_indices : Индексы активных элементов.

    # ==================================
    # Алгоритм 20 стр99
    sigma = {}
    U = {}
    for i in range(16):
        U[i] = []
    # Строка1
    for i in range(len(tri_mesh.nodes)):
        sigma[i] = []
    # Строка2-4
    for t in range(len(topology.elements_indices)):
        for v in range(len(tri_mesh.nodes)):
            if tri_mesh.elements[t, 0] == v:
                sigma[v].insert(0, t)
            elif tri_mesh.elements[t, 1] == v:
                sigma[v].insert(1, t)
            elif tri_mesh.elements[t, 2] == v:
                sigma[v].insert(2, t)
    # Строка5-7
    for t in range(16):
        vrem = tri_mesh.elements[t]
        for i in range(3):
            x = vrem[i]
            temp = []
            if vrem[0] != x:
                temp.insert(0, vrem[0])
            if vrem[1] != x:
                temp.insert(1, vrem[1])
            if vrem[2] != x:
                temp.insert(2, vrem[2])
    # Строка8
            k = temp[0]
            m = temp[1]
            L = []
            sig_k = sigma[k]
            sig_m = sigma[m]
            for i in range(len(sigma[k])):
                for j in range(len(sigma[m])):
                    if sig_k[i] == sig_m[j]:
                        L.insert(0, sig_k[i])
    #Строка9-15
            if L[0] != t:
                U[t].insert(i, L[0])
            elif len(L) > 1 and L[1] != t:
                U[t].insert(i, L[1])
            else:
                U[t].insert(i, -1)
            # else:
            #     for x in range(15):
            #         countr = 0
            #         if tri_mesh.elements[x, 0] == L[0] or tri_mesh.elements[x, 1] == L[0] or tri_mesh.elements[x, 2] == L[0]:
            #             countr = countr + 1
            #         if len(L) > 1 and (tri_mesh.elements[x, 0] == L[1] or tri_mesh.elements[x, 1] == L[1] or tri_mesh.elements[x, 2] == L[1]):
            #             countr = countr + 1
            #         if x != t and countr > 0:
            #             U[t].insert(i, x)
    print(U)
    # ==================================
    #Алгоритм 21 стр100
    V = []
    T = topology.elements_indices
    M = T
    C = []

    #Преобразование массива
    for m in range(len(tri_mesh.nodes)):
        V.insert(m, [])
        V[m].insert(0,tri_mesh.nodes[m, 0])
        V[m].insert(1, tri_mesh.nodes[m, 1])

    # while len(M) > 0:
    #     for i in range(len(M)):
    for c in range(1):
        for i in range(len(M)):
            #Алгоритм 22 стр101================
            # Строка1
            R = []
            temp = 0
            tek = U[i]
            if tek[0] == -1 or tek[1] == -1 or tek[2] == -1:
                neighbor = -1
            else:
                for v in range(3):
                    if tri_mesh.elements[i, v] >= temp:
                        temp = tri_mesh.elements[i, v]
                        mark_edge = v
                        neighbor = tek[mark_edge]

            # Строка2-6
            # if neighbor[1] == neighbor[2]
            # нахождение ребра и координат его середины, создание нового узла(вершины), добваление в массив
            vspom = tri_mesh.elements[i]
            f = vspom.max()
            j = 0
            if vspom[0] == f:
                j = 0
            elif vspom[1] == f:
                j = 1
            else:
                j = 2
            new_vspom = np.delete(vspom, j)
            coord_a = tri_mesh.nodes[new_vspom[0]]
            coord_b = tri_mesh.nodes[new_vspom[1]]
            new_v = [(coord_a[0] + coord_b[0])/2, (coord_a[1] + coord_b[1])/2]

            # np.append(V, new_v)
            signal = 0
            for c in range(len(V)):
                if new_v == V[c]:
                    signal = -1
            if signal != -1:
                # np.append(V, new_v)
                V.insert(len(V) + i, new_v)
    #Обратное преобразование массива в numpy
    New_nodes = np.array(V)
    print(New_nodes)
            #==================================
        #     T.insert()
        #     del M[i], T[i]
        # for z in range(len(T)):
        #     if C[z] == 1:
        #         M.insert(z)
    # ==================================
    # визуализация триангуляции
    from mayavi import mlab
    mlab.triangular_mesh(tri_mesh.nodes[:, 0], tri_mesh.nodes[:, 1], np.array([0] * len(tri_mesh.nodes)),
                         tri_mesh.elements, representation='wireframe')

    # mlab.triangular_mesh(New_nodes[:, 0], New_nodes[:, 1], np.array([0] * len(New_nodes)),
    #                      tri_mesh.elements, representation='wireframe')

    mlab.show()


if __name__ == '__main__':
    test1()
    print('Finished')
