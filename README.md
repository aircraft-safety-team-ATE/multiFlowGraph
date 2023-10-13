# 多信号流图

#### 介绍
多信号流图后端核心代码


#### 安装教程
* 双击run.bat，即可启动；
* 通过127.0.0.1:8080进行访问；
* 算法脚本请集成“lib\detectAlgo\support\BaseAlgoClass.py”基类进行封装，放入“lib\detectAlgo”文件夹下即可

#### 快速开始
运行前端

参考front-end文件夹下的README.md

运行后端

python 3.8通过测试

requirements.txt中包含了所有需要的包，可以通过以下命令安装
```
cd back-end
pip install -r requirements.txt
```
运行后端
```
cd back-end
python manage.py
```

#### 开发日志
2023.03.21  基本完成后端核心代码，部分功能端口（测点优化、读取FMECA、算法接入）未完全开放

2023.03.27  前后端合并（测点优化、读取FMECA已开放），node_modules未放入，请从老版本中载入下载

2023.10.13  跟新最新的多信号流图前端代码 并通过运行测试 不过测点优化似乎有点问题
