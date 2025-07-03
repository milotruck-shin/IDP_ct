cmake_minimum_required(VERSION 3.0)
project(opencv_test VERSION 0.1.0 LANGUAGES C CXX)
find_package(OpenCV REQUIRED)

include_directories(${OpenCV_INCLUDE_DIRS})

#create executable from source file
add_executable(opencv_test main.cpp)    #CMake will compile main.cpp and link it to final exe called open_cv test

#link the library to executable
target_link_libraries(opencv_test ${OpenCV_LIBS})