cmake_minimum_required(VERSION 3.16)
project(DirectedGraph)

set(CMAKE_CXX_STANDARD 17)

include(FetchContent)

# --- Скачивание GoogleTest ---
FetchContent_Declare(
        googletest
        URL https://github.com/google/googletest/archive/refs/heads/main.zip
)

FetchContent_MakeAvailable(googletest)

# --- Основной исполняемый файл ---
add_executable(main
        main.cpp
        directed_graph.cpp
)

# --- Цель для юнит-тестов ---
add_executable(graph_tests
        test_directed_graph.cpp
        directed_graph.cpp
)

target_link_libraries(graph_tests
        gtest
        gtest_main
)

enable_testing()
add_test(NAME graph_tests COMMAND graph_tests)
