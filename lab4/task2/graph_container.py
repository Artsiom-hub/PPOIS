from __future__ import annotations
from typing import Generic, TypeVar, List, Optional, Iterator, Iterable
T = TypeVar("T")


class DirectedGraph(Generic[T]):

    value_type = T
    vertex_type = T
    edge_type = tuple[int, int]

    size_type = int
    difference_type = int
    pointer = T
    reference = T
    const_reference = T

  

    class VertexIterator:
        def __init__(self, graph, index):
            self.graph = graph
            self.index = index

        def __next__(self):
            if self.index >= len(self.graph._vertices):
                raise StopIteration
            v = self.graph._vertices[self.index]
            self.index += 1
            return v

        def __iter__(self):
            return self

    
        def __prev__(self):
            if self.index <= 0:
                raise StopIteration
            self.index -= 1
            return self.graph._vertices[self.index]

    class EdgeIterator:
        def __init__(self, graph, index):
            self.graph = graph
            self.index = index

        def __next__(self):
            if self.index >= len(self.graph._edges):
                raise StopIteration
            e = self.graph._edges[self.index]
            self.index += 1
            return e

        def __iter__(self):
            return self

        def __prev__(self):
            if self.index <= 0:
                raise StopIteration
            self.index -= 1
            return self.graph._edges[self.index]

    class IncidentEdgeIterator:
   
        def __init__(self, graph, v_idx):
            self.graph = graph
            self.v_idx = v_idx
            self.e_idx = 0

        def __next__(self):
            while self.e_idx < len(self.graph._edges):
                e = self.graph._edges[self.e_idx]
                start, end = e
                self.e_idx += 1
                if start == self.v_idx or end == self.v_idx:
                    return e
            raise StopIteration

        def __iter__(self):
            return self

    class AdjacentVertexIterator:

        def __init__(self, graph, v_idx):
            self.graph = graph
            self.v_idx = v_idx
            self.e_idx = 0

        def __next__(self):
            while self.e_idx < len(self.graph._edges):
                start, end = self.graph._edges[self.e_idx]
                self.e_idx += 1
                if start == self.v_idx:
                    return self.graph._vertices[end]
            raise StopIteration

        def __iter__(self):
            return self


    def __init__(self, iterable: Optional[Iterable[T]] = None):
        self._vertices: List[T] = []
        self._edges: List[tuple[int, int]] = []

        if iterable:
            for v in iterable:
                self.add_vertex(v)

 
    def vertex_count(self) -> int:
        return len(self._vertices)

    def edge_count(self) -> int:
        return len(self._edges)

    def has_vertex(self, value: T) -> bool:
        return value in self._vertices

    def has_edge(self, u: T, v: T) -> bool:
        try:
            ui = self._vertices.index(u)
            vi = self._vertices.index(v)
        except ValueError:
            return False
        return (ui, vi) in self._edges

    def add_vertex(self, value: T) -> None:
        if value in self._vertices:
            raise ValueError("vertex already exists")
        self._vertices.append(value)

    def remove_vertex(self, value: T) -> None:
        if value not in self._vertices:
            raise ValueError("vertex not found")
        idx = self._vertices.index(value)


        self._edges = [(u, v) for (u, v) in self._edges if u != idx and v != idx]


        self._vertices.pop(idx)
        new_edges = []
        for (u, v) in self._edges:
            nu = u - (1 if u > idx else 0)
            nv = v - (1 if v > idx else 0)
            new_edges.append((nu, nv))
        self._edges = new_edges

    def add_edge(self, u: T, v: T) -> None:
        ui = self._vertices.index(u)
        vi = self._vertices.index(v)
        if (ui, vi) in self._edges:
            raise ValueError("edge already exists")
        self._edges.append((ui, vi))

    def remove_edge(self, u: T, v: T) -> None:
        ui = self._vertices.index(u)
        vi = self._vertices.index(v)
        try:
            self._edges.remove((ui, vi))
        except ValueError:
            raise ValueError("edge not found")


    def degree_vertex(self, value: T) -> int:
        idx = self._vertices.index(value)
        return sum(1 for u, v in self._edges if u == idx or v == idx)

    def degree_edge(self, u: T, v: T) -> int:
  
        if not self.has_edge(u, v):
            raise ValueError("edge not found")
        return 2

 
    def vertices(self):
        return DirectedGraph.VertexIterator(self, 0)

    def edges(self):
        return DirectedGraph.EdgeIterator(self, 0)

    def incident_edges(self, v: T):
        return DirectedGraph.IncidentEdgeIterator(self, self._vertices.index(v))

    def adjacent_vertices(self, v: T):
        return DirectedGraph.AdjacentVertexIterator(self, self._vertices.index(v))
