import unittest
from graph_container import *


class TestDirectedGraphTypedefs(unittest.TestCase):
    def test_typedefs_exist(self):
        g = DirectedGraph[int]()
        self.assertIs(g.value_type, int)
        self.assertIs(g.vertex_type, int)
        self.assertEqual(g.edge_type, tuple[int, int])
        self.assertIs(g.size_type, int)
        self.assertIs(g.pointer, int)
        self.assertIs(g.reference, int)
        self.assertIs(g.const_reference, int)


class TestVertexIterator(unittest.TestCase):

    def setUp(self):
        self.g = DirectedGraph([10, 20, 30])

    def test_vertex_iterator_forward(self):
        it = DirectedGraph.VertexIterator(self.g, 0)
        self.assertEqual(next(it), 10)
        self.assertEqual(next(it), 20)
        self.assertEqual(next(it), 30)
        with self.assertRaises(StopIteration):
            next(it)

    def test_vertex_iterator_backward(self):
        it = DirectedGraph.VertexIterator(self.g, 3)  
        self.assertEqual(it.__prev__(), 30)
        self.assertEqual(it.__prev__(), 20)
        self.assertEqual(it.__prev__(), 10)
        with self.assertRaises(StopIteration):
            it.__prev__()

    def test_vertex_iterator_iter_protocol(self):
        it = DirectedGraph.VertexIterator(self.g, 0)
        collected = [v for v in it]
        self.assertEqual(collected, [10, 20, 30])


class TestEdgeIterator(unittest.TestCase):

    def setUp(self):
        self.g = DirectedGraph(["A", "B", "C"])
        self.g.add_edge("A", "B")
        self.g.add_edge("B", "C")
        self.g.add_edge("A", "C")

    def test_edge_iterator_forward(self):
        it = DirectedGraph.EdgeIterator(self.g, 0)
        self.assertEqual(next(it), (0, 1))  
        self.assertEqual(next(it), (1, 2))  
        self.assertEqual(next(it), (0, 2))  
        with self.assertRaises(StopIteration):
            next(it)

    def test_edge_iterator_backward(self):
        it = DirectedGraph.EdgeIterator(self.g, 3)
        self.assertEqual(it.__prev__(), (0, 2))
        self.assertEqual(it.__prev__(), (1, 2))
        self.assertEqual(it.__prev__(), (0, 1))
        with self.assertRaises(StopIteration):
            it.__prev__()

    def test_edge_iterator_iter_protocol(self):
        it = DirectedGraph.EdgeIterator(self.g, 0)
        edges = [e for e in it]
        self.assertEqual(edges, [(0, 1), (1, 2), (0, 2)])


class TestIncidentEdgeIterator(unittest.TestCase):

    def setUp(self):
        self.g = DirectedGraph(["A", "B", "C"])
        self.g.add_edge("A", "B")  
        self.g.add_edge("B", "C")  
        self.g.add_edge("C", "A")  

    def test_incident_edges_to_vertex_0(self):
        it = DirectedGraph.IncidentEdgeIterator(self.g, 0)  
        edges = [next(it), next(it)]
        self.assertIn((0, 1), edges)
        self.assertIn((2, 0), edges)
        with self.assertRaises(StopIteration):
            next(it)

    def test_incident_edges_to_vertex_1(self):
        it = DirectedGraph.IncidentEdgeIterator(self.g, 1)  
        e1 = next(it)
        e2 = next(it)
        self.assertIn(e1, [(0, 1), (1, 2)])
        self.assertIn(e2, [(0, 1), (1, 2)])
        with self.assertRaises(StopIteration):
            next(it)

    def test_incident_no_edges(self):
        g2 = DirectedGraph(["X", "Y"])
        # no edges at all
        it = DirectedGraph.IncidentEdgeIterator(g2, 0)
        with self.assertRaises(StopIteration):
            next(it)
   
    def test_adjacent_vertices_basic(self):
        g = DirectedGraph(["A", "B", "C", "D"])
        g.add_edge("A", "B")
        g.add_edge("A", "C")
        g.add_edge("C", "D")

        it = DirectedGraph.AdjacentVertexIterator(g, g._vertices.index("A"))
        result = [next(it), next(it)]
        self.assertIn("B", result)
        self.assertIn("C", result)
        with self.assertRaises(StopIteration):
            next(it)

    def test_adjacent_vertices_none(self):
        g = DirectedGraph(["A", "B", "C"])
        g.add_edge("B", "C") 
        it = DirectedGraph.AdjacentVertexIterator(g, g._vertices.index("A"))
        with self.assertRaises(StopIteration):
            next(it)

    def test_adjacent_vertices_chain(self):
        g = DirectedGraph(["A", "B", "C", "D"])
        g.add_edge("A", "B")
        g.add_edge("B", "C")
        g.add_edge("C", "D")

        it = DirectedGraph.AdjacentVertexIterator(g, g._vertices.index("B"))
        self.assertEqual(next(it), "C")
        with self.assertRaises(StopIteration):
            next(it)

 

    def test_constructor_initial_vertices(self):
        g = DirectedGraph(["A", "B", "C"])
        self.assertEqual(g.vertex_count(), 3)
        self.assertTrue(g.has_vertex("A"))
        self.assertFalse(g.has_vertex("Z"))

    def test_has_edge(self):
        g = DirectedGraph(["A", "B"])
        g.add_edge("A", "B")
        self.assertTrue(g.has_edge("A", "B"))
        self.assertFalse(g.has_edge("B", "A"))
        self.assertFalse(g.has_edge("A", "C")) 

  

    def test_add_vertex(self):
        g = DirectedGraph()
        g.add_vertex("X")
        self.assertTrue(g.has_vertex("X"))
        self.assertEqual(g.vertex_count(), 1)

        with self.assertRaises(ValueError):
            g.add_vertex("X")  

    def test_remove_vertex_basic(self):
        g = DirectedGraph(["A", "B", "C"])
        g.add_edge("A", "B")  
        g.add_edge("B", "C")  

        g.remove_vertex("B")

       
        self.assertEqual(g._vertices, ["A", "C"])

        
        self.assertEqual(g.edge_count(), 0)

    def test_remove_vertex_reindex_edges(self):
        g = DirectedGraph(["A", "B", "C", "D"])
        g.add_edge("A", "D")  
        g.add_edge("C", "D")  

        g.remove_vertex("B")  
    

        expected_edges = [
            (0, 2),  
            (1, 2), 
        ]

        self.assertEqual(g._edges, expected_edges)

    def test_remove_vertex_not_exists(self):
        g = DirectedGraph(["A"])
        with self.assertRaises(ValueError):
            g.remove_vertex("Z")
   

    def test_add_edge_basic(self):
        g = DirectedGraph(["A", "B", "C"])
        g.add_edge("A", "B") 
        self.assertIn((0, 1), g._edges)
        self.assertEqual(g.edge_count(), 1)

    def test_add_edge_duplicate(self):
        g = DirectedGraph(["A", "B"])
        g.add_edge("A", "B")
        with self.assertRaises(ValueError):
            g.add_edge("A", "B")

    def test_add_edge_unknown_vertex(self):
        g = DirectedGraph(["A", "B"])
        with self.assertRaises(ValueError):
            g.add_edge("A", "X")

    def test_remove_edge_basic(self):
        g = DirectedGraph(["A", "B", "C"])
        g.add_edge("A", "C")
        g.add_edge("C", "B")

        g.remove_edge("A", "C")

        self.assertNotIn((0, 2), g._edges)
        self.assertEqual(g.edge_count(), 1)

    def test_remove_edge_not_exists(self):
        g = DirectedGraph(["A", "B"])
        with self.assertRaises(ValueError):
            g.remove_edge("A", "B")



    def test_degree_vertex_basic(self):
        g = DirectedGraph(["A", "B", "C"])
        g.add_edge("A", "B")
        g.add_edge("B", "C")
        g.add_edge("C", "A")

  
        self.assertEqual(g.degree_vertex("A"), 2)
     
        self.assertEqual(g.degree_vertex("B"), 2)
   
        self.assertEqual(g.degree_vertex("C"), 2)

    def test_degree_vertex_no_edges(self):
        g = DirectedGraph(["A", "B"])
        self.assertEqual(g.degree_vertex("A"), 0)



    def test_degree_edge_basic(self):
        g = DirectedGraph(["A", "B"])
        g.add_edge("A", "B")
        self.assertEqual(g.degree_edge("A", "B"), 2)

    def test_degree_edge_not_exists(self):
        g = DirectedGraph(["A", "B"])
        with self.assertRaises(ValueError):
            g.degree_edge("A", "B")



    def test_vertices_iterator(self):
        g = DirectedGraph(["A", "B", "C"])
        it = g.vertices()
        collected = [next(it), next(it), next(it)]
        self.assertEqual(collected, ["A", "B", "C"])
        with self.assertRaises(StopIteration):
            next(it)

  

    def test_edges_iterator(self):
        g = DirectedGraph(["A", "B", "C"])
        g.add_edge("A", "B")
        g.add_edge("B", "C")

        it = g.edges()
        collected = [next(it), next(it)]
        self.assertEqual(collected, [(0, 1), (1, 2)])
        with self.assertRaises(StopIteration):
            next(it)



    def test_incident_edges_basic(self):
        g = DirectedGraph(["A", "B", "C"])
        g.add_edge("A", "C")  
        g.add_edge("B", "C")
        g.add_edge("C", "A")

        it = g.incident_edges("C")
        result = [next(it), next(it), next(it)]
        self.assertCountEqual(result, [(0, 2), (1, 2), (2, 0)])

        with self.assertRaises(StopIteration):
            next(it)

    def test_incident_edges_none(self):
        g = DirectedGraph(["A", "B"])
        g.add_edge("A", "B")
        it = g.incident_edges("A")
        self.assertEqual(next(it), (0, 1))
        with self.assertRaises(StopIteration):
            next(it)


    def test_adjacent_vertices_basic(self):
        g = DirectedGraph(["A", "B", "C", "D"])
        g.add_edge("A", "C") 
        g.add_edge("A", "B")

        it = g.adjacent_vertices("A")
        result = [next(it), next(it)]
        self.assertCountEqual(result, ["B", "C"])

        with self.assertRaises(StopIteration):
            next(it)

    def test_adjacent_vertices_no_neighbors(self):
        g = DirectedGraph(["A", "B"])
        g.add_edge("B", "A")
        it = g.adjacent_vertices("A")
        with self.assertRaises(StopIteration):
            next(it)


if __name__ == "__main__":
    unittest.main()
