#include "directed_graph.cpp"
#include <iostream>

template<typename G>
void print_vertices(const G& g) {
    std::cout << "Vertices (forward): ";
    for (auto it = g.vertices_begin(); it != g.vertices_end(); ++it)
        std::cout << it->value << " ";
    std::cout << "\n";

    std::cout << "Vertices (reverse): ";
    for (auto it = g.vertices_rbegin(); it != g.vertices_rend(); ++it)
        std::cout << it->value << " ";
    std::cout << "\n";
}

template<typename G>
void print_edges(const G& g) {
    std::cout << "Edges (forward): ";
    for (auto it = g.edges_begin(); it != g.edges_end(); ++it)
        std::cout << it->from->value << "->" << it->to->value << " ";
    std::cout << "\n";

    std::cout << "Edges (reverse): ";
    for (auto it = g.edges_rbegin(); it != g.edges_rend(); ++it)
        std::cout << it->from->value << "->" << it->to->value << " ";
    std::cout << "\n";
}

int main() {
    DirectedGraph<int> g;

    std::cout << "=== ADD VERTICES ===\n";
    auto v1 = g.add_vertex(1);
    auto v2 = g.add_vertex(2);
    auto v3 = g.add_vertex(3);
    auto v4 = g.add_vertex(4);

    print_vertices(g);

    std::cout << "\n=== ADD EDGES ===\n";
    auto e12 = g.add_edge(1, 2);
    auto e23 = g.add_edge(2, 3);
    auto e13 = g.add_edge(1, 3);
    auto e34 = g.add_edge(3, 4);
    auto e14 = g.add_edge(1, 4);

    print_edges(g);

    std::cout << "\n=== DEGREE CHECKS ===\n";
    std::cout << "deg(1) = " << g.vertex_degree(1) << "\n";
    std::cout << "deg(edge 1->3) = " << g.edge_degree(1, 3) << "\n";

    std::cout << "\n=== INCIDENT EDGES OF 1 ===\n";
    for (auto it = g.incident_edges_begin(v1);
         it != g.incident_edges_end(v1); ++it) {
        std::cout << it->from->value << "->" << it->to->value << " ";
    }
    std::cout << "\n";

    std::cout << "\n=== ADJACENT VERTICES OF 1 ===\n";
    for (auto it = g.adjacent_vertices_begin(v1);
         it != g.adjacent_vertices_end(v1); ++it) {
        std::cout << *it << " ";
    }
    std::cout << "\n";

    std::cout << "\n=== REMOVE EDGE 1->4 ===\n";
    g.remove_edge(1, 4);
    print_edges(g);

    std::cout << "\n=== REMOVE EDGE BY ITERATOR (1->3) ===\n";
    g.remove_edge(e13);
    print_edges(g);

    std::cout << "\n=== REMOVE VERTEX 3 ===\n";
    g.remove_vertex(3);
    print_vertices(g);
    print_edges(g);

    std::cout << "\n=== REMOVE VERTEX BY ITERATOR (vertex 2) ===\n";
    g.remove_vertex(v2);
    print_vertices(g);
    print_edges(g);

    std::cout << "\n=== COPY CONSTRUCTOR / COMPARISONS ===\n";
    DirectedGraph<int> g2 = g;           // copy
    std::cout << "g == g2 ? " << (g == g2) << "\n";

    g2.add_vertex(100);
    std::cout << "after adding 100: g < g2 ? " << (g < g2) << "\n";

    std::cout << "\n=== CLEAR ===\n";
    g2.clear();
    std::cout << "g2.empty() = " << g2.empty() << "\n";

    std::cout << "\n=== EXCEPTIONS TEST ===\n";
    try {
        g.add_edge(99, 100);
    } catch (const std::exception& ex) {
        std::cout << "Exception caught: " << ex.what() << "\n";
    }

    try {
        g.remove_vertex(999);
    } catch (const std::exception& ex) {
        std::cout << "Exception caught: " << ex.what() << "\n";
    }

    std::cout << "\n=== FINAL GRAPH ===\n";
    std::cout << g << "\n";

    return 0;
}
