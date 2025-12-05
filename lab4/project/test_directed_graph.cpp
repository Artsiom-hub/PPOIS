#include <gtest/gtest.h>
#include "directed_graph.cpp"

// Удобный алиас
using G = DirectedGraph<int>;

// -------------------------------
//   Тест: добавление вершин
// -------------------------------
TEST(GraphTest, AddVertices) {
    G g;

    auto v1 = g.add_vertex(10);
    auto v2 = g.add_vertex(20);
    auto v3 = g.add_vertex(30);

    EXPECT_EQ(g.vertex_count(), 3);
    EXPECT_TRUE(g.contains_vertex(10));
    EXPECT_TRUE(g.contains_vertex(20));
    EXPECT_TRUE(g.contains_vertex(30));

    EXPECT_THROW(g.add_vertex(10), G::graph_error);

}

// -------------------------------
//   Тест: добавление рёбер
// -------------------------------
TEST(GraphTest, AddEdges) {
    G g;

    g.add_vertex(1);
    g.add_vertex(2);
    g.add_vertex(3);

    g.add_edge(1, 2);
    g.add_edge(1, 3);

    EXPECT_EQ(g.edge_count(), 2);
    EXPECT_TRUE(g.contains_edge(1, 2));
    EXPECT_TRUE(g.contains_edge(1, 3));

    EXPECT_THROW(g.add_edge(1, 4), G::graph_error);   // нет вершины
    EXPECT_THROW(g.add_edge(1, 2), G::graph_error);   // дубликат
}

// -------------------------------
//   Тест: удаление вершин
// -------------------------------
TEST(GraphTest, RemoveVertex) {
    G g;
    g.add_vertex(1);
    g.add_vertex(2);
    g.add_vertex(3);

    g.add_edge(1, 2);
    g.add_edge(2, 3);

    g.remove_vertex(2);

    EXPECT_EQ(g.vertex_count(), 2);
    EXPECT_EQ(g.edge_count(), 0); // все рёбра, связанные с 2, должны исчезнуть
}

// -------------------------------
//   Тест: удаление ребра
// -------------------------------
TEST(GraphTest, RemoveEdge) {
    G g;
    g.add_vertex(1);
    g.add_vertex(2);

    g.add_edge(1, 2);
    EXPECT_EQ(g.edge_count(), 1);

    g.remove_edge(1, 2);
    EXPECT_EQ(g.edge_count(), 0);

    EXPECT_THROW(g.remove_edge(1, 2), G::graph_error);
}

// -------------------------------
//   Тест: степень вершины
// -------------------------------
TEST(GraphTest, VertexDegree) {
    G g;

    g.add_vertex(1);
    g.add_vertex(2);
    g.add_vertex(3);

    g.add_edge(1, 2);
    g.add_edge(2, 3);
    g.add_edge(3, 1);

    EXPECT_EQ(g.vertex_degree(1), 2); // одно входящее, одно исходящее
    EXPECT_EQ(g.vertex_degree(2), 2);
    EXPECT_EQ(g.vertex_degree(3), 2);

    EXPECT_THROW(g.vertex_degree(10), G::graph_error);
}

// -------------------------------
//   Тест: степень ребра
// -------------------------------
TEST(GraphTest, EdgeDegree) {
    G g;

    g.add_vertex(1);
    g.add_vertex(2);
    g.add_vertex(3);

    g.add_edge(1, 2);
    g.add_edge(1, 3);
    g.add_edge(2, 3);

    // Ребро (1->3) смежно с (1->2) и (2->3)? — да, 2 штуки
    EXPECT_EQ(g.edge_degree(1, 3), 2);

    EXPECT_THROW(g.edge_degree(5, 8), G::graph_error);
}

// -------------------------------
//   Тест: итераторы вершин
// -------------------------------
TEST(GraphTest, VertexIterators) {
    G g;
    g.add_vertex(1);
    g.add_vertex(2);
    g.add_vertex(3);

    std::vector<int> verts;
    for (auto it = g.vertices_begin(); it != g.vertices_end(); ++it)
        verts.push_back(it->value);

    EXPECT_EQ(verts.size(), 3);
    EXPECT_TRUE(std::find(verts.begin(), verts.end(), 1) != verts.end());
    EXPECT_TRUE(std::find(verts.begin(), verts.end(), 2) != verts.end());
    EXPECT_TRUE(std::find(verts.begin(), verts.end(), 3) != verts.end());
}

// -------------------------------
//   Тест: итераторы рёбер
// -------------------------------
TEST(GraphTest, EdgeIterators) {
    G g;
    g.add_vertex(1);
    g.add_vertex(2);
    g.add_vertex(3);

    g.add_edge(1, 2);
    g.add_edge(2, 3);

    int count = 0;
    for (auto it = g.edges_begin(); it != g.edges_end(); ++it)
        count++;

    EXPECT_EQ(count, 2);
}

// -------------------------------
//   Тест: adjacent_vertices
// -------------------------------
TEST(GraphTest, AdjacentVertices) {
    G g;

    auto v1 = g.add_vertex(1);
    auto v2 = g.add_vertex(2);
    auto v3 = g.add_vertex(3);

    g.add_edge(1, 2);
    g.add_edge(1, 3);

    std::vector<int> adj;

    for (auto it = g.adjacent_vertices_begin(v1);
         it != g.adjacent_vertices_end(v1); ++it)
        adj.push_back(*it);

    EXPECT_EQ(adj.size(), 2);
    EXPECT_TRUE(std::find(adj.begin(), adj.end(), 2) != adj.end());
    EXPECT_TRUE(std::find(adj.begin(), adj.end(), 3) != adj.end());
}

// -------------------------------
//   Тест: copy constructor
// -------------------------------
TEST(GraphTest, CopyConstructor) {
    G g;

    g.add_vertex(1);
    g.add_vertex(2);
    g.add_edge(1, 2);

    G h = g;

    EXPECT_EQ(h.vertex_count(), 2);
    EXPECT_EQ(h.edge_count(), 1);
    EXPECT_TRUE(h.contains_edge(1, 2));

    // изменения не должны влиять на оригинал
    h.add_vertex(3);

    EXPECT_FALSE(g.contains_vertex(3));
}

// -------------------------------
//   Тест: сравнение графов
// -------------------------------
TEST(GraphTest, Comparison) {
    G g1, g2;

    g1.add_vertex(1);
    g1.add_vertex(2);
    g1.add_edge(1, 2);

    g2.add_vertex(2);
    g2.add_vertex(1);
    g2.add_edge(1, 2);

    EXPECT_TRUE(g1 == g2);
    EXPECT_FALSE(g1 != g2);
    EXPECT_FALSE(g1 < g2);
}
