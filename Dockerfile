# 假设在 Dockerfile 中指定了平台
FROM python:3.9-slim


# 设置工作目录
WORKDIR /app

# 复制依赖文件到容器中
COPY requirements.txt .

# 升级 pip
RUN pip install --upgrade pip

# 安装 Python 依赖项
RUN pip install --no-cache-dir -r requirements.txt

# 单独安装 PyQt5
RUN pip install PyQt5==5.15.2

# 复制项目文件到容器中
COPY . .

# 启动命令
CMD ["python", "toolsUI.py"]
