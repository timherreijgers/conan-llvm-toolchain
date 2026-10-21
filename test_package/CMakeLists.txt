cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

add_executable(test_package src/test_package.cpp)
target_compile_features(test_package PRIVATE cxx_std_17)

include(CTest)
add_test(NAME test_package COMMAND test_package)