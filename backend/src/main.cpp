#include <iostream>
#include <string>
#include <filesystem>
#include "ApiServer.h"

namespace fs = std::filesystem;

int main(int argc, char** argv) {
    // 默认数据库路径
    std::string dbPath = "../../database/app.db";
    int port = 50000;

    // 检查命令行参数
    if (argc > 1) {
        dbPath = argv[1];
    }
    if (argc > 2) {
        port = std::stoi(argv[2]);
    }

    // 检查数据库文件是否存在
    if (!fs::exists(dbPath)) {
        std::cerr << "Error: Database file not found at " << dbPath << std::endl;
        std::cerr << "Please run the data processing scripts first." << std::endl;
        return 1;
    }

    std::cout << "Starting API server..." << std::endl;
    std::cout << "Database path: " << dbPath << std::endl;
    std::cout << "Port: " << port << std::endl;

    try {
        ApiServer server(dbPath, port);
        server.start();
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }

    return 0;
} 