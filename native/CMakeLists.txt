cmake_minimum_required(VERSION 3.14)
project(MyWaltNativeEngine CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(native_engine native_engine.cpp)
add_executable(fast_search fast_search.cpp)

if(WIN32)
    target_link_libraries(native_engine shell32 user32)
endif()
