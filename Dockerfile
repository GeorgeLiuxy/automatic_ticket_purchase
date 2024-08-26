FROM ubuntu:latest
LABEL authors="george"

ENTRYPOINT ["top", "-b"]

# 使用官方的Python镜像作为基础镜像
FROM python:3.9.6

# 设置工作目录
WORKDIR /app

# 复制依赖文件到容器中
COPY requirements.txt .

# 安装依赖项
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件到容器中
COPY . .

# 指定启动命令
CMD ["python", "toolsUI.py"]
