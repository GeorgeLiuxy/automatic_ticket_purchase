
## 准备工作
### 1. 配置环境
安装所需要的环境
1.1 安装 Python 3.9
你可以使用 Homebrew 来安装 Python 3.9。
```shell
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install python@3.9.2
```

如果还没有安装 Homebrew，可以通过以下命令安装：
```shell
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
安装完 Homebrew 后，使用以下命令安装 Python 3.9：
```shell
brew install python@3.9
```
安装完成后，你可以检查 Python 3.9 是否安装成功：
```shell
python3.9 --version
```
1.2 创建虚拟环境
   首先，选择一个你希望创建虚拟环境的目录，并导航到该目录。例如：
```shell
mkdir ~/myproject
cd ~/myproject
```
接下来，使用 python3.9 创建虚拟环境：
```shell
python3.9 -m venv venv
```
这将在 myproject 目录下创建一个名为 venv 的虚拟环境目录。

1.3 激活虚拟环境
   要激活刚创建的虚拟环境，运行以下命令：
```shell
source venv/bin/activate
```
激活后，你的终端提示符会变为 (venv)，表示你已经在虚拟环境中。

1.4 使用虚拟环境
   在虚拟环境中，你可以使用 pip 来安装所需的 Python 包。例如：
```shell
pip install -r requirements.txt
```
安装包后，它们会被安装在虚拟环境的 venv 目录中，而不会影响系统的全局 Python 环境。

### 2. 配置ChromeDriver
需要下载与系统安装对应的ChromeDriver驱动并配置(也可以改用其他浏览器驱动)，
下载地址: http://chromedriver.storage.googleapis.com/index.html
驱动地址放到本地路径下：/Volumes/software/chromedriver-mac-arm64/chromedriver
授权驱动执行权限

```shell
chmod +x /Volumes/software/chromedriver-mac-arm64/chromedriver

```

### 3. 运行脚本
```shell
python toolsUI.py
```

### 4. 运行脚本
   当你完成开发任务后，可以通过以下命令退出虚拟环境：
```shell
deactivate
```
这将返回到系统的全局 Python 环境。
