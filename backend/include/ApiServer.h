#pragma once

#include <string>
#include <memory>
#include "crow.h"
#include "DatabaseManager.h"

// CORS中间件实现
class CORSMiddleware 
{
public:
    struct context {};

    void before_handle(crow::request& /*req*/, crow::response& res, context& /*ctx*/) 
    {
        res.set_header("Access-Control-Allow-Origin", "*");
        res.set_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS");
        res.set_header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept, Authorization");
        res.set_header("Access-Control-Allow-Credentials", "true");
        res.set_header("Access-Control-Max-Age", "86400"); // 24小时
    }
    
    void after_handle(crow::request& /*req*/, crow::response& /*res*/, context& /*ctx*/)
    {
        // 在响应发送后执行的逻辑，这里不需要做任何事情
    }
};

/**
 * API服务器类
 * 使用Crow框架提供RESTful API
 */
class ApiServer {
public:
    /**
     * 构造函数
     * @param dbPath 数据库文件路径
     * @param port 服务器端口
     */
    ApiServer(const std::string& dbPath, int port = 8080);

    /**
     * 启动服务器
     */
    void start();

    /**
     * 停止服务器
     */
    void stop();

private:
    std::shared_ptr<DatabaseManager> dbManager;
    crow::App<CORSMiddleware> app;
    int port;
    bool running;

    /**
     * 设置API路由
     */
    void setupRoutes();

    /**
     * 注册概览API
     * 返回整体统计数据
     */
    void registerOverviewApi();

    /**
     * 注册时间线API
     * 返回时间序列数据
     */
    void registerTimelineApi();

    /**
     * 注册国家维度API
     * 返回按国家分组的统计数据
     */
    void registerCountryApi();

    /**
     * 注册设备维度API
     * 返回按设备分组的统计数据
     */
    void registerDeviceApi();

    /**
     * 注册详情API
     * 返回指定日期的详细数据
     */
    void registerDetailsApi();

    /**
     * 注册LTV API
     * 返回用户生命周期价值(LTV)数据
     * 支持按时间窗口和维度查询
     */
    void registerLtvApi();
}; 