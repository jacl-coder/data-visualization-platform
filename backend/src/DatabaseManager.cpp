#include "DatabaseManager.h"
#include <iostream>
#include <stdexcept>

DatabaseManager::DatabaseManager(const std::string& dbPath) 
    : db(nullptr), connected(false) {
    
    int rc = sqlite3_open(dbPath.c_str(), &db);
    if (rc != SQLITE_OK) {
        std::cerr << "Cannot open database: " << sqlite3_errmsg(db) << std::endl;
        sqlite3_close(db);
        db = nullptr;
        return;
    }
    
    connected = true;
}

DatabaseManager::~DatabaseManager() {
    if (db) {
        sqlite3_close(db);
        db = nullptr;
    }
}

DatabaseManager::ResultSet DatabaseManager::executeQuery(
    const std::string& sql, 
    const std::vector<std::string>& params) {
    
    ResultSet resultSet;
    if (!connected) {
        throw std::runtime_error("Database is not connected");
    }
    
    sqlite3_stmt* stmt;
    int rc = sqlite3_prepare_v2(db, sql.c_str(), -1, &stmt, nullptr);
    
    if (rc != SQLITE_OK) {
        std::string error = sqlite3_errmsg(db);
        throw std::runtime_error("SQL prepare error: " + error);
    }
    
    // 绑定参数
    bindParameters(stmt, params);
    
    // 获取列数
    int colCount = sqlite3_column_count(stmt);
    
    // 获取列名
    std::vector<std::string> columnNames;
    for (int i = 0; i < colCount; i++) {
        const char* colName = sqlite3_column_name(stmt, i);
        columnNames.push_back(colName);
    }
    
    // 获取结果
    while (sqlite3_step(stmt) == SQLITE_ROW) {
        Row row;
        
        for (int i = 0; i < colCount; i++) {
            // 获取列值
            const char* value = reinterpret_cast<const char*>(sqlite3_column_text(stmt, i));
            row[columnNames[i]] = value ? value : "";
        }
        
        resultSet.push_back(row);
    }
    
    sqlite3_finalize(stmt);
    return resultSet;
}

int DatabaseManager::executeUpdate(
    const std::string& sql, 
    const std::vector<std::string>& params) {
    
    if (!connected) {
        throw std::runtime_error("Database is not connected");
    }
    
    sqlite3_stmt* stmt;
    int rc = sqlite3_prepare_v2(db, sql.c_str(), -1, &stmt, nullptr);
    
    if (rc != SQLITE_OK) {
        std::string error = sqlite3_errmsg(db);
        throw std::runtime_error("SQL prepare error: " + error);
    }
    
    // 绑定参数
    bindParameters(stmt, params);
    
    // 执行
    rc = sqlite3_step(stmt);
    sqlite3_finalize(stmt);
    
    if (rc != SQLITE_DONE) {
        std::string error = sqlite3_errmsg(db);
        throw std::runtime_error("SQL execution error: " + error);
    }
    
    // 返回受影响的行数
    return sqlite3_changes(db);
}

bool DatabaseManager::isConnected() const {
    return connected;
}

void DatabaseManager::bindParameters(
    sqlite3_stmt* stmt, 
    const std::vector<std::string>& params) {
    
    for (size_t i = 0; i < params.size(); i++) {
        sqlite3_bind_text(stmt, i+1, params[i].c_str(), -1, SQLITE_TRANSIENT);
    }
} 