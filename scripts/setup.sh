#!/bin/bash
# 数据分析与可视化平台一键安装运行脚本
# 作者：lxp
# 版本：1.0

# 设置终端颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 获取项目根目录(脚本所在目录的父目录)
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"
DATA_PROCESSING_DIR="$PROJECT_DIR/data_processing"
DATABASE_DIR="$PROJECT_DIR/database"

# 后端和前端服务的URL
BACKEND_URL="http://localhost:40001"
FRONTEND_URL="http://localhost:40000"

# 记录进程ID
BACKEND_PID=""
FRONTEND_PID=""

# 项目依赖版本
REQUIRED_PYTHON_VERSION="3.9"
REQUIRED_NODE_VERSION="18"
REQUIRED_NPM_VERSION="7"
REQUIRED_CMAKE_VERSION="3.20"

# 打印欢迎信息
function print_welcome() {
    echo -e "${BLUE}=======================================================${NC}"
    echo -e "${BLUE}   数据分析与可视化平台安装与运行工具               ${NC}"
    echo -e "${BLUE}=======================================================${NC}"
    echo -e "${GREEN}该脚本将自动完成以下任务：${NC}"
    echo -e "  1. 检查系统环境和必要依赖"
    echo -e "  2. 安装Python依赖"
    echo -e "  3. 创建数据库和处理数据"
    echo -e "  4. 编译C++后端"
    echo -e "  5. 安装前端依赖并运行"
    echo -e "  6. 打开浏览器展示应用"
    echo -e "${BLUE}=======================================================${NC}"
    echo
}

# 检查并安装依赖
function check_dependencies() {
    echo -e "${BLUE}[1/6] 检查系统环境和必要依赖...${NC}"
    
    # 检测操作系统类型
    OS_TYPE=""
    if [ -f /etc/debian_version ]; then
        OS_TYPE="debian"
        echo -e "  - 检测到 Debian/Ubuntu 系统"
    elif [ -f /etc/redhat-release ]; then
        OS_TYPE="redhat"
        echo -e "  - 检测到 CentOS/RHEL/Fedora 系统"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS_TYPE="mac"
        echo -e "  - 检测到 macOS 系统"
    else
        echo -e "${YELLOW}警告: 未能确定操作系统类型，可能无法自动安装依赖${NC}"
    fi
    
    # 检查Python
    if ! command -v python3 &> /dev/null; then
        echo -e "${YELLOW}未找到Python 3，尝试自动安装...${NC}"
        if [ "$OS_TYPE" == "debian" ]; then
            sudo apt-get update && sudo apt-get install -y python3 python3-dev
        elif [ "$OS_TYPE" == "redhat" ]; then
            sudo yum install -y python3 python3-devel
        elif [ "$OS_TYPE" == "mac" ]; then
            brew install python
        else
            echo -e "${RED}错误: 未找到Python 3${NC}"
            echo -e "请手动安装Python 3.9或更高版本后重试"
            exit 1
        fi
        
        # 再次检查是否已安装
        if ! command -v python3 &> /dev/null; then
            echo -e "${RED}错误: Python 3安装失败${NC}"
            exit 1
        else
            echo -e "${GREEN}Python 3安装成功!${NC}"
        fi
    fi
    
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    echo -e "  - 检测到Python版本: ${GREEN}$PYTHON_VERSION${NC}"
    
    if (( $(echo "$PYTHON_VERSION < $REQUIRED_PYTHON_VERSION" | bc -l) )); then
        echo -e "${YELLOW}警告: 推荐Python版本 $REQUIRED_PYTHON_VERSION 或更高${NC}"
    fi
    
    # 检查pip
    if ! command -v pip3 &> /dev/null; then
        echo -e "${YELLOW}未找到pip3，尝试自动安装...${NC}"
        if [ "$OS_TYPE" == "debian" ]; then
            sudo apt-get update && sudo apt-get install -y python3-pip
        elif [ "$OS_TYPE" == "redhat" ]; then
            sudo yum install -y python3-pip
        elif [ "$OS_TYPE" == "mac" ]; then
            curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
            python3 get-pip.py
            rm get-pip.py
        else
            echo -e "${RED}错误: 未找到pip3${NC}"
            echo -e "请手动安装pip后重试"
            exit 1
        fi
        
        # 再次检查是否已安装
        if ! command -v pip3 &> /dev/null; then
            echo -e "${RED}错误: pip3安装失败${NC}"
            exit 1
        else
            echo -e "${GREEN}pip3安装成功!${NC}"
        fi
    fi
    echo -e "  - 检测到pip: ${GREEN}$(pip3 --version | awk '{print $2}')${NC}"
    
    # 检查Node.js
    if ! command -v node &> /dev/null; then
        echo -e "${YELLOW}未找到Node.js，尝试自动安装...${NC}"
        if [ "$OS_TYPE" == "debian" ]; then
            # 安装最新的Node.js 18.x LTS版本
            echo -e "  - 安装Node.js 18.x LTS版本..."
            curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
            sudo apt-get install -y nodejs
        elif [ "$OS_TYPE" == "redhat" ]; then
            # 安装最新的Node.js 18.x LTS版本
            echo -e "  - 安装Node.js 18.x LTS版本..."
            curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
            sudo yum install -y nodejs
        elif [ "$OS_TYPE" == "mac" ]; then
            brew install node@18
            brew link node@18
        else
            echo -e "${RED}错误: 未找到Node.js${NC}"
            echo -e "请手动安装Node.js $REQUIRED_NODE_VERSION 或更高版本后重试"
            echo -e "推荐安装Node.js 18.x LTS版本，可以访问 https://nodejs.org/en/download/ 获取安装包"
            exit 1
        fi
        
        # 再次检查是否已安装
        if ! command -v node &> /dev/null; then
            echo -e "${RED}错误: Node.js安装失败${NC}"
            exit 1
        else
            echo -e "${GREEN}Node.js安装成功!${NC}"
        fi
    fi
    
    NODE_VERSION=$(node -v | cut -d 'v' -f 2)
    echo -e "  - 检测到Node.js版本: ${GREEN}$NODE_VERSION${NC}"
    
    # 将版本号分解为主版本号
    NODE_MAJOR_VERSION=$(echo $NODE_VERSION | cut -d '.' -f 1)
    
    if (( $NODE_MAJOR_VERSION < 14 )); then
        echo -e "${RED}错误: Node.js版本过低 (需要 14+ 版本)${NC}"
        echo -e "当前版本 $NODE_VERSION 不支持Vite所需的ES模块语法"
        echo -e "请升级Node.js版本:"
        
        if [ "$OS_TYPE" == "debian" ]; then
            echo -e "  - 尝试自动升级到Node.js 18.x LTS版本..."
            curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
            sudo apt-get install -y nodejs
        elif [ "$OS_TYPE" == "redhat" ]; then
            echo -e "  - 尝试自动升级到Node.js 18.x LTS版本..."
            curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
            sudo yum install -y nodejs
        elif [ "$OS_TYPE" == "mac" ]; then
            echo -e "  - 尝试自动升级Node.js..."
            brew install node@18
            brew link --overwrite node@18
        else
            echo -e "请手动升级Node.js到 18.x LTS版本"
            echo -e "可以访问 https://nodejs.org/en/download/ 获取安装包"
            exit 1
        fi
        
        # 再次检查版本
        NODE_VERSION=$(node -v | cut -d 'v' -f 2)
        NODE_MAJOR_VERSION=$(echo $NODE_VERSION | cut -d '.' -f 1)
        
        if (( $NODE_MAJOR_VERSION < 14 )); then
            echo -e "${RED}错误: Node.js升级失败，版本仍然太低${NC}"
            echo -e "请手动升级Node.js到 18.x LTS版本"
            exit 1
        else
            echo -e "${GREEN}Node.js升级成功! 当前版本: $NODE_VERSION${NC}"
        fi
    elif (( $NODE_MAJOR_VERSION < 18 )) && (( $NODE_MAJOR_VERSION >= 14 )); then
        echo -e "${YELLOW}警告: 建议使用Node.js 18.x LTS版本以获得最佳兼容性${NC}"
        echo -e "当前版本 $NODE_VERSION 可能工作，但不推荐"
        
        # 询问用户是否要升级
        read -p "是否升级到Node.js 18.x LTS版本? (y/n): " -n 1 -r REPLY
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            if [ "$OS_TYPE" == "debian" ]; then
                echo -e "  - 升级到Node.js 18.x LTS版本..."
                curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
                sudo apt-get install -y nodejs
            elif [ "$OS_TYPE" == "redhat" ]; then
                echo -e "  - 升级到Node.js 18.x LTS版本..."
                curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
                sudo yum install -y nodejs
            elif [ "$OS_TYPE" == "mac" ]; then
                echo -e "  - 升级Node.js..."
                brew install node@18
                brew link --overwrite node@18
            else
                echo -e "${YELLOW}无法自动升级Node.js，继续使用当前版本${NC}"
            fi
            
            # 再次检查版本
            NODE_VERSION=$(node -v | cut -d 'v' -f 2)
            echo -e "  - 当前Node.js版本: ${GREEN}$NODE_VERSION${NC}"
        else
            echo -e "  - 继续使用当前Node.js版本: $NODE_VERSION"
        fi
    fi
    
    # 检查npm
    if ! command -v npm &> /dev/null; then
        echo -e "${YELLOW}未找到npm，尝试自动安装...${NC}"
        if [ "$OS_TYPE" == "debian" ]; then
            sudo apt-get update && sudo apt-get install -y npm
        elif [ "$OS_TYPE" == "redhat" ]; then
            sudo yum install -y npm
        elif [ "$OS_TYPE" == "mac" ]; then
            brew install npm
        else
            echo -e "${RED}错误: 未找到npm${NC}"
            echo -e "请手动安装npm后重试"
            exit 1
        fi
        
        # 再次检查是否已安装
        if ! command -v npm &> /dev/null; then
            echo -e "${RED}错误: npm安装失败${NC}"
            exit 1
        else
            echo -e "${GREEN}npm安装成功!${NC}"
        fi
    fi
    
    NPM_VERSION=$(npm -v)
    echo -e "  - 检测到npm版本: ${GREEN}$NPM_VERSION${NC}"
    
    if (( $(echo "$NPM_VERSION < $REQUIRED_NPM_VERSION" | bc -l) )); then
        echo -e "${YELLOW}警告: 推荐npm版本 $REQUIRED_NPM_VERSION 或更高${NC}"
    fi
    
    # 检查C++编译器
    if ! command -v g++ &> /dev/null; then
        echo -e "${YELLOW}未找到C++编译器，尝试自动安装...${NC}"
        if [ "$OS_TYPE" == "debian" ]; then
            sudo apt-get update && sudo apt-get install -y build-essential
        elif [ "$OS_TYPE" == "redhat" ]; then
            sudo yum install -y gcc-c++ make
        elif [ "$OS_TYPE" == "mac" ]; then
            xcode-select --install
            # 等待Xcode CLI工具安装完成
            echo -e "${YELLOW}正在安装Xcode命令行工具，请在弹出窗口中确认安装，然后等待安装完成...${NC}"
            sleep 5
            while ! command -v g++ &> /dev/null; do
                sleep 5
                echo -e "  - 等待安装完成..."
            done
        else
            echo -e "${RED}错误: 未找到C++编译器${NC}"
            echo -e "请手动安装g++或其他C++编译器后重试"
            exit 1
        fi
        
        # 再次检查是否已安装
        if ! command -v g++ &> /dev/null; then
            echo -e "${RED}错误: C++编译器安装失败${NC}"
            exit 1
        else
            echo -e "${GREEN}C++编译器安装成功!${NC}"
        fi
    fi
    
    GCC_VERSION=$(g++ --version | head -n1 | awk '{print $NF}')
    echo -e "  - 检测到g++版本: ${GREEN}$GCC_VERSION${NC}"
    
    # 检查CMake
    if ! command -v cmake &> /dev/null; then
        echo -e "${YELLOW}未找到cmake，尝试自动安装...${NC}"
        if [ "$OS_TYPE" == "debian" ]; then
            sudo apt-get update && sudo apt-get install -y cmake
        elif [ "$OS_TYPE" == "redhat" ]; then
            sudo yum install -y cmake
        elif [ "$OS_TYPE" == "mac" ]; then
            brew install cmake
        else
            echo -e "${RED}错误: 未找到cmake${NC}"
            echo -e "请手动安装cmake $REQUIRED_CMAKE_VERSION 或更高版本后重试"
            exit 1
        fi
        
        # 再次检查是否已安装
        if ! command -v cmake &> /dev/null; then
            echo -e "${RED}错误: cmake安装失败${NC}"
            exit 1
        else
            echo -e "${GREEN}cmake安装成功!${NC}"
        fi
    fi
    
    CMAKE_VERSION=$(cmake --version | head -n1 | awk '{print $3}')
    echo -e "  - 检测到cmake版本: ${GREEN}$CMAKE_VERSION${NC}"
    
    if (( $(echo "$CMAKE_VERSION < $REQUIRED_CMAKE_VERSION" | bc -l) )); then
        echo -e "${YELLOW}警告: 推荐cmake版本 $REQUIRED_CMAKE_VERSION 或更高${NC}"
    fi
    
    # 检查SQLite
    if ! command -v sqlite3 &> /dev/null; then
        echo -e "${YELLOW}未找到sqlite3，尝试自动安装...${NC}"
        if [ "$OS_TYPE" == "debian" ]; then
            sudo apt-get update && sudo apt-get install -y sqlite3 libsqlite3-dev
        elif [ "$OS_TYPE" == "redhat" ]; then
            sudo yum install -y sqlite sqlite-devel
        elif [ "$OS_TYPE" == "mac" ]; then
            brew install sqlite
        else
            echo -e "${RED}错误: 未找到sqlite3${NC}"
            echo -e "请手动安装sqlite3后重试"
            exit 1
        fi
        
        # 再次检查是否已安装
        if ! command -v sqlite3 &> /dev/null; then
            echo -e "${RED}错误: sqlite3安装失败${NC}"
            exit 1
        else
            echo -e "${GREEN}sqlite3安装成功!${NC}"
        fi
    else
        # 即使sqlite3命令存在，也确保安装了开发库
        echo -e "  - 检测到sqlite3已安装，确保开发库也已安装..."
        if [ "$OS_TYPE" == "debian" ]; then
            sudo apt-get update && sudo apt-get install -y libsqlite3-dev
            echo -e "  - ${GREEN}确保libsqlite3-dev已安装√${NC}"
        elif [ "$OS_TYPE" == "redhat" ]; then
            sudo yum install -y sqlite-devel
            echo -e "  - ${GREEN}确保sqlite-devel已安装√${NC}"
        elif [ "$OS_TYPE" == "mac" ]; then
            # macOS上的sqlite通常已包含开发文件
            echo -e "  - ${GREEN}macOS上的sqlite包含开发文件√${NC}"
        fi
    fi
    
    SQLITE_VERSION=$(sqlite3 --version | awk '{print $1}')
    echo -e "  - 检测到sqlite3版本: ${GREEN}$SQLITE_VERSION${NC}"
    
    # 检查curl（用于检测服务是否就绪）
    if ! command -v curl &> /dev/null; then
        echo -e "${YELLOW}未找到curl命令，尝试自动安装...${NC}"
        if [ "$OS_TYPE" == "debian" ]; then
            sudo apt-get update && sudo apt-get install -y curl
        elif [ "$OS_TYPE" == "redhat" ]; then
            sudo yum install -y curl
        elif [ "$OS_TYPE" == "mac" ]; then
            brew install curl
        else
            echo -e "${RED}错误: 未找到curl命令${NC}"
            echo -e "请手动安装curl后重试"
            exit 1
        fi
        
        # 再次检查是否已安装
        if ! command -v curl &> /dev/null; then
            echo -e "${RED}错误: curl安装失败${NC}"
            echo -e "请手动安装curl后重试"
            exit 1
        else
            echo -e "${GREEN}curl安装成功!${NC}"
        fi
    fi
    echo -e "  - 检测到curl已安装"
    
    # 检查Asio库（C++后端依赖）
    echo -e "  - 检查Asio库..."
    if [ "$OS_TYPE" == "debian" ]; then
        if ! dpkg -l | grep -q libasio-dev; then
            echo -e "${YELLOW}未找到Asio库，尝试自动安装...${NC}"
            sudo apt-get update && sudo apt-get install -y libasio-dev
            if dpkg -l | grep -q libasio-dev; then
                echo -e "${GREEN}Asio库安装成功!${NC}"
            else
                echo -e "${RED}错误: Asio库安装失败${NC}"
                echo -e "请手动安装: sudo apt-get install libasio-dev"
                exit 1
            fi
        else
            echo -e "  - 检测到Asio库已安装"
        fi
    elif [ "$OS_TYPE" == "redhat" ]; then
        if ! rpm -qa | grep -q asio; then
            echo -e "${YELLOW}未找到Asio库，尝试自动安装...${NC}"
            sudo yum install -y asio-devel
            if rpm -qa | grep -q asio; then
                echo -e "${GREEN}Asio库安装成功!${NC}"
            else
                echo -e "${RED}错误: Asio库安装失败${NC}"
                echo -e "请手动安装: sudo yum install asio-devel"
                exit 1
            fi
        else
            echo -e "  - 检测到Asio库已安装"
        fi
    elif [ "$OS_TYPE" == "mac" ]; then
        if ! brew list --formula | grep -q asio; then
            echo -e "${YELLOW}未找到Asio库，尝试自动安装...${NC}"
            brew install asio
            if brew list --formula | grep -q asio; then
                echo -e "${GREEN}Asio库安装成功!${NC}"
            else
                echo -e "${RED}错误: Asio库安装失败${NC}"
                echo -e "请手动安装: brew install asio"
                exit 1
            fi
        else
            echo -e "  - 检测到Asio库已安装"
        fi
    else
        echo -e "${YELLOW}警告: 无法自动检测或安装Asio库，如果后续构建失败，请手动安装${NC}"
        echo -e "  - Debian/Ubuntu: sudo apt-get install libasio-dev"
        echo -e "  - CentOS/RHEL/Fedora: sudo yum install asio-devel"
        echo -e "  - macOS: brew install asio"
    fi
    
    # 检查Boost库（C++后端依赖）
    echo -e "  - 检查Boost库..."
    if [ "$OS_TYPE" == "debian" ]; then
        if ! dpkg -l | grep -q libboost-system-dev || ! dpkg -l | grep -q libboost-thread-dev; then
            echo -e "${YELLOW}未找到Boost库的system或thread组件，尝试自动安装...${NC}"
            sudo apt-get update && sudo apt-get install -y libboost-system-dev libboost-thread-dev
            if dpkg -l | grep -q libboost-system-dev && dpkg -l | grep -q libboost-thread-dev; then
                echo -e "${GREEN}Boost库安装成功!${NC}"
            else
                echo -e "${YELLOW}警告: Boost库安装可能不完整，但将继续尝试构建${NC}"
                echo -e "如果构建失败，请手动安装: sudo apt-get install libboost-all-dev"
            fi
        else
            echo -e "  - 检测到Boost库system和thread组件已安装"
        fi
    elif [ "$OS_TYPE" == "redhat" ]; then
        if ! rpm -qa | grep -q boost-devel; then
            echo -e "${YELLOW}未找到Boost库，尝试自动安装...${NC}"
            sudo yum install -y boost-devel
            if rpm -qa | grep -q boost-devel; then
                echo -e "${GREEN}Boost库安装成功!${NC}"
            else
                echo -e "${YELLOW}警告: Boost库安装可能不完整，但将继续尝试构建${NC}"
                echo -e "如果构建失败，请手动安装: sudo yum install boost-devel"
            fi
        else
            echo -e "  - 检测到Boost库已安装"
        fi
    elif [ "$OS_TYPE" == "mac" ]; then
        if ! brew list --formula | grep -q boost; then
            echo -e "${YELLOW}未找到Boost库，尝试自动安装...${NC}"
            brew install boost
            if brew list --formula | grep -q boost; then
                echo -e "${GREEN}Boost库安装成功!${NC}"
            else
                echo -e "${YELLOW}警告: Boost库安装可能不完整，但将继续尝试构建${NC}"
                echo -e "如果构建失败，请手动安装: brew install boost"
            fi
        else
            echo -e "  - 检测到Boost库已安装"
        fi
    else
        echo -e "${YELLOW}警告: 无法自动检测或安装Boost库，如果后续构建失败，请手动安装${NC}"
        echo -e "  - Debian/Ubuntu: sudo apt-get install libboost-system-dev libboost-thread-dev"
        echo -e "  - CentOS/RHEL/Fedora: sudo yum install boost-devel"
        echo -e "  - macOS: brew install boost"
    fi
    
    # 检查xdg-open或open (用于打开浏览器)
    if command -v xdg-open &> /dev/null; then
        OPEN_CMD="xdg-open"
    elif command -v open &> /dev/null; then
        OPEN_CMD="open"
    else
        OPEN_CMD=""
        if [ "$OS_TYPE" == "debian" ]; then
            echo -e "${YELLOW}未找到xdg-open命令，尝试安装...${NC}"
            sudo apt-get update && sudo apt-get install -y xdg-utils
            if command -v xdg-open &> /dev/null; then
                OPEN_CMD="xdg-open"
                echo -e "${GREEN}xdg-open安装成功!${NC}"
            else
                echo -e "${YELLOW}警告: xdg-open安装失败, 将无法自动打开浏览器${NC}"
            fi
        else
            echo -e "${YELLOW}警告: 未找到xdg-open或open命令, 将无法自动打开浏览器${NC}"
        fi
    fi
    
    echo -e "${GREEN}系统环境检查完成!${NC}"
    echo
}

# 安装Python依赖
function install_python_deps() {
    echo -e "${BLUE}[2/6] 安装Python依赖...${NC}"
    
    cd "$PROJECT_DIR"
    
    # 检查python3-venv是否已安装
    if [ "$OS_TYPE" == "debian" ]; then
        if ! dpkg -l | grep -q python3-venv; then
            echo -e "${YELLOW}未找到python3-venv包，尝试安装...${NC}"
            sudo apt-get update && sudo apt-get install -y python3-venv python3-full
            if [ $? -ne 0 ]; then
                echo -e "${RED}错误: 无法安装python3-venv${NC}"
                exit 1
            fi
        fi
    elif [ "$OS_TYPE" == "redhat" ]; then
        if ! rpm -qa | grep -q python3-virtualenv; then
            echo -e "${YELLOW}未找到python3-virtualenv包，尝试安装...${NC}"
            sudo yum install -y python3-virtualenv
            if [ $? -ne 0 ]; then
                echo -e "${RED}错误: 无法安装python3-virtualenv${NC}"
                exit 1
            fi
        fi
    fi
    
    # 创建虚拟环境目录（如果不存在）
    VENV_DIR="$PROJECT_DIR/venv"
    if [ ! -d "$VENV_DIR" ]; then
        echo -e "  - 创建Python虚拟环境..."
        python3 -m venv "$VENV_DIR"
        if [ $? -ne 0 ]; then
            echo -e "${RED}错误: 无法创建Python虚拟环境${NC}"
            echo -e "请确保已安装python3-venv包: sudo apt-get install python3-venv python3-full"
            exit 1
        fi
    else
        echo -e "  - 使用已存在的Python虚拟环境"
    fi
    
    # 激活虚拟环境
    echo -e "  - 激活虚拟环境..."
    source "$VENV_DIR/bin/activate"
    
    # 升级pip
    echo -e "  - 升级pip..."
    pip install --upgrade pip
    
    cd "$DATA_PROCESSING_DIR"
    
    if [ ! -f "requirements.txt" ]; then
        echo -e "${RED}错误: 未找到data_processing/requirements.txt文件${NC}"
        deactivate
        exit 1
    fi
    
    echo -e "  - 安装项目所需Python库..."
    pip install -r requirements.txt
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}错误: Python依赖安装失败${NC}"
        deactivate
        exit 1
    fi
    
    echo -e "${GREEN}Python依赖安装完成!${NC}"
    
    # 记录虚拟环境路径，后面需要使用
    PYTHON_VENV="$VENV_DIR/bin/python3"
    
    # 暂时不退出虚拟环境，因为后面的数据处理还需要使用
    echo
}

# 创建数据库和处理数据
function process_data() {
    echo -e "${BLUE}[3/6] 创建数据库和处理数据...${NC}"
    
    cd "$DATA_PROCESSING_DIR"
    
    # 确保database目录存在
    mkdir -p "$DATABASE_DIR"
    
    echo -e "  - 运行数据处理脚本..."
    # 使用虚拟环境中的Python
    # 清空控制台输出但保留错误信息
    "$PYTHON_VENV" main.py > /dev/null
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}错误: 数据处理失败${NC}"
        deactivate
        exit 1
    fi
    
    # 检查数据库是否创建成功
    if [ ! -f "$DATABASE_DIR/app.db" ]; then
        echo -e "${RED}错误: 数据库创建失败${NC}"
        deactivate
        exit 1
    fi
    
    # 数据处理完成后退出虚拟环境
    deactivate
    
    echo -e "${GREEN}数据处理完成!${NC}"
    echo
}

# 编译后端
function build_backend() {
    echo -e "${BLUE}[4/6] 编译C++后端...${NC}"
    
    cd "$BACKEND_DIR"
    
    # 检查build目录是否存在，存在则清除内容后重新创建
    if [ -d "build" ]; then
        echo -e "  - 清除旧的构建文件..."
        rm -rf build
    fi
    
    # 创建新的build目录
    echo -e "  - 创建build目录..."
    mkdir -p build
    cd build
    
    # 确定SQLite3库的位置
    SQLITE3_INCLUDE=""
    SQLITE3_LIBRARY=""
    
    if [ "$OS_TYPE" == "debian" ]; then
        if [ -f "/usr/include/sqlite3.h" ]; then
            SQLITE3_INCLUDE="/usr/include"
        elif [ -f "/usr/local/include/sqlite3.h" ]; then
            SQLITE3_INCLUDE="/usr/local/include"
        fi
        
        if [ -f "/usr/lib/x86_64-linux-gnu/libsqlite3.so" ]; then
            SQLITE3_LIBRARY="/usr/lib/x86_64-linux-gnu/libsqlite3.so"
        elif [ -f "/usr/lib/libsqlite3.so" ]; then
            SQLITE3_LIBRARY="/usr/lib/libsqlite3.so"
        elif [ -f "/usr/local/lib/libsqlite3.so" ]; then
            SQLITE3_LIBRARY="/usr/local/lib/libsqlite3.so"
        fi
    fi
    
    echo -e "  - 配置CMake项目..."
    
    # 如果找到了SQLite3库路径，则使用它们
    if [ -n "$SQLITE3_INCLUDE" ] && [ -n "$SQLITE3_LIBRARY" ]; then
        echo -e "  - 使用手动指定的SQLite3库位置..."
        cmake -DCMAKE_BUILD_TYPE=Release \
              -DSQLite3_INCLUDE_DIR="$SQLITE3_INCLUDE" \
              -DSQLite3_LIBRARY="$SQLITE3_LIBRARY" ..
    else
        # 否则使用默认路径
        cmake -DCMAKE_BUILD_TYPE=Release ..
    fi
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}错误: CMake配置失败${NC}"
        exit 1
    fi
    
    echo -e "  - 编译项目..."
    cmake --build . --config Release
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}错误: 编译失败${NC}"
        exit 1
    fi
    
    # 检查编译结果
    if [ ! -f "api_server" ]; then
        echo -e "${RED}错误: 未找到编译后的api_server可执行文件${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}后端编译完成!${NC}"
    echo
}

# 安装前端依赖并构建
function setup_frontend() {
    echo -e "${BLUE}[5/6] 安装前端依赖...${NC}"
    
    cd "$FRONTEND_DIR"
    
    echo -e "  - 安装npm包..."
    npm install
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}错误: 前端依赖安装失败${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}前端依赖安装完成!${NC}"
    echo
}

# 启动服务并打开浏览器
function start_services() {
    echo -e "${BLUE}[6/6] 启动服务并打开浏览器...${NC}"
    
    # 启动后端服务
    cd "$BACKEND_DIR/build"
    echo -e "  - 启动后端服务..."
    ./api_server &
    BACKEND_PID=$!
    
    # 验证后端服务是否成功启动
    sleep 2
    if ! ps -p $BACKEND_PID > /dev/null; then
        echo -e "${RED}错误: 后端服务启动失败${NC}"
        cleanup
        exit 1
    fi
    
    # 等待后端服务完全启动
    echo -e "  - 等待后端服务就绪..."
    
    # 尝试连接后端API
    RETRY_COUNT=0
    MAX_RETRIES=10
    
    while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
        # 优先使用curl检查服务
        if command -v curl &> /dev/null; then
            if curl --silent --head --fail $BACKEND_URL > /dev/null; then
                echo -e "  - ${GREEN}后端服务已就绪${NC}"
                break
            fi
        # 如果curl不可用，尝试使用nc命令
        elif command -v nc &> /dev/null; then
            if nc -z -w 2 localhost 40001; then
                echo -e "  - ${GREEN}后端服务已就绪${NC}"
                break
            fi
        # 如果nc也不可用，尝试使用wget命令
        elif command -v wget &> /dev/null; then
            if wget --spider --quiet $BACKEND_URL; then
                echo -e "  - ${GREEN}后端服务已就绪${NC}"
                break
            fi
        # 最后尝试使用纯bash进行TCP连接测试
        else
            if (echo > /dev/tcp/localhost/40001) &> /dev/null; then
                echo -e "  - ${GREEN}后端服务已就绪${NC}"
                break
            fi
        fi
        
        RETRY_COUNT=$((RETRY_COUNT+1))
        
        if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
            echo -e "${RED}错误: 后端服务无响应${NC}"
            echo -e "${YELLOW}但服务进程似乎已启动，将继续尝试启动前端...${NC}"
            # 不退出，继续尝试启动前端
            break
        fi
        
        echo -e "  - 等待后端服务 (尝试 $RETRY_COUNT/$MAX_RETRIES)..."
        sleep 2
    done
    
    # 启动前端服务
    cd "$FRONTEND_DIR"
    echo -e "  - 启动前端开发服务器..."
    
    # 启动开发服务器并转入后台
    npm run dev &
    FRONTEND_PID=$!
    
    # 验证前端服务是否成功启动
    sleep 5
    if ! ps -p $FRONTEND_PID > /dev/null; then
        echo -e "${RED}错误: 前端服务启动失败${NC}"
        cleanup
        exit 1
    fi
    
    # 等待前端服务完全启动
    echo -e "  - 等待前端服务就绪..."
    
    # 尝试连接前端服务
    RETRY_COUNT=0
    MAX_RETRIES=10
    
    while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
        # 优先使用curl检查服务
        if command -v curl &> /dev/null; then
            if curl --silent --head --fail $FRONTEND_URL > /dev/null; then
                echo -e "  - ${GREEN}前端服务已就绪${NC}"
                break
            fi
        # 如果curl不可用，尝试使用nc命令
        elif command -v nc &> /dev/null; then
            if nc -z -w 2 localhost 40000; then
                echo -e "  - ${GREEN}前端服务已就绪${NC}"
                break
            fi
        # 如果nc也不可用，尝试使用wget命令
        elif command -v wget &> /dev/null; then
            if wget --spider --quiet $FRONTEND_URL; then
                echo -e "  - ${GREEN}前端服务已就绪${NC}"
                break
            fi
        # 最后尝试使用纯bash进行TCP连接测试
        else
            if (echo > /dev/tcp/localhost/40000) &> /dev/null; then
                echo -e "  - ${GREEN}前端服务已就绪${NC}"
                break
            fi
        fi
        
        RETRY_COUNT=$((RETRY_COUNT+1))
        
        if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
            echo -e "${YELLOW}警告: 前端服务无响应, 但仍将尝试打开浏览器${NC}"
            break
        fi
        
        echo -e "  - 等待前端服务 (尝试 $RETRY_COUNT/$MAX_RETRIES)..."
        sleep 2
    done
    
    # 打开浏览器
    echo -e "  - 打开浏览器..."
    if [ -n "$OPEN_CMD" ]; then
        $OPEN_CMD $FRONTEND_URL
    else
        echo -e "${YELLOW}  - 无法自动打开浏览器, 请手动访问: ${FRONTEND_URL}${NC}"
    fi
    
    echo -e "${GREEN}所有服务已成功启动!${NC}"
    echo -e "${BLUE}=======================================================${NC}"
    echo -e "${GREEN}数据分析与可视化平台已成功启动!${NC}"
    echo -e "  - 前端地址: ${FRONTEND_URL}"
    echo -e "  - 后端API: ${BACKEND_URL}"
    echo -e "${BLUE}=======================================================${NC}"
    echo
    echo -e "按 CTRL+C 停止所有服务并退出..."
    
    # 等待用户按Ctrl+C
    trap cleanup INT
    wait
}

# 清理函数
function cleanup() {
    echo -e "\n${BLUE}正在清理资源...${NC}"
    
    if [ -n "$BACKEND_PID" ]; then
        echo -e "  - 停止后端服务 (PID: $BACKEND_PID)..."
        kill $BACKEND_PID 2>/dev/null || true
    fi
    
    if [ -n "$FRONTEND_PID" ]; then
        echo -e "  - 停止前端服务 (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID 2>/dev/null || true
        
        # 也kill掉可能的子进程
        pkill -P $FRONTEND_PID 2>/dev/null || true
    fi
    
    echo -e "${GREEN}清理完成!${NC}"
    echo -e "${BLUE}=======================================================${NC}"
    echo -e "${GREEN}感谢使用数据分析与可视化平台!${NC}"
    echo -e "${BLUE}=======================================================${NC}"
    exit 0
}

# 主函数
function main() {
    print_welcome
    
    # 等待用户确认，改为(Y/n)格式，回车默认为是
    read -p "是否继续安装? (Y/n): " -n 1 -r REPLY
    echo
    # 如果用户输入为空（直接回车）或者输入Y/y，则继续
    if [[ -z "$REPLY" || $REPLY =~ ^[Yy]$ ]]; then
        check_dependencies
        install_python_deps
        process_data
        build_backend
        setup_frontend
        start_services
    else
        echo -e "${RED}安装已取消${NC}"
        exit 0
    fi
}

# 执行主函数
main 