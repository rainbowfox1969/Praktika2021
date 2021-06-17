# -*- coding: utf-8 -*-
import numpy as np
from scipy.sparse import coo_matrix, csgraph
from itertools import combinations
from scipy.special import comb


class NMesh:
    def __init__(self, nodes, elements):
        self.nodes = np.array(nodes)
        self.elements = np.array(elements, dtype=np.int32)
        self.layers = {}
        self.scalars = {}

    def add_layer(self, layer_name, layer):
        assert len(layer) == len(self.elements)
        self.layers[layer_name] = np.array(layer, dtype=np.int32)

    def add_scalar(self, scalar_name, scalar):
        assert len(scalar) == len(self.nodes)
        if not (scalar_name in self.scalars):
            self.scalars[scalar_name] = None
        self.scalars[scalar_name] = scalar

    def _get_layers_filter(self, layers, operand='AND'):
        if operand == 'AND':
            layers_filter = np.ones(len(self.elements), dtype=np.bool)
        elif operand == 'OR':
            layers_filter = np.zeros(len(self.elements), dtype=np.bool)
        else:
            assert False

        if layers is None:
            return layers_filter

        for layer_name, layers_values in layers.items():
            if layer_name[:2] == 'OR':
                assert isinstance(layers_values, dict)
                if operand == 'AND':
                    layers_filter &= self._get_layers_filter(layers_values, operand='OR')
                elif operand == 'OR':
                    layers_filter |= self._get_layers_filter(layers_values, operand='OR')
                else:
                    assert False
            elif layer_name[:3] == 'AND':
                assert isinstance(layers_values, dict)
                if operand == 'AND':
                    layers_filter &= self._get_layers_filter(layers_values, operand='AND')
                elif operand == 'OR':
                    layers_filter |= self._get_layers_filter(layers_values, operand='AND')
                else:
                    assert False
            else:
                if layer_name not in self.layers.keys():
                    print('Layer %s not found' % layer_name)
                    assert False
                    # continue
                sub_filter = np.zeros(len(self.elements), dtype=np.bool)
                for layer_value in layers_values:
                    sub_filter |= np.array(self.layers[layer_name]) == layer_value

                if operand == 'AND':
                    layers_filter &= sub_filter
                elif operand == 'OR':
                    layers_filter |= sub_filter
                else:
                    assert False

        return layers_filter

    def get_topology(self, layers=None, deep=-1):
        return NTopology(self, layers, deep)

    def get_scalar_value(self, scalar_name, points_data, layers=None):
        """ Получение значений скаляра в точках.

        Args:
            scalar_name : Имя скаляра.
            points_data : Данные точек, представляющие собой тетраэдры, в которых точки находятся,
                        и соответствующие барицентрические координаты.

        Returns:
            scalar_values : Значения скаляра.

        """
        if not (layers is None):
            layers_filter = self._get_layers_filter(layers)
        # индексы элементов и барицентрические координаты точек в этих элементах. Длины одинаковые
        elements_idcs, elements_volumes = points_data

        # Скаляр в узлах сетки
        scalar = self.scalars[scalar_name]

        # sc_vals = scalar[self.elements[elms_idcs]]
        # Взвешивание
        res = (scalar[self.elements[elements_idcs]] * elements_volumes).sum(axis=1) / elements_volumes.sum(axis=1)
        # res = get_scalar_values(scalar[self.elements[elements_idcs]], elements_volumes)

        # бланкуем там где элементы не заданы
        res[elements_idcs == -1] = np.nan

        # бланкуем неактивные элементы
        if not (layers is None):
            res[~layers_filter[elements_idcs]] = np.nan

        return res

    def get_baricentric_coords(self, points, elements):
        # should be implemented in a subclass
        assert False



class NTopology:
    def __init__(self, mesh, layers=None, deep=-1):
        """Нахождение граней(общих вершин, ребер или треугольников) элементов.

        Args:
            layers : Словарь выбранных слоев.
            deep: Параметр, при значении -1 возвращаются треугольники тетраэдра,
                   -N возвращаются вершины тетраэдра.

        Returns:
            faces : Грани элементов.
            faces_indices : Элементы, состоящие из граней.
            elements_indices : Индексы элементов.
            faces2elements : Соответствие грани элементам, которым она принадлежит.
            act_elements_indices : Индексы активных элементов.

        """

        # получим активные ячейки по фильтру
        layers_filter = mesh._get_layers_filter(layers)

        num_active_elements = layers_filter.sum()

        # число узлов в симплексах
        N = mesh.elements.shape[1]

        # порядок возвращаемых "граней"
        # N = 4, deep = -1, возвращаются треугольники тетраэдра
        # N = 4, deep = -N, возвращаются вершины тетраэдра
        order = N + deep

        num_faces = comb(N, order, exact=True)

        faces_dict = {}
        faces_indices = -np.ones((num_active_elements, num_faces), dtype=np.int32)
        elements_indices = -np.ones(num_active_elements, dtype=np.int32)

        # Для каждой грани узнаем индекс элемента в списке активных элементов
        faces2elements = []

        # uti - unique face identificator
        last_uti = -1
        cur_element_idx = -1

        act_elements_indices = -np.ones(len(mesh.elements), dtype=np.int32)

        # сортируем один по всем элементам индексы вершин по возрастанию, что бы combinations выдавала нам
        # одинаковые грани, по которым можно сопоставлять
        sorted_elements = np.sort(mesh.elements, axis=1)
        for element_index, element in enumerate(sorted_elements):
            if not layers_filter[element_index]:
                continue

            cur_element_idx += 1
            elements_indices[cur_element_idx] = element_index
            act_elements_indices[element_index] = cur_element_idx

            for k, face in enumerate(combinations(element, order)):
                try:
                    uti = faces_dict[face]
                    # print('asdf')
                except KeyError:
                    last_uti += 1
                    faces_dict[face] = last_uti
                    faces2elements.append([])
                    uti = last_uti

                # записываем элементу уникальный номер грани
                faces_indices[cur_element_idx, k] = uti
                faces2elements[uti].append(cur_element_idx)

        faces = np.zeros((len(faces_dict), order), dtype=np.int32)

        for face, uti in faces_dict.items():
            faces[uti, :] = face

        if 0 < len(faces2elements):
            max_num_elements = np.max([len(elements) for elements in faces2elements])
        else:
            max_num_elements = 2
        np_faces2elements = -np.ones((len(faces2elements), max_num_elements), dtype=np.int32)
        for t_face_index, cur_elements in enumerate(faces2elements):
            for t_element_index, cur_element in enumerate(cur_elements):
                np_faces2elements[t_face_index, t_element_index] = cur_element

        self.mesh = mesh
        self.faces = faces
        self.faces_indices = faces_indices
        self.elements_indices = elements_indices
        self.faces2elements = np_faces2elements
        self.act_elements_indices = act_elements_indices
