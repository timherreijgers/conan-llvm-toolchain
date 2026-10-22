cmake_minimum_required(VERSION 4.3)

if (CMAKE_VERSION VERSION_GREATER_EQUAL "4.4.0")
    set(CMAKE_EXPERIMENTAL_CXX_IMPORT_STD "f35a9ac6-8463-4d38-8eec-5d6008153e7d")
elseif (CMAKE_VERSION VERSION_GREATER_EQUAL "4.3.0")
    set(CMAKE_EXPERIMENTAL_CXX_IMPORT_STD "451f2fe2-a8a2-47c3-bc32-94786d8fc91b")
endif ()

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wno-reserved-module-identifier")

message(STATUS "CMake version: ${CMAKE_VERSION}")
message(STATUS "import std gate: ${CMAKE_EXPERIMENTAL_CXX_IMPORT_STD}")

project(test_package LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_executable(test_package src/test_package.cpp)
target_compile_features(test_package PRIVATE cxx_std_17)

include(CTest)
add_test(NAME test_package COMMAND test_package)