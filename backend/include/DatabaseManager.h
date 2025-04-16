#pragma once

#include <sqlite3.h>
#include <string>
#include <vector>
#include <map>
#include <memory>

/**
 * 数据库管理器类
 * 处理与SQLite数据库的连接和查询
 */
class DatabaseManager {
public:
    using Row = std::map<std::string, std::string>;
    using ResultSet = std::vector<Row>;

    /**
     * 构造函数
     * @param dbPath 数据库文件路径
     */
    DatabaseManager(const std::string& dbPath);

    /**
     * 析构函数
     */
    ~DatabaseManager();

    /**
     * 执行SQL查询并返回结果集
     * @param sql SQL查询语句
     * @param params 查询参数
     * @return 结果集
     */
    ResultSet executeQuery(const std::string& sql, const std::vector<std::string>& params = {});

    /**
     * 执行更新操作（INSERT, UPDATE, DELETE）
     * @param sql SQL语句
     * @param params 查询参数
     * @return 受影响的行数
     */
    int executeUpdate(const std::string& sql, const std::vector<std::string>& params = {});

    /**
     * 检查连接是否成功
     * @return 连接状态
     */
    bool isConnected() const;

private:
    sqlite3* db;
    bool connected;

    /**
     * 绑定参数到SQL语句
     * @param stmt 准备好的SQL语句
     * @param params 参数列表
     */
    void bindParameters(sqlite3_stmt* stmt, const std::vector<std::string>& params);
}; 