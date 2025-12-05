#pragma once

#include <list>
#include <vector>
#include <utility>
#include <algorithm>
#include <iterator>
#include <stdexcept>
#include <ostream>
#include <functional>

template <typename T>
class DirectedGraph
{
public:
    // === STL-style typedefs ===
    using value_type        = T;
    using size_type         = std::size_t;
    using difference_type   = std::ptrdiff_t;
    using reference         = value_type&;
    using const_reference   = const value_type&;
    using pointer           = value_type*;
    using const_pointer     = const value_type*;

private:
    struct VertexRecord
    {
        value_type value;

        explicit VertexRecord(const value_type& v) : value(v) {}
    };

    using vertex_list = std::list<VertexRecord>;

public:
    using vertex_iterator       = typename vertex_list::iterator;
    using const_vertex_iterator = typename vertex_list::const_iterator;
    using reverse_vertex_iterator       = typename vertex_list::reverse_iterator;
    using const_reverse_vertex_iterator = typename vertex_list::const_reverse_iterator;

private:
    struct EdgeRecord
    {
        vertex_iterator from;
        vertex_iterator to;

        EdgeRecord(vertex_iterator f, vertex_iterator t)
            : from(f), to(t) {}
    };

    using edge_list = std::list<EdgeRecord>;

public:
    using edge_iterator       = typename edge_list::iterator;
    using const_edge_iterator = typename edge_list::const_iterator;
    using reverse_edge_iterator       = typename edge_list::reverse_iterator;
    using const_reverse_edge_iterator = typename edge_list::const_reverse_iterator;

    // --- Exception type ---
    class graph_error : public std::runtime_error
    {
    public:
        explicit graph_error(const std::string& msg)
            : std::runtime_error(msg) {}
    };

    // === Итераторы по инцидентным рёбрам (out-edges вершины) ===
    class incident_edge_iterator
    {
        using base_iter = edge_iterator;

        DirectedGraph* graph_ = nullptr;
        vertex_iterator v_;
        base_iter it_;

        void skip_forward()
        {
            while (it_ != graph_->edges_.end() && it_->from != v_) {
                ++it_;
            }
        }

        void skip_backward()
        {
            while (true) {
                if (it_ == graph_->edges_.begin()) {
                    if (it_->from != v_) {
                        it_ = graph_->edges_.end();
                    }
                    return;
                }
                if (it_->from == v_) return;
                --it_;
            }
        }

    public:
        using iterator_category = std::bidirectional_iterator_tag;
        using value_type        = EdgeRecord;
        using difference_type   = std::ptrdiff_t;
        using pointer           = EdgeRecord*;
        using reference         = EdgeRecord&;

        incident_edge_iterator() = default;

        incident_edge_iterator(DirectedGraph* g,
                               vertex_iterator v,
                               base_iter it)
            : graph_(g), v_(v), it_(it)
        {
            if (graph_) skip_forward();
        }

        reference operator*() const { return *it_; }
        pointer   operator->() const { return &(*it_); }

        incident_edge_iterator& operator++()
        {
            ++it_;
            skip_forward();
            return *this;
        }

        incident_edge_iterator operator++(int)
        {
            incident_edge_iterator tmp(*this);
            ++(*this);
            return tmp;
        }

        incident_edge_iterator& operator--()
        {
            if (!graph_ || it_ == graph_->edges_.begin())
                throw graph_error("Cannot decrement incident_edge_iterator before begin");

            --it_;
            skip_backward();
            return *this;
        }

        incident_edge_iterator operator--(int)
        {
            incident_edge_iterator tmp(*this);
            --(*this);
            return tmp;
        }

        bool operator==(const incident_edge_iterator& other) const
        {
            return graph_ == other.graph_ && it_ == other.it_ && v_ == other.v_;
        }

        bool operator!=(const incident_edge_iterator& other) const
        {
            return !(*this == other);
        }

        // доступ к базовому итератору (для erase)
        base_iter base() const { return it_; }
    };

    class const_incident_edge_iterator
    {
        incident_edge_iterator it_;
    public:
        using iterator_category = std::bidirectional_iterator_tag;
        using value_type        = const EdgeRecord;
        using difference_type   = std::ptrdiff_t;
        using pointer           = const EdgeRecord*;
        using reference         = const EdgeRecord&;

        const_incident_edge_iterator() = default;
        const_incident_edge_iterator(const incident_edge_iterator& it) : it_(it) {}

        reference operator*() const { return *it_; }
        pointer   operator->() const { return &(*it_); }

        const_incident_edge_iterator& operator++()
        {
            ++it_;
            return *this;
        }

        const_incident_edge_iterator operator++(int)
        {
            const_incident_edge_iterator tmp(*this);
            ++(*this);
            return tmp;
        }

        const_incident_edge_iterator& operator--()
        {
            --it_;
            return *this;
        }

        const_incident_edge_iterator operator--(int)
        {
            const_incident_edge_iterator tmp(*this);
            --(*this);
            return tmp;
        }

        bool operator==(const const_incident_edge_iterator& other) const
        {
            return it_ == other.it_;
        }

        bool operator!=(const const_incident_edge_iterator& other) const
        {
            return !(*this == other);
        }
    };

    // === Итератор по смежным вершинам (out-neighbors) ===
    class adjacent_vertex_iterator
    {
        incident_edge_iterator eit_;

    public:
        using iterator_category = std::bidirectional_iterator_tag;
        using value_type        = value_type;
        using difference_type   = std::ptrdiff_t;
        using pointer           = value_type*;
        using reference         = value_type&;

        adjacent_vertex_iterator() = default;
        explicit adjacent_vertex_iterator(const incident_edge_iterator& e)
            : eit_(e) {}

        reference operator*() const { return eit_.operator*().to->value; }
        pointer   operator->() const { return &(eit_.operator*().to->value); }

        adjacent_vertex_iterator& operator++()
        {
            ++eit_;
            return *this;
        }

        adjacent_vertex_iterator operator++(int)
        {
            adjacent_vertex_iterator tmp(*this);
            ++(*this);
            return tmp;
        }

        adjacent_vertex_iterator& operator--()
        {
            --eit_;
            return *this;
        }

        adjacent_vertex_iterator operator--(int)
        {
            adjacent_vertex_iterator tmp(*this);
            --(*this);
            return tmp;
        }

        bool operator==(const adjacent_vertex_iterator& other) const
        {
            return eit_ == other.eit_;
        }

        bool operator!=(const adjacent_vertex_iterator& other) const
        {
            return !(*this == other);
        }
    };

    class const_adjacent_vertex_iterator
    {
        adjacent_vertex_iterator it_;
    public:
        using iterator_category = std::bidirectional_iterator_tag;
        using value_type        = const value_type;
        using difference_type   = std::ptrdiff_t;
        using pointer           = const value_type*;
        using reference         = const value_type&;

        const_adjacent_vertex_iterator() = default;
        const_adjacent_vertex_iterator(const adjacent_vertex_iterator& it)
            : it_(it) {}

        reference operator*() const { return *it_; }
        pointer   operator->() const { return &(*it_); }

        const_adjacent_vertex_iterator& operator++()
        {
            ++it_;
            return *this;
        }

        const_adjacent_vertex_iterator operator++(int)
        {
            const_adjacent_vertex_iterator tmp(*this);
            ++(*this);
            return tmp;
        }

        const_adjacent_vertex_iterator& operator--()
        {
            --it_;
            return *this;
        }

        const_adjacent_vertex_iterator operator--(int)
        {
            const_adjacent_vertex_iterator tmp(*this);
            --(*this);
            return tmp;
        }

        bool operator==(const const_adjacent_vertex_iterator& other) const
        {
            return it_ == other.it_;
        }

        bool operator!=(const const_adjacent_vertex_iterator& other) const
        {
            return !(*this == other);
        }
    };

private:
    vertex_list vertices_;
    edge_list   edges_;

public:
    // === Конструкторы / деструктор ===
    DirectedGraph() = default;

    DirectedGraph(const DirectedGraph& other)
    {
        // сначала копируем вершины
        for (const auto& v : other.vertices_) {
            vertices_.emplace_back(v.value);
        }

        // сопоставляем старые итераторы с новыми
        std::vector<std::pair<typename DirectedGraph::const_vertex_iterator,
                              typename DirectedGraph::vertex_iterator>> mapping;
        {
            auto it_new  = vertices_.begin();
            auto it_old  = other.vertices_.begin();
            for (; it_old != other.vertices_.end();
                 ++it_old, ++it_new) {
                mapping.emplace_back(it_old, it_new);
            }
        }

        auto map_vertex = [&](typename DirectedGraph::vertex_iterator old_it)
        {
            for (auto& p : mapping) {
                if (p.first == old_it) return p.second;
            }
            throw graph_error("Inconsistent vertex mapping during copy");
        };

        // копируем рёбра
        for (auto e = other.edges_.begin(); e != other.edges_.end(); ++e) {
            auto from_new = map_vertex(e->from);
            auto to_new   = map_vertex(e->to);
            edges_.emplace_back(from_new, to_new);
        }
    }

    DirectedGraph& operator=(const DirectedGraph& other)
    {
        if (this == &other) return *this;
        DirectedGraph tmp(other);
        swap(tmp);
        return *this;
    }

    ~DirectedGraph() = default;

    void swap(DirectedGraph& other) noexcept
    {
        vertices_.swap(other.vertices_);
        edges_.swap(other.edges_);
    }

    // === Базовые методы контейнера ===
    bool empty() const noexcept
    {
        return vertices_.empty();
    }

    void clear() noexcept
    {
        vertices_.clear();
        edges_.clear();
    }

    size_type vertex_count() const noexcept
    {
        return vertices_.size();
    }

    size_type edge_count() const noexcept
    {
        return edges_.size();
    }

    // === Поиск вершины по значению ===
    vertex_iterator find_vertex(const value_type& v)
    {
        return std::find_if(vertices_.begin(), vertices_.end(),
                            [&](const VertexRecord& rec) {
                                return rec.value == v;
                            });
    }

    const_vertex_iterator find_vertex(const value_type& v) const
    {
        return std::find_if(vertices_.cbegin(), vertices_.cend(),
                            [&](const VertexRecord& rec) {
                                return rec.value == v;
                            });
    }

    bool contains_vertex(const value_type& v) const
    {
        return find_vertex(v) != vertices_.end();
    }

    // === Поиск ребра по значениям вершин ===
    edge_iterator find_edge(const value_type& from, const value_type& to)
    {
        auto vf = find_vertex(from);
        auto vt = find_vertex(to);
        if (vf == vertices_.end() || vt == vertices_.end())
            return edges_.end();

        return std::find_if(edges_.begin(), edges_.end(),
                            [&](const EdgeRecord& e) {
                                return e.from == vf && e.to == vt;
                            });
    }

    const_edge_iterator find_edge(const value_type& from, const value_type& to) const
    {
        auto vf = find_vertex(from);
        auto vt = find_vertex(to);
        if (vf == vertices_.end() || vt == vertices_.end())
            return edges_.end();

        return std::find_if(edges_.cbegin(), edges_.cend(),
                            [&](const EdgeRecord& e) {
                                return e.from == vf && e.to == vt;
                            });
    }

    bool contains_edge(const value_type& from, const value_type& to) const
    {
        return find_edge(from, to) != edges_.end();
    }

    // === Добавление / удаление вершин ===
    vertex_iterator add_vertex(const value_type& v)
    {
        if (contains_vertex(v))
            throw graph_error("Vertex already exists");
        vertices_.emplace_back(v);
        auto it = vertices_.end();
        --it;
        return it;
    }

    void remove_vertex(const value_type& v)
    {
        auto it = find_vertex(v);
        if (it == vertices_.end())
            throw graph_error("Vertex not found");

        remove_vertex(it);
    }

    void remove_vertex(vertex_iterator vit)
    {
        // удалить все инцидентные рёбра
        for (auto e = edges_.begin(); e != edges_.end(); ) {
            if (e->from == vit || e->to == vit) {
                e = edges_.erase(e);
            } else {
                ++e;
            }
        }
        vertices_.erase(vit);
    }

    // === Добавление / удаление рёбер ===
    edge_iterator add_edge(const value_type& from, const value_type& to)
    {
        auto vf = find_vertex(from);
        auto vt = find_vertex(to);

        if (vf == vertices_.end() || vt == vertices_.end())
            throw graph_error("Cannot add edge: vertex not found");

        if (contains_edge(from, to))
            throw graph_error("Edge already exists");

        edges_.emplace_back(vf, vt);
        auto it = edges_.end();
        --it;
        return it;
    }

    void remove_edge(const value_type& from, const value_type& to)
    {
        auto it = find_edge(from, to);
        if (it == edges_.end())
            throw graph_error("Edge not found");
        edges_.erase(it);
    }

    void remove_edge(edge_iterator eit)
    {
        edges_.erase(eit);
    }

    // === Степени ===
    // Степень вершины: число исходящих + входящих рёбер
    size_type vertex_degree(const value_type& v) const
    {
        auto vit = find_vertex(v);
        if (vit == vertices_.end())
            throw graph_error("Vertex not found");

        size_type deg = 0;
        for (auto& e : edges_) {
            if (e.from == vit || e.to == vit) ++deg;
        }
        return deg;
    }

    // Степень ребра: число рёбер, смежных этому ребру
    size_type edge_degree(const value_type& from, const value_type& to) const
    {
        auto eit = find_edge(from, to);
        if (eit == edges_.end())
            throw graph_error("Edge not found");

        size_type deg = 0;
        for (auto it = edges_.cbegin(); it != edges_.cend(); ++it) {
            if (it == eit) continue;
            if (it->from == eit->from || it->from == eit->to ||
                it->to   == eit->from || it->to   == eit->to) {
                ++deg;
            }
        }
        return deg;
    }

    // === Итераторы по вершинам ===
    vertex_iterator       vertices_begin()       { return vertices_.begin(); }
    vertex_iterator       vertices_end()         { return vertices_.end();   }
    const_vertex_iterator vertices_begin() const { return vertices_.begin(); }
    const_vertex_iterator vertices_end()   const { return vertices_.end();   }
    const_vertex_iterator vertices_cbegin() const { return vertices_.cbegin(); }
    const_vertex_iterator vertices_cend()   const { return vertices_.cend();   }

    reverse_vertex_iterator       vertices_rbegin()       { return vertices_.rbegin(); }
    reverse_vertex_iterator       vertices_rend()         { return vertices_.rend();   }
    const_reverse_vertex_iterator vertices_rbegin() const { return vertices_.rbegin(); }
    const_reverse_vertex_iterator vertices_rend()   const { return vertices_.rend();   }

    // === Итераторы по рёбрам ===
    edge_iterator       edges_begin()       { return edges_.begin(); }
    edge_iterator       edges_end()         { return edges_.end();   }
    const_edge_iterator edges_begin() const { return edges_.begin(); }
    const_edge_iterator edges_end()   const { return edges_.end();   }
    const_edge_iterator edges_cbegin() const { return edges_.cbegin(); }
    const_edge_iterator edges_cend()   const { return edges_.cend();   }

    reverse_edge_iterator       edges_rbegin()       { return edges_.rbegin(); }
    reverse_edge_iterator       edges_rend()         { return edges_.rend();   }
    const_reverse_edge_iterator edges_rbegin() const { return edges_.rbegin(); }
    const_reverse_edge_iterator edges_rend()   const { return edges_.rend();   }

    // === Итераторы по инцидентным рёбрам вершины ===
    incident_edge_iterator incident_edges_begin(vertex_iterator v)
    {
        return incident_edge_iterator(this, v, edges_.begin());
    }

    incident_edge_iterator incident_edges_end(vertex_iterator v)
    {
        return incident_edge_iterator(this, v, edges_.end());
    }


    const_incident_edge_iterator incident_edges_begin(vertex_iterator v) const
    {
        return const_incident_edge_iterator(
            incident_edge_iterator(const_cast<DirectedGraph*>(this),
                                   const_cast<vertex_iterator&>(v),
                                   const_cast<edge_list&>(edges_).begin()));
    }

    const_incident_edge_iterator incident_edges_end(vertex_iterator v) const
    {
        return const_incident_edge_iterator(
            incident_edge_iterator(
                const_cast<DirectedGraph*>(this),
                v,
                const_cast<edge_list&>(edges_).end()
            )
        );
    }


    // === Итераторы по смежным вершинам (out-neighbors) ===
    adjacent_vertex_iterator adjacent_vertices_begin(vertex_iterator v)
    {
        return adjacent_vertex_iterator(incident_edges_begin(v));
    }

    adjacent_vertex_iterator adjacent_vertices_end(vertex_iterator v)
    {
        return adjacent_vertex_iterator(incident_edges_end(v));
    }

    const_adjacent_vertex_iterator adjacent_vertices_begin(vertex_iterator v) const
    {
        return const_adjacent_vertex_iterator(adjacent_vertices_begin(
            const_cast<vertex_iterator&>(v)));
    }

    const_adjacent_vertex_iterator adjacent_vertices_end(vertex_iterator v) const
    {
        return const_adjacent_vertex_iterator(adjacent_vertices_end(
            const_cast<vertex_iterator&>(v)));
    }

    // === Операторы сравнения ===
    friend bool operator==(const DirectedGraph& a, const DirectedGraph& b)
    {
        if (a.vertex_count() != b.vertex_count() ||
            a.edge_count()   != b.edge_count())
            return false;

        std::vector<value_type> av, bv;
        av.reserve(a.vertex_count());
        bv.reserve(b.vertex_count());

        for (const auto& v : a.vertices_) av.push_back(v.value);
        for (const auto& v : b.vertices_) bv.push_back(v.value);

        std::sort(av.begin(), av.end());
        std::sort(bv.begin(), bv.end());
        if (av != bv) return false;

        auto edges_to_pairs = [](const DirectedGraph& g) {
            std::vector<std::pair<value_type, value_type>> res;
            res.reserve(g.edge_count());
            for (auto e = g.edges_.cbegin(); e != g.edges_.cend(); ++e) {
                res.emplace_back(e->from->value, e->to->value);
            }
            std::sort(res.begin(), res.end());
            return res;
        };

        return edges_to_pairs(a) == edges_to_pairs(b);
    }

    friend bool operator!=(const DirectedGraph& a, const DirectedGraph& b)
    {
        return !(a == b);
    }

    friend bool operator<(const DirectedGraph& a, const DirectedGraph& b)
    {
        // лексикографическое сравнение по вершинам, затем по рёбрам
        std::vector<value_type> av, bv;
        av.reserve(a.vertex_count());
        bv.reserve(b.vertex_count());
        for (auto& v : a.vertices_) av.push_back(v.value);
        for (auto& v : b.vertices_) bv.push_back(v.value);
        std::sort(av.begin(), av.end());
        std::sort(bv.begin(), bv.end());

        if (av < bv) return true;
        if (bv < av) return false;

        auto edges_to_pairs = [](const DirectedGraph& g) {
            std::vector<std::pair<value_type, value_type>> res;
            res.reserve(g.edge_count());
            for (auto e = g.edges_.cbegin(); e != g.edges_.cend(); ++e) {
                res.emplace_back(e->from->value, e->to->value);
            }
            std::sort(res.begin(), res.end());
            return res;
        };

        return edges_to_pairs(a) < edges_to_pairs(b);
    }

    friend bool operator>(const DirectedGraph& a, const DirectedGraph& b)
    {
        return b < a;
    }

    friend bool operator<=(const DirectedGraph& a, const DirectedGraph& b)
    {
        return !(b < a);
    }

    friend bool operator>=(const DirectedGraph& a, const DirectedGraph& b)
    {
        return !(a < b);
    }

    // === Вывод в поток через std::for_each ===
    friend std::ostream& operator<<(std::ostream& os, const DirectedGraph& g)
    {
        os << "Vertices:\n";
        std::for_each(g.vertices_.cbegin(), g.vertices_.cend(),
                      [&](const VertexRecord& v) {
                          os << "  " << v.value << "\n";
                      });

        os << "Edges:\n";
        std::for_each(g.edges_.cbegin(), g.edges_.cend(),
                      [&](const EdgeRecord& e) {
                          os << "  " << e.from->value << " -> " << e.to->value << "\n";
                      });

        return os;
    }
};
