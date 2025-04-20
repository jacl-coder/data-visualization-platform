#!/bin/bash
# 数据分析与可视化平台 Docker 构建与部署脚本
# 版本：1.0

# 设置终端颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 获取项目根目录
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# Docker Hub用户名
DOCKER_USERNAME="jacl01"

# 镜像名称和标签
BACKEND_IMAGE_NAME="data-viz-backend"
FRONTEND_IMAGE_NAME="data-viz-frontend"
TAG=$(date +"%Y%m%d")

# 脚本模式
MODE="full" # 默认模式：构建并部署

# 解析命令行参数
while [[ $# -gt 0 ]]; do
  case $1 in
    --build-only)
      MODE="build"
      shift
      ;;
    --push)
      MODE="push"
      shift
      ;;
    --deploy-only)
      MODE="deploy"
      shift
      ;;
    --help)
      echo "用法: $0 [选项]"
      echo "选项:"
      echo "  --build-only    仅构建镜像，不启动服务"
      echo "  --push          构建镜像并推送到Docker Hub"
      echo "  --deploy-only   仅启动服务，不构建镜像"
      echo "  --help          显示此帮助信息"
      exit 0
      ;;
    *)
      echo "未知选项: $1"
      echo "使用 --help 查看帮助信息"
      exit 1
      ;;
  esac
done

# 欢迎信息
echo -e "${BLUE}=======================================================${NC}"
echo -e "${BLUE}    数据分析与可视化平台 Docker 构建与部署工具        ${NC}"
echo -e "${BLUE}=======================================================${NC}"
echo -e "${GREEN}当前模式: ${NC}"

case $MODE in
  full)
    echo -e "  全流程：构建镜像并启动服务"
    echo -e "${GREEN}该脚本将完成以下任务：${NC}"
    echo -e "  1. 检查必要的依赖"
    echo -e "  2. 处理数据并生成数据库"
    echo -e "  3. 构建后端和前端Docker镜像"
    echo -e "  4. 为镜像添加标签"
    echo -e "  5. 启动Docker Compose服务"
    ;;
  build)
    echo -e "  仅构建镜像"
    echo -e "${GREEN}该脚本将完成以下任务：${NC}"
    echo -e "  1. 检查必要的依赖"
    echo -e "  2. 处理数据并生成数据库"
    echo -e "  3. 构建后端和前端Docker镜像"
    echo -e "  4. 为镜像添加标签"
    ;;
  push)
    echo -e "  构建镜像并推送到Docker Hub"
    echo -e "${GREEN}该脚本将完成以下任务：${NC}"
    echo -e "  1. 检查必要的依赖"
    echo -e "  2. 处理数据并生成数据库"
    echo -e "  3. 构建后端和前端Docker镜像"
    echo -e "  4. 为镜像添加标签"
    echo -e "  5. 推送镜像到Docker Hub"
    ;;
  deploy)
    echo -e "  仅启动服务"
    echo -e "${GREEN}该脚本将完成以下任务：${NC}"
    echo -e "  1. 检查必要的依赖"
    echo -e "  2. 启动Docker Compose服务"
    ;;
esac

echo -e "${BLUE}=======================================================${NC}"
echo

# 检查依赖
echo -e "${BLUE}[1/5] 检查必要的依赖...${NC}"

# 检查Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}错误: Docker未安装${NC}"
    echo -e "请先安装Docker: https://docs.docker.com/get-docker/"
    exit 1
fi
echo -e "  - ${GREEN}Docker已安装√${NC}"

# 检查Docker权限
if ! docker info &> /dev/null; then
    echo -e "${YELLOW}警告: 当前用户没有Docker权限${NC}"
    echo -e "您有以下几种方式解决此问题:"
    echo -e "  1. 使用sudo运行此脚本: ${GREEN}sudo $0${NC}"
    echo -e "  2. 将当前用户添加到docker用户组 (推荐):"
    echo -e "     ${GREEN}sudo usermod -aG docker $USER${NC}"
    echo -e "     添加后需要注销并重新登录，或运行: ${GREEN}newgrp docker${NC}"
    
    read -p "是否使用sudo继续运行? (y/n): " -n 1 -r REPLY
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}使用sudo继续运行脚本...${NC}"
        # 使用sudo重新执行自身
        exec sudo "$0" "$@"
        exit $?
    else
        echo -e "${RED}退出脚本。请解决Docker权限问题后重试。${NC}"
        exit 1
    fi
fi
echo -e "  - ${GREEN}Docker权限检查通过√${NC}"

# 检查Docker Compose
if ! command -v docker-compose &> /dev/null; then
    # 检查是否有新版docker compose子命令
    if ! docker compose version &> /dev/null; then
        if [[ "$MODE" != "build" ]]; then
            echo -e "${RED}错误: Docker Compose未安装${NC}"
            echo -e "请先安装Docker Compose: https://docs.docker.com/compose/install/"
            echo -e "或使用新版Docker CLI的compose子命令: docker compose"
            exit 1
        else
            echo -e "${YELLOW}警告: Docker Compose未安装，但在仅构建模式下这不是必须的${NC}"
        fi
    else
        echo -e "  - ${GREEN}Docker Compose (新版CLI子命令) 已安装√${NC}"
        # 定义compose命令为新版格式
        COMPOSE_CMD="docker compose"
    fi
else
    echo -e "  - ${GREEN}Docker Compose (独立命令) 已安装√${NC}"
    # 定义compose命令为旧版格式
    COMPOSE_CMD="docker-compose"
fi

# 仅在需要进行数据处理和构建时执行
if [[ "$MODE" != "deploy" ]]; then
    # 检查Python (用于数据处理)
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}错误: Python 3未安装${NC}"
        echo -e "需要Python 3来处理数据"
        exit 1
    fi
    echo -e "  - ${GREEN}Python 3已安装√${NC}"

    # 处理数据
    echo -e "${BLUE}[2/5] 处理数据并生成数据库...${NC}"

    # 确保数据库目录存在
    mkdir -p database

    # 检查是否需要创建虚拟环境
    if [ ! -d "venv" ]; then
        echo -e "  - 创建Python虚拟环境..."
        python3 -m venv venv
    fi

    # 激活虚拟环境
    source venv/bin/activate

    # 安装Python依赖
    echo -e "  - 安装Python依赖..."
    pip install -r data_processing/requirements.txt

    # 处理数据
    echo -e "  - 开始处理数据..."
    python data_processing/main.py

    # 退出虚拟环境
    deactivate

    # 构建Docker镜像
    echo -e "${BLUE}[3/5] 构建Docker镜像...${NC}"

    echo -e "  - 构建后端镜像..."
    docker build -t $BACKEND_IMAGE_NAME -f Dockerfile.backend .
    if [ $? -ne 0 ]; then
        echo -e "${RED}后端Docker镜像构建失败!${NC}"
        exit 1
    fi

    echo -e "  - 构建前端镜像..."
    docker build -t $FRONTEND_IMAGE_NAME -f Dockerfile.frontend .
    if [ $? -ne 0 ]; then
        echo -e "${RED}前端Docker镜像构建失败!${NC}"
        exit 1
    fi

    echo -e "  - ${GREEN}Docker镜像构建成功√${NC}"

    # 添加标签
    echo -e "${BLUE}[4/5] 为镜像添加标签...${NC}"

    # 为本地镜像添加标签
    docker tag $BACKEND_IMAGE_NAME:latest $BACKEND_IMAGE_NAME:$TAG
    docker tag $FRONTEND_IMAGE_NAME:latest $FRONTEND_IMAGE_NAME:$TAG

    echo -e "  - ${GREEN}已为镜像添加标签: $TAG${NC}"

    # 如果是push模式，推送到Docker Hub
    if [[ "$MODE" == "push" ]]; then
        echo -e "${BLUE}[5/5] 推送镜像到Docker Hub...${NC}"
        
        # 登录Docker Hub
        echo -e "  - 登录Docker Hub..."
        docker login
        if [ $? -ne 0 ]; then
            echo -e "${RED}Docker Hub登录失败，跳过推送步骤${NC}"
            exit 1
        fi
        
        # 为Docker Hub添加标签
        docker tag $BACKEND_IMAGE_NAME:latest $DOCKER_USERNAME/$BACKEND_IMAGE_NAME:latest
        docker tag $BACKEND_IMAGE_NAME:$TAG $DOCKER_USERNAME/$BACKEND_IMAGE_NAME:$TAG
        docker tag $FRONTEND_IMAGE_NAME:latest $DOCKER_USERNAME/$FRONTEND_IMAGE_NAME:latest
        docker tag $FRONTEND_IMAGE_NAME:$TAG $DOCKER_USERNAME/$FRONTEND_IMAGE_NAME:$TAG

        # 推送镜像
        echo -e "  - 推送后端镜像..."
        docker push $DOCKER_USERNAME/$BACKEND_IMAGE_NAME:latest
        docker push $DOCKER_USERNAME/$BACKEND_IMAGE_NAME:$TAG

        echo -e "  - 推送前端镜像..."
        docker push $DOCKER_USERNAME/$FRONTEND_IMAGE_NAME:latest
        docker push $DOCKER_USERNAME/$FRONTEND_IMAGE_NAME:$TAG

        echo -e "  - ${GREEN}镜像已成功推送到Docker Hub√${NC}"
        echo -e "    后端: ${BLUE}$DOCKER_USERNAME/$BACKEND_IMAGE_NAME:latest${NC}"
        echo -e "    前端: ${BLUE}$DOCKER_USERNAME/$FRONTEND_IMAGE_NAME:latest${NC}"
    fi
fi

# 如果是full或deploy模式，启动服务
if [[ "$MODE" == "full" || "$MODE" == "deploy" ]]; then
    echo -e "${BLUE}[5/5] 启动服务...${NC}"
    $COMPOSE_CMD up -d
    if [ $? -ne 0 ]; then
        echo -e "${RED}服务启动失败!${NC}"
        exit 1
    fi

    echo -e "${GREEN}数据可视化平台Docker容器已成功启动!${NC}"
    echo -e "您可以通过以下地址访问：${BLUE}http://localhost:40000${NC}"
    echo
    echo -e "其他常用命令:"
    echo -e "  - 查看日志: ${YELLOW}$COMPOSE_CMD logs -f${NC}"
    echo -e "  - 停止服务: ${YELLOW}$COMPOSE_CMD down${NC}"
    echo -e "  - 重启服务: ${YELLOW}$COMPOSE_CMD restart${NC}"
fi

# 如果是build或push模式，显示构建的镜像
if [[ "$MODE" == "build" || "$MODE" == "push" ]]; then
    echo -e "${BLUE}构建的镜像:${NC}"
    docker images | grep -E "$BACKEND_IMAGE_NAME|$FRONTEND_IMAGE_NAME"
    
    echo -e "${GREEN}数据可视化平台Docker镜像构建完成!${NC}"
    echo -e "您可以通过以下命令启动服务:"
    echo -e "  ${BLUE}$COMPOSE_CMD up -d${NC}"
    echo -e "然后通过 ${BLUE}http://localhost:40000${NC} 访问应用"
fi

echo -e "${BLUE}=======================================================${NC}"
exit 0 