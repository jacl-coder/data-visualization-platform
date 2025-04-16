cmake_minimum_required(VERSION 3.20)
project(data_visualization_backend)

# 设置C++标准
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 查找SQLite库
find_package(SQLite3 REQUIRED)
include_directories(${SQLite3_INCLUDE_DIRS})

# 查找Boost库 (Crow可能依赖部分Boost库)
find_package(Boost COMPONENTS system thread)
if(Boost_FOUND)
    include_directories(${Boost_INCLUDE_DIRS})
endif()

# 查找Asio库
find_path(ASIO_INCLUDE_DIR asio.hpp
    PATHS /usr/include /usr/local/include ${CMAKE_SOURCE_DIR}/libs
)
if(NOT ASIO_INCLUDE_DIR)
    message(FATAL_ERROR "Asio库未找到，请安装：sudo apt-get install libasio-dev")
endif()
include_directories(${ASIO_INCLUDE_DIR})

# 添加JSON库
include_directories(${CMAKE_SOURCE_DIR}/libs/nlohmann)

# 添加include目录
include_directories(include)

# 添加Crow头文件库路径
include_directories(libs/crow/include)

# 添加源文件
file(GLOB SOURCES "src/*.cpp")

# 创建可执行文件
add_executable(api_server ${SOURCES})

# 链接SQLite库
target_link_libraries(api_server ${SQLite3_LIBRARIES})

# 链接Boost库(如果找到)
if(Boost_FOUND)
    target_link_libraries(api_server ${Boost_LIBRARIES})
endif()

# 链接pthread (Crow需要)
target_link_libraries(api_server pthread)

# 如果需要，链接其他系统库
target_link_libraries(api_server stdc++fs)

# 安装目标
install(TARGETS api_server DESTINATION bin)
