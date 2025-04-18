#include "ApiServer.h"
#include <iostream>
#include <string>
#include <vector>
#include "json.hpp"

// 简化JSON使用
using json = nlohmann::json;

// CORSMiddleware类已移至ApiServer.h

// 创建统一的API成功响应，同时添加CORS头
json createSuccessResponse(const json& data, const std::string& message = "数据获取成功") {
    json response;
    response["status"] = "success";
    response["code"] = 200;
    response["message"] = message;
    response["data"] = data;
    return response;
}

// 创建API错误响应，同时添加CORS头
json createErrorResponse(int code, const std::string& message) {
    json response;
    response["status"] = "error";
    response["code"] = code;
    response["message"] = message;
    response["data"] = nullptr;
    return response;
}

// 辅助函数：为响应添加CORS头
void addCorsHeaders(crow::response& res) {
    res.set_header("Access-Control-Allow-Origin", "*");
    res.set_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS");
    res.set_header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept, Authorization");
    res.set_header("Access-Control-Allow-Credentials", "true");
    res.set_header("Access-Control-Max-Age", "86400"); // 24小时缓存预检请求
}

ApiServer::ApiServer(const std::string& dbPath, int port)
    : port(port), running(false) {
    
    // 创建数据库连接
    dbManager = std::make_shared<DatabaseManager>(dbPath);
    
    if (!dbManager->isConnected()) {
        throw std::runtime_error("Failed to connect to database");
    }
    
    // 设置路由
    setupRoutes();
}

void ApiServer::start() {
    if (running) {
        return;
    }
    
    running = true;
    std::cout << "Server starting on port " << port << std::endl;
    
    // 启动Crow应用
    app.port(port).multithreaded().run();
}

void ApiServer::stop() {
    if (!running) {
        return;
    }
    
    running = false;
    std::cout << "Server stopping..." << std::endl;
    
    // 停止Crow应用
    app.stop();
}

void ApiServer::setupRoutes() {
    // 注册所有API路由
    registerOverviewApi();
    registerTimelineApi();
    registerCountryApi();
    registerDeviceApi();
    registerDetailsApi();

    app.route_dynamic("/api/(.*)")
    .methods("OPTIONS"_method)
    ([](const crow::request&) {
        crow::response res;
        res.set_header("Access-Control-Allow-Origin", "*");
        res.set_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS");
        res.set_header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept, Authorization");
        res.set_header("Access-Control-Allow-Credentials", "true");
        res.set_header("Access-Control-Max-Age", "86400"); // 24小时缓存预检请求
        res.code = 204;
        return res;
    });
    
    // 添加根路由
    app.route_dynamic("/")
    ([](const crow::request&) {
        crow::response res;
        // 使用统一的响应格式，即使是简单的文本响应
        json data = "Data Visualization API Server";
        res.body = createSuccessResponse(data, "API服务器运行正常").dump();
        res.set_header("Content-Type", "application/json");
        // 添加CORS头
        addCorsHeaders(res);
        return res;
    });
}

void ApiServer::registerOverviewApi() {
    app.route_dynamic("/api/overview")
    ([this](const crow::request&) {
        try {
            // 查询用户总数
            auto userResult = dbManager->executeQuery(
                "SELECT COUNT(DISTINCT appsflyer_id) as user_count FROM users"
            );
            
            // 查询事件总数
            auto eventResult = dbManager->executeQuery(
                "SELECT COUNT(*) as event_count FROM events"
            );
            
            // 查询设备总数
            auto deviceResult = dbManager->executeQuery(
                "SELECT COUNT(DISTINCT device_category) as device_count FROM events"
            );
            
            // 查询总收入
            auto revenueResult = dbManager->executeQuery(
                "SELECT SUM(event_revenue_usd) as total_revenue FROM events WHERE event_name = 'af_purchase'"
            );
            
            // 创建数据对象
            json data;
            data["user_count"] = std::stoi(userResult[0]["user_count"]);
            data["event_count"] = std::stoi(eventResult[0]["event_count"]);
            data["device_count"] = std::stoi(deviceResult[0]["device_count"]);
            data["total_revenue"] = std::stod(revenueResult[0]["total_revenue"]);
            
            // 使用统一的响应格式
            crow::response res;
            res.body = createSuccessResponse(data, "概览数据获取成功").dump();
            res.set_header("Content-Type", "application/json");
            // 添加CORS头
            addCorsHeaders(res);
            return res;
        } catch (const std::exception& e) {
            crow::response res;
            res.code = 500;
            res.body = createErrorResponse(500, e.what()).dump();
            res.set_header("Content-Type", "application/json");
            // 添加CORS头
            addCorsHeaders(res);
            return res;
        }
    });
}

void ApiServer::registerTimelineApi() {
    app.route_dynamic("/api/timeline")
    ([this](const crow::request& req) {
        try {
            std::string whereClause = "";
            std::vector<std::string> params;
            std::string limitClause = "";
            
            // 检查是否有日期范围参数
            if (req.url_params.get("dateRange") != nullptr) {
                std::string dateParam = req.url_params.get("dateRange");
                
                // 检查是否是日期范围查询（格式：startDate|endDate）
                size_t separatorPos = dateParam.find('|');
                if (separatorPos != std::string::npos) {
                    // 日期范围查询
                    std::string startDate = dateParam.substr(0, separatorPos);
                    std::string endDate = dateParam.substr(separatorPos + 1);
                    
                    whereClause = " WHERE stat_date BETWEEN ? AND ? ";
                    params.push_back(startDate);
                    params.push_back(endDate);
                    
                    // 不使用LIMIT子句
                    limitClause = "";
                }
            } else {
                // 兼容旧的days参数
                int days = 30;
                if (req.url_params.get("days") != nullptr) {
                    days = std::stoi(req.url_params.get("days"));
                }
                
                // 使用LIMIT子句
                limitClause = " LIMIT ?";
                params.push_back(std::to_string(days));
            }
            
            // 查询每日数据
            auto result = dbManager->executeQuery(
                "SELECT stat_date, user_count, event_count, revenue_usd, device_count "
                "FROM daily_stats " +
                whereClause +
                "ORDER BY stat_date DESC" +
                limitClause,
                params
            );
            
            // 创建数据数组
            json dataArray = json::array();
            for (const auto& row : result) {
                json item;
                item["date"] = row.at("stat_date");
                item["user_count"] = std::stoi(row.at("user_count"));
                item["event_count"] = std::stoi(row.at("event_count"));
                item["revenue"] = std::stod(row.at("revenue_usd"));
                item["device_count"] = std::stoi(row.at("device_count"));
                dataArray.push_back(item);
            }
            
            // 创建包含元数据的响应
            json responseData;
            responseData["items"] = dataArray;
            responseData["total"] = dataArray.size();
            
            // 使用统一的响应格式
            crow::response res;
            res.body = createSuccessResponse(responseData, "时间线数据获取成功").dump();
            res.set_header("Content-Type", "application/json");
            // 添加CORS头
            addCorsHeaders(res);
            return res;
        } catch (const std::exception& e) {
            crow::response res;
            res.code = 500;
            res.body = createErrorResponse(500, e.what()).dump();
            res.set_header("Content-Type", "application/json");
            // 添加CORS头
            addCorsHeaders(res);
            return res;
        }
    });
}

void ApiServer::registerCountryApi() {
    app.route_dynamic("/api/country")
    ([this](const crow::request& req) {
        try {
            std::string whereClause = "";
            std::vector<std::string> params;
            
            // 检查是否有日期参数
            if (req.url_params.get("date") != nullptr) {
                std::string dateParam = req.url_params.get("date");
                
                // 检查是否是日期范围查询（格式：startDate|endDate）
                size_t separatorPos = dateParam.find('|');
                if (separatorPos != std::string::npos) {
                    // 日期范围查询
                    std::string startDate = dateParam.substr(0, separatorPos);
                    std::string endDate = dateParam.substr(separatorPos + 1);
                    
                    whereClause = " WHERE stat_date BETWEEN ? AND ? ";
                    params.push_back(startDate);
                    params.push_back(endDate);
                } else {
                    // 单一日期查询
                    whereClause = " WHERE stat_date = ? ";
                    params.push_back(dateParam);
                }
            }
            
            // 查询各国家数据，使用日期参数
            auto result = dbManager->executeQuery(
                "SELECT country_code, SUM(user_count) as total_users, "
                "SUM(revenue_usd) as revenue "
                "FROM country_stats " +
                whereClause +
                "GROUP BY country_code "
                "ORDER BY revenue DESC",
                params
            );
            
            // 创建数据数组
            json dataArray = json::array();
            for (const auto& row : result) {
                json countryData;
                countryData["country"] = row.at("country_code");
                countryData["users"] = std::stoi(row.at("total_users"));
                countryData["revenue"] = std::stod(row.at("revenue"));
                dataArray.push_back(countryData);
            }
            
            // 创建包含元数据的响应
            json responseData;
            responseData["items"] = dataArray;
            responseData["total"] = dataArray.size();
            
            // 使用统一的响应格式
            crow::response res;
            res.body = createSuccessResponse(responseData, "国家维度数据获取成功").dump();
            res.set_header("Content-Type", "application/json");
            // 添加CORS头
            addCorsHeaders(res);
            return res;
        } catch (const std::exception& e) {
            crow::response res;
            res.code = 500;
            res.body = createErrorResponse(500, e.what()).dump();
            res.set_header("Content-Type", "application/json");
            // 添加CORS头
            addCorsHeaders(res);
            return res;
        }
    });
}

void ApiServer::registerDeviceApi() {
    app.route_dynamic("/api/device")
    ([this](const crow::request& req) {
        try {
            std::string whereClause = "";
            std::vector<std::string> params;
            
            // 检查是否有日期参数
            if (req.url_params.get("date") != nullptr) {
                std::string dateParam = req.url_params.get("date");
                
                // 检查是否是日期范围查询（格式：startDate|endDate）
                size_t separatorPos = dateParam.find('|');
                if (separatorPos != std::string::npos) {
                    // 日期范围查询
                    std::string startDate = dateParam.substr(0, separatorPos);
                    std::string endDate = dateParam.substr(separatorPos + 1);
                    
                    whereClause = " WHERE stat_date BETWEEN ? AND ? ";
                    params.push_back(startDate);
                    params.push_back(endDate);
                } else {
                    // 单一日期查询
                    whereClause = " WHERE stat_date = ? ";
                    params.push_back(dateParam);
                }
            }
            
            // 查询各设备数据，使用日期参数
            auto result = dbManager->executeQuery(
                "SELECT device_category, SUM(user_count) as total_users, "
                "SUM(revenue_usd) as revenue "
                "FROM device_stats " +
                whereClause +
                "GROUP BY device_category "
                "ORDER BY revenue DESC",
                params
            );
            
            // 创建数据数组
            json dataArray = json::array();
            for (const auto& row : result) {
                json deviceData;
                deviceData["device"] = row.at("device_category");
                deviceData["users"] = std::stoi(row.at("total_users"));
                deviceData["revenue"] = std::stod(row.at("revenue"));
                dataArray.push_back(deviceData);
            }
            
            // 创建包含元数据的响应
            json responseData;
            responseData["items"] = dataArray;
            responseData["total"] = dataArray.size();
            
            // 使用统一的响应格式
            crow::response res;
            res.body = createSuccessResponse(responseData, "设备维度数据获取成功").dump();
            res.set_header("Content-Type", "application/json");
            // 添加CORS头
            addCorsHeaders(res);
            return res;
        } catch (const std::exception& e) {
            crow::response res;
            res.code = 500;
            res.body = createErrorResponse(500, e.what()).dump();
            res.set_header("Content-Type", "application/json");
            // 添加CORS头
            addCorsHeaders(res);
            return res;
        }
    });
}

void ApiServer::registerDetailsApi() {
    app.route_dynamic("/api/details")
    ([this](const crow::request& req) {
        try {
            // 获取日期参数
            if (req.url_params.get("date") == nullptr) {
                throw std::runtime_error("Missing required parameter: date");
            }
            
            std::string date = req.url_params.get("date");
            
            // 查询指定日期的详细数据
            auto userCountryResult = dbManager->executeQuery(
                "SELECT country_code, COUNT(DISTINCT appsflyer_id) as user_count "
                "FROM events "
                "WHERE created_date = ? "
                "GROUP BY country_code "
                "ORDER BY user_count DESC",
                {date}
            );
            
            auto userDeviceResult = dbManager->executeQuery(
                "SELECT device_category, COUNT(DISTINCT appsflyer_id) as user_count "
                "FROM events "
                "WHERE created_date = ? "
                "GROUP BY device_category "
                "ORDER BY user_count DESC",
                {date}
            );
            
            auto revenueResult = dbManager->executeQuery(
                "SELECT COALESCE(SUM(event_revenue_usd), 0) as total_revenue "
                "FROM events "
                "WHERE created_date = ? AND event_name = 'af_purchase'",
                {date}
            );
            
            // 创建数据对象
            json data;
            data["date"] = date;
            
            // 安全处理可能为空的total_revenue
            double totalRevenue = 0.0;
            if (!revenueResult.empty() && !revenueResult[0]["total_revenue"].empty()) {
                try {
                    totalRevenue = std::stod(revenueResult[0]["total_revenue"]);
                } catch (const std::exception&) {
                    // 转换失败时使用默认值0
                    totalRevenue = 0.0;
                }
            }
            data["total_revenue"] = totalRevenue;
            
            json countries = json::array();
            for (const auto& row : userCountryResult) {
                json item;
                item["country"] = row.at("country_code");
                item["users"] = std::stoi(row.at("user_count"));
                countries.push_back(item);
            }
            data["countries"] = countries;
            
            json devices = json::array();
            for (const auto& row : userDeviceResult) {
                json item;
                item["device"] = row.at("device_category");
                item["users"] = std::stoi(row.at("user_count"));
                devices.push_back(item);
            }
            data["devices"] = devices;
            
            // 使用统一的响应格式
            crow::response res;
            res.body = createSuccessResponse(data, "日期详情数据获取成功").dump();
            res.set_header("Content-Type", "application/json");
            // 添加CORS头
            addCorsHeaders(res);
            return res;
        } catch (const std::exception& e) {
            crow::response res;
            res.code = 500;
            res.body = createErrorResponse(500, e.what()).dump();
            res.set_header("Content-Type", "application/json");
            // 添加CORS头
            addCorsHeaders(res);
            return res;
        }
    });
}