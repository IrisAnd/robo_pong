cmake_minimum_required(VERSION 2.8.12)

project(Auto_calib)

find_package(OpenCV REQUIRED PATHS ~/Schreibtisch/OpenCV/build NO_DEFAULT_PATH)
include_directories(${OpenCV_INCLUDE_DIRS})

add_executable(Auto_calib src/AUTO_calibration_robot.cpp)
target_link_libraries(Auto_calib ${OpenCV_LIBS})

