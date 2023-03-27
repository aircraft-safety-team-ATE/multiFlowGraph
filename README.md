# 多信号流图

#### 介绍
多信号流图后端核心代码

#### 运行环境(Python3.8)
1. Flask==2.1.2
2. Jinja2==3.1.2
3. openpyxl==3.0.10
4. pandas==1.4.2

#### 安装教程
* 双击run.bat，即可启动；
* 通过127.0.0.1:8080进行访问；
* 算法脚本请集成“lib\detectAlgo\support\BaseAlgoClass.py”基类进行封装，放入“lib\detectAlgo”文件夹下即可

#### 开发日志
2023.03.21  基本完成后端核心代码，部分功能端口（测点优化、读取FMECA、算法接入）未完全开放
2023.03.27  前后端合并（测点优化、读取FMECA已开放），node_modules未放入，请从老版本中载入下载

