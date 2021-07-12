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
    max_volume = 0.2

    # Создание триангуляционной сетки
    tri_mesh = TriMesh.from_contour(contour, facets, max_volume)
    # вывод элементов(треугольников) и узлов сетки
    print(tri_mesh.elements)
    print(tri_mesh.nodes)

    # Взятие топологии
    topology = tri_mesh.get_topology()

    # print(topology.elements_indices)
    # topology.faces: Грани элементов (стороны треугольников).
    # topology.faces_indices : Элементы, состоящие из граней.
    # topology.elements_indices : Индексы элементов.
    # topology.faces2elements : Соответствие грани элементам, которым она принадлежит.
    # topology.act_elements_indices : Индексы активных элементов.

    # ==================================
    # создание U (версия 2)
    sigma = {}
    U = {}
    for i in range(len(topology.elements_indices)):
        U[i] = []
    for i in range(len(tri_mesh.nodes)):
        sigma[i] = []
    # Заполнение sigma(совокупность треугольников для которых V одна из вершин)
    for t in range(len(topology.elements_indices)):
        for v in range(len(tri_mesh.nodes)):
            if tri_mesh.elements[t, 0] == v:
                sigma[v].insert(0, t)
            elif tri_mesh.elements[t, 1] == v:
                sigma[v].insert(1, t)
            elif tri_mesh.elements[t, 2] == v:
                sigma[v].insert(2, t)
    # Заполнение массива U(треугольники соседствующие по определенному ребру)
    for t in range(len(topology.elements_indices)):
        vrem = tri_mesh.elements[t]
        for i in range(3):
            if i == 0:
                a = vrem[0]
                b = vrem[1]
                for x in range(len(topology.elements_indices)):
                    vrem2 = tri_mesh.elements[x]
                    if x != t:
                        if (a == vrem2[0] or a == vrem2[1] or a == vrem2[2]) and (b == vrem2[0] or b == vrem2[1] or b == vrem2[2]):
                            U[t].append(x)
                if len(U[t]) < 1:
                    U[t].append(-1)

            if i == 1:
                a = vrem[1]
                b = vrem[2]
                for x in range(len(topology.elements_indices)):
                    vrem2 = tri_mesh.elements[x]
                    if x != t:
                        if (a == vrem2[0] or a == vrem2[1] or a == vrem2[2]) and (b == vrem2[0] or b == vrem2[1] or b == vrem2[2]):
                            U[t].append(x)
                if len(U[t]) < 2:
                    U[t].append(-1)

            if i == 2:
                a = vrem[0]
                b = vrem[2]
                for x in range(len(topology.elements_indices)):
                    vrem2 = tri_mesh.elements[x]
                    if x != t:
                        if (a == vrem2[0] or a == vrem2[1] or a == vrem2[2]) and (b == vrem2[0] or b == vrem2[1] or b == vrem2[2]):
                            U[t].append(x)
                if len(U[t]) < 3:
                    U[t].append(-1)

    #Версия 1
    # for t in range(len(topology.elements_indices)):
    #     vrem = tri_mesh.elements[t]
    #     for i in range(3):
    #         x = vrem[i]
    #         temp = []
    #         if vrem[0] != x:
    #             temp.insert(0, vrem[0])
    #         if vrem[1] != x:
    #             temp.insert(1, vrem[1])
    #         if vrem[2] != x:
    #             temp.insert(2, vrem[2])

    #         k = temp[0]
    #         m = temp[1]
    #         L = []
    #         sig_k = sigma[k]
    #         sig_m = sigma[m]
    #         for b in range(len(sigma[k])):
    #             for j in range(len(sigma[m])):
    #                 if sig_k[b] == sig_m[j]:
    #                     L.insert(0, sig_k[b])

    #         if L[0] != t:
    #             U[t].insert(i, L[0])
    #         elif len(L) > 1 and L[1] != t:
    #             U[t].insert(i, L[1])
    #         else:
    #             U[t].insert(i, -1)
            # else:
            #     for x in range(15):
            #         countr = 0
            #         if tri_mesh.elements[x, 0] == L[0] or tri_mesh.elements[x, 1] == L[0] or tri_mesh.elements[x, 2] == L[0]:
            #             countr = countr + 1
            #         if len(L) > 1 and (tri_mesh.elements[x, 0] == L[1] or tri_mesh.elements[x, 1] == L[1] or tri_mesh.elements[x, 2] == L[1]):
            #             countr = countr + 1
            #         if x != t and countr > 0:
            #             U[t].insert(i, x)

    #Словарь D (содержит вершины треугольников и номер помеченного ребра)
    D = {}
    for t in range(len(topology.elements_indices)):
        #Нахождение помеченного ребра через координаты
        versh = tri_mesh.elements[t]
        A = tri_mesh.nodes[versh[0]]
        B = tri_mesh.nodes[versh[1]]
        C = tri_mesh.nodes[versh[2]]
        dlina = []
        dlina_ab = np.sqrt((A[0]-B[0])*(A[0]-B[0])+(A[1]-B[1])*(A[1]-B[1]))
        dlina_bc = np.sqrt((C[0]-B[0])*(C[0]-B[0])+(C[1]-B[1])*(C[1]-B[1]))
        dlina_ac = np.sqrt((A[0]-C[0])*(A[0]-C[0])+(A[1]-C[1])*(A[1]-C[1]))
        dlina_srav = 0
        dlina.append(dlina_ab)
        dlina.append(dlina_bc)
        dlina.append(dlina_ac)
        pos = 0
        # Нахождение самого длинного ребра и выбор его как помеченного
        for i in range(3):
            if dlina[i] > dlina_srav:
                dlina_srav = dlina[i]
                pos = i
        # Запись в словарь
        D[t] = ([versh[0], versh[1], versh[2]], pos)

    print(D)
    print(U)
    # ==================================
    #Метод бисекции триангуляции
    V = []
    el = []
    T = list(topology.elements_indices)
    M = T[:]
    C = []
    sig =[]

    #Преобразование массива
    for m in range(len(tri_mesh.nodes)):
        V.insert(m, [])
        V[m].insert(0,tri_mesh.nodes[m, 0])
        V[m].insert(1, tri_mesh.nodes[m, 1])

    #массив сигналов
    for d in range(len(M)):
        sig.append(0)

    # while len(M) > 0:
    #     for i in range(len(M)):
    for c in range(1):
        for i in range(len(M)):
            #Бисекция
            R = []
            temp = 0
            tek = U[i]
            v = D[i]
            mark_edge = v[1]
            neighbor = tek[mark_edge]
            # if tek[0] == -1 or tek[1] == -1 or tek[2] == -1:
            #     neighbor = -1
            # else:
            #     v = D[i]
            #     mark_edge = v[1]
            #     neighbor = tek[mark_edge]
            # нахождение ребра и координат его середины, создание нового узла(вершины), добавление в массив
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

            signal = 0
            for c in range(len(V)):
                if new_v == V[c]:
                    signal = -1
            if signal != -1:
                V.insert(len(V) + i, new_v)
            if sig[i] != 1:
                el.append([f, len(V) - 1, new_vspom[0]])
                el.append([f, len(V) - 1, new_vspom[1]])
                sig[i] = 1


            if len(el) < neighbor:
                if neighbor != -1:
                    vn = tri_mesh.elements[neighbor]
                    m = vn.max()
                    p = 0
                    if vspom[0] == f:
                        p = 0
                    elif vspom[1] == f:
                        p = 1
                    else:
                        p = 2
                    vn = np.delete(vspom, p)
                    if sig[neighbor] != 1:
                        el.append([m, len(V) - 1, vn[0]])
                        el.append([m, len(V) - 1, vn[1]])
                        sig[neighbor] = 1

        # if V[10] == [6, 11, 4] and V[11] == [6, 11, 0]:
            # V[10] = [6, 10, 4]
            # V[11] = [6, 10, 0]
        # Обновление списка треугольников
        while len(T) < len(el):
            l = len(T)
            T.append(l)

        new_elements = np.array(el)
        new_nodes = np.array(V)
        # Новый список U
        for i in range(len(T)):
            U[i] = []

        for i in range(len(V)):
            sigma[i] = []

        for t in range(len(T)):
            for v in range(len(V)):
                if new_elements[t, 0] == v:
                    sigma[v].insert(0, t)
                elif new_elements[t, 1] == v:
                    sigma[v].insert(1, t)
                elif new_elements[t, 2] == v:
                    sigma[v].insert(2, t)

        for t in range(len(T)):
            vrem = el[t]
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

                if L[0] != t:
                    U[t].insert(i, L[0])
                elif len(L) > 1 and L[1] != t:
                    U[t].insert(i, L[1])
                else:
                    U[t].insert(i, -1)

    print(new_elements)
    print(new_nodes)
    print(U)
    #Обратное преобразование массива в numpy
    # new_nodes = np.array(V)
    # new_elements = np.array(el)
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

    mlab.triangular_mesh(new_nodes[:, 0], new_nodes[:, 1], np.array([0] * len(new_nodes)),
                         new_elements, representation='wireframe')

    mlab.show()


if __name__ == '__main__':
    test1()
    print('Finished')
