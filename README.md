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

## 多信号流图通用测试流程

### 单故障单测试 

测试文件：platform\test_data\多信号流图\test1.json

![image-20240108035321442](https://buaa007.oss-cn-beijing.aliyuncs.com/imagesimage-20240108035321442.png)

**ground Truth**

|       | 测试1 |
| ----- | ----- |
| 故障1 | 1     |

**2024.1.8测试结果**

![image-20240108035813355](https://buaa007.oss-cn-beijing.aliyuncs.com/imagesimage-20240108035813355.png)

### 多故障单测试

测试文件：platform\test_data\多信号流图\test2.json

![image-20240108035844269](https://buaa007.oss-cn-beijing.aliyuncs.com/imagesimage-20240108035844269.png)

**ground Truth**

|       | 测试1 |
| ----- | ----- |
| 故障1 | 1     |
| 故障2 | 1     |

**2024.1.8测试结果**

![image-20240108035959043](https://buaa007.oss-cn-beijing.aliyuncs.com/imagesimage-20240108035959043.png)

### 单故障多测试
测试文件：platform\test_data\多信号流图\test3.json

![image-20240108040107839](https://buaa007.oss-cn-beijing.aliyuncs.com/imagesimage-20240108040107839.png)

**ground Truth**

|       | 测试1 | 测试2 |
| ----- | ----- | ----- |
| 故障1 | 1     | 1     |

**2024.1.8测试结果**

![image-20240108040215398](https://buaa007.oss-cn-beijing.aliyuncs.com/imagesimage-20240108040215398.png)

### 故障转递1
测试文件：platform\test_data\多信号流图\test4.json

![image-20240108040254319](https://buaa007.oss-cn-beijing.aliyuncs.com/imagesimage-20240108040254319.png)

**ground Truth**

|       | 测试1 |
| ----- | ----- |
| 故障1 | 1     |
| 故障2 | 1     |

**2024.1.8测试结果**

![image-20240108040312004](https://buaa007.oss-cn-beijing.aliyuncs.com/imagesimage-20240108040312004.png)

### 故障传递2
测试文件：platform\test_data\多信号流图\test5.json

![image-20240108040447024](https://buaa007.oss-cn-beijing.aliyuncs.com/imagesimage-20240108040447024.png)

**ground Truth**

|       | 测试1 |
| ----- | ----- |
| 故障1 | 1     |
| 故障2 | 1     |
| 故障3 | 1     |
| 故障4 | 1     |

**2024.1.8测试结果**

![image-20240108040529059](https://buaa007.oss-cn-beijing.aliyuncs.com/imagesimage-20240108040529059.png)

### 故障传递1+多故障单测试
测试文件：platform\test_data\多信号流图\test6.json

![image-20240108040812329](https://buaa007.oss-cn-beijing.aliyuncs.com/imagesimage-20240108040812329.png)

**ground Truth**

|       | 测试1 |
| ----- | ----- |
| 故障1 | 1     |
| 故障2 | 1     |
| 故障3 | 1     |
| 故障4 | 1     |
| 故障5 | 1     |

**2024.1.8测试结果**

![image-20240108040850922](https://buaa007.oss-cn-beijing.aliyuncs.com/imagesimage-20240108040850922.png)

### 故障传递1+多故障单测试 融合 故障传递1
测试文件：platform\test_data\多信号流图\test7.json

![image-20240108041332857](https://buaa007.oss-cn-beijing.aliyuncs.com/imagesimage-20240108041332857.png)

**ground Truth**

|       | 测试1 |      |
| ----- | ----- | ---- |
| 故障1 | 1     | 0    |
| 故障2 | 1     | 0    |
| 故障3 | 1     | 0    |
| 故障4 | 0     | 1    |
| 故障5 | 0     | 1    |

**2024.1.8测试结果**

![image-20240108041440104](https://buaa007.oss-cn-beijing.aliyuncs.com/imagesimage-20240108041440104.png)

### 多根树1
测试文件：platform\test_data\多信号流图\test8.json

![image-20240108042621261](https://buaa007.oss-cn-beijing.aliyuncs.com/imagesimage-20240108042621261.png)

注意 静态图片可能无法表示出这种关系 导致误解 实际连线是从故障4 连接到 测试1  前端渲染 线会有动态效果可以避免这种误解

**ground Truth**

|       | 测试1 | 测试2 |
| ----- | ----- | ----- |
| 故障1 | 1     | 0     |
| 故障2 | 1     | 0     |
| 故障3 | 1     | 0     |
| 故障4 | 1     | 1     |
| 故障5 | 1     | 1     |
| 故障6 | 1     | 1     |

**2024.1.8测试结果**

![image-20240108042826209](https://buaa007.oss-cn-beijing.aliyuncs.com/imagesimage-20240108042826209.png)

### 多根树2
测试文件：platform\test_data\多信号流图\test9.json

![image-20240108043023238](https://buaa007.oss-cn-beijing.aliyuncs.com/imagesimage-20240108043023238.png)

注意 静态图片可能无法表示出这种关系 导致误解 实际连线是从故障5 连接到 测试1  前端渲染 线会有动态效果可以避免这种误解

**ground Truth**

|       | 测试1 | 测试2 |
| ----- | ----- | ----- |
| 故障1 | 1     | 0     |
| 故障2 | 1     | 0     |
| 故障3 | 1     | 0     |
| 故障4 | 1     | 0     |
| 故障5 | 1     | 1     |
| 故障6 | 1     | 1     |

**2024.1.8测试结果**

![image-20240108043120710](https://buaa007.oss-cn-beijing.aliyuncs.com/imagesimage-20240108043120710.png)

### 多根树3
测试文件：platform\test_data\多信号流图\test10.json

![image-20240108045038008](https://buaa007.oss-cn-beijing.aliyuncs.com/imagesimage-20240108045038008.png)



**ground Truth**

|       | 测试1 | 测试2 |
| ----- | ----- | ----- |
| 故障1 | 1     | 1     |
| 故障2 | 1     | 1     |
| 故障3 | 1     | 1     |
| 故障4 | 1     | 1     |

**2024.1.8测试结果**

![image-20240108045137920](https://buaa007.oss-cn-beijing.aliyuncs.com/imagesimage-20240108045137920.png)

### 子系统——简单连线
测试文件：platform\test_data\多信号流图\test_subsystem1.json

![image-20240108045652785](https://buaa007.oss-cn-beijing.aliyuncs.com/imagesimage-20240108045652785.png)

![image-20240108045724430](https://buaa007.oss-cn-beijing.aliyuncs.com/imagesimage-20240108045724430.png)



**ground Truth**

|       | 测试1 |
| ----- | ----- |
| 故障1 | 1     |
| 输入1 | 1     |
| 输出1 | 1     |

**2024.1.8测试结果**

![image-20240108045742524](https://buaa007.oss-cn-beijing.aliyuncs.com/imagesimage-20240108045742524.png)

### 子系统——深度子系统
测试文件：platform\test_data\多信号流图\test_subsystem2.json

![image-20240108050230884](https://buaa007.oss-cn-beijing.aliyuncs.com/imagesimage-20240108050230884.png)

![image-20240108050239189](https://buaa007.oss-cn-beijing.aliyuncs.com/imagesimage-20240108050239189.png)

![image-20240108050246105](https://buaa007.oss-cn-beijing.aliyuncs.com/imagesimage-20240108050246105.png)

![image-20240108050253338](https://buaa007.oss-cn-beijing.aliyuncs.com/imagesimage-20240108050253338.png)



**ground Truth**

|       | 测试1 |
| ----- | ----- |
| 故障1 | 1     |
| 输出1 | 1     |
| 输入1 | 1     |
| 输入1 | 1     |
| 输出1 | 1     |
| 输入1 | 1     |
| 输出1 | 1     |

**2024.1.8测试结果**

![image-20240108050452565](https://buaa007.oss-cn-beijing.aliyuncs.com/imagesimage-20240108050452565.png)

### 子系统——多输入多输出
测试文件：platform\test_data\多信号流图\test_subsystem3.json

![image-20240108051015656](https://buaa007.oss-cn-beijing.aliyuncs.com/imagesimage-20240108051015656.png)

![image-20240108051027873](https://buaa007.oss-cn-beijing.aliyuncs.com/imagesimage-20240108051027873.png)



**ground Truth**

|                | 测试1 | 测试2 |
| -------------- | ----- | ----- |
| 故障1          | 1     | 0     |
| 输出1          | 1     | 0     |
| 输入1          | 1     | 0     |
| 输入2          | 0     | 1     |
| 输出2          | 0     | 1     |
| 子系统2：故障1 | 1     | 0     |
| 故障2          | 0     | 1     |

**2024.1.8测试结果**

![image-20240108051044196](https://buaa007.oss-cn-beijing.aliyuncs.com/imagesimage-20240108051044196.png)

### 子系统——子系统中的测点
测试文件：platform\test_data\多信号流图\test_subsystem4.json

![image-20240108051015656](https://buaa007.oss-cn-beijing.aliyuncs.com/imagesimagesimage-20240108051015656.png)

![image-20240108051558282](https://buaa007.oss-cn-beijing.aliyuncs.com/imagesimage-20240108051558282.png)

**ground Truth**

|                | 测试1 | 子系统2：测试1 | 测试2 |
| -------------- | ----- | -------------- | ----- |
| 故障1          | 1     | 1              | 0     |
| 输出1          | 1     | 0              | 0     |
| 输入1          | 1     | 1              | 0     |
| 输入2          | 0     | 0              | 1     |
| 输出2          | 0     | 0              | 1     |
| 子系统2：故障1 | 1     | 1              | 0     |
| 故障2          | 0     | 0              | 1     |

**2024.1.8测试结果**

![image-20240108051638152](https://buaa007.oss-cn-beijing.aliyuncs.com/imagesimage-20240108051638152.png)

### 子系统——多并列系统
测试文件：platform\test_data\多信号流图\test10.json

![image-20240108051952552](https://buaa007.oss-cn-beijing.aliyuncs.com/imagesimage-20240108051952552.png)

![image-20240108051558282](https://buaa007.oss-cn-beijing.aliyuncs.com/imagesimagesimage-20240108051558282.png)

![image-20240108051931724](https://buaa007.oss-cn-beijing.aliyuncs.com/imagesimage-20240108051931724.png)



**ground Truth**

|                | 测试1 | 子系统2：测试1 | 测试2 |
| -------------- | ----- | -------------- | ----- |
| 故障1          | 1     | 1              | 0     |
| 输出1          | 1     | 0              | 0     |
| 输入1          | 1     | 1              | 0     |
| 输入2          | 0     | 0              | 1     |
| 输出2          | 0     | 0              | 1     |
| 子系统2：故障1 | 1     | 1              | 0     |
| 故障2          | 0     | 0              | 1     |
| 输入1          | 0     | 0              | 1     |
| 输出1          | 0     | 0              | 1     |

**2024.1.8测试结果**

![image-20240108052044935](https://buaa007.oss-cn-beijing.aliyuncs.com/imagesimage-20240108052044935.png)
