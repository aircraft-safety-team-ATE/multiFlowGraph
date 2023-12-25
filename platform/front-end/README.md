# 基于LogicFlow的多信号流图绘制工具

基于 [LogicFlow](https://github.com/didi/LogicFlow) 开发的多信号流图绘制工具

## 使用

> 面向纯小白的使用教学，按需跳过

### Node.js

首先要有 [Node.js](https://nodejs.org/en/download) 环境，LTS 版本即可，安装可以参考[菜鸟教程](https://www.runoob.com/nodejs/nodejs-install-setup.html)

> Node.js 的版本太低可能会出问题

> [Node.js 历史版本下载地址](https://nodejs.org/dist/)

> 参考：绘使用的版本是 16.13.0

查看 Node.js 的版本：

```bash
node --version
```

### npm

NPM 是随同 Node.js 一起安装的包管理工具，能解决 Node.js 代码部署上的很多问题

查看 npm 版本：

```bash
npm -v
```

确定有 npm 后，在当前项目文件夹目录下（确保能看到 **package.json**）按需运行以下代码：

- 依赖安装，**必做！**

``` bash
npm install
```

执行完本命令后文件夹下会多一个名为 **node_modules** 的文件夹，里面有该项目的所有依赖

- 在[本机的 8080 端口](http://localhost:8080/)运行本平台

``` bash
npm run dev
```

测试与演示使用这个命令就足够了

- 生成用于生产环境的小规模文件（一般用不到）

``` bash
npm run build
```

> 生成的文件位于 **dict** 文件夹中

> 以上指令生产的文件是用于服务器端的，直接以文件形式打开是无效的（但是把 index.html 中的绝对地址全改成相对地址后其实是可以本地打开的）

## 配置

### 流图编辑配置

在 `src/components/logicflowConfig/common/commonConfig.js` 中按提示进行修改即可

### 节点初始化配置

在 `src/components/logicflowConfig/init.js` 中可以自定义节点的初始化属性，初始化属性仅影响在拖拽绘图时生成的节点的样式和节点内部的一些自定义属性的初始值

```js
{
  type: 'fault-node',
  text: '故障',
  properties: {
  	// common
  	showType: 'edit',
  	collision : false,
  	detectable: true,
  	fuzzible: false,
  	fuzzy_state: 0,
  	state: 0,
  	icon: require("@/assets/images/delay.svg"),
  	typeColor: '#edc3ae'
  	// special
  	flevel: 0
  }
}
```

上述例子定义了测试节点（test-node）的初始化属性，绝大多数属性都不需要修改，仅部分需要修改：

- `type` : 初始化节点的类型（该节点需要注册）
- `text` : 节点初始化时的文本
- `properties.icon` : 节点的 icon，额外的 icon 可以添加至 `src/assets/images` 文件夹中
- `properties.typeColor` : 节点的颜色
- 对于不同的节点， `properties` 中可能存在一些特定的属性，这部分属性需要根据使用需求自行设置初始值

❗ 自定义属性只能添加在 `properties` 中

### 自定义菜单栏

在 `src/components/logicflowConfig/tools/menu.js` 可以修改已有的菜单栏，包括各类节点与连线的右键菜单栏，以及侧边栏和按钮组

按钮组如有需要新增按钮请自行在 `src/components/MSFGcomponents/Control.vue` 中添加按钮以及相关的回调函数

### 添加事件监听器

在 `src/components/logicflowConfig/tools/listeners.js` 可以添加或删除事件监听器

添加事件监听参考 [LogicFlow-事件](http://logic-flow.org/guide/basic/event.html)

LogicFlow 提供的事件参考 [LogicFlow-eventCenterApi](http://logic-flow.org/api/eventCenterApi.html)

事件监听器也可以监听基于 LogicFlow eventCenter 抛出的自定义事件，如何抛出自定义事件参考 [LogicFlow-事件中心](http://logic-flow.org/guide/basic/event.html#%E8%87%AA%E5%AE%9A%E4%B9%89%E4%BA%8B%E4%BB%B6)

### 已有节点添加可编辑新属性

1. 在 `src/components/logicflowConfig/init.js` 中为对应的节点添加额外的自定义属性，并赋初值

❗ 自定义属性只能添加在 `properties` 中

2. 在 `src/components/MSFGcomponents/EditDialog.vue` 中为对应的节点添加额外的表单元素

### 后端接口

该组件使用 axios 与后端进行通讯，默认地址为 'http://127.0.0.1:8000/'，需要自行使用 Django、Flask 等框架搭建后端以实现前后端交互

> 前后端通讯过程中可能会有跨域问题，请自行解决，推荐使用 `F12` 打开 DevTool 中的控制台进行调试

在 `src/utils/setaxios.js` 中可以自定义 axios 的各项默认值

## 绘图数据格式

详细绘图数据格式可以参考 `public/data-demo.json`

一个非子系统的节点的数据格式如下：

```ts
type Node = {
  text: string, 				// 节点名称
  type: string, 				// 已注册的节点类型
  showConfig: {
  	position: { 				// 节点的位置参数
  	  x: number,
  	  y: number
  	},
  	properties: {
	  showType: "edit", 		// ※无需修改
	  collision: boolean,		// 是否闭环
	  detectable: boolean,		// 是否可测
	  fuzzible: boolean,		// 是否为模糊节点
	  fuzzy_state: number, 		// 模糊分数
	  state: number, 			// 故障分数
	  icon: string, 			// 使用的图标
	  typeColor: string , 		// 节点的背景颜色，HEX 或 RGB 都行
	  width: number, 			// 节点宽度，※无需修改
	  ui: "node-red", 			// ※无需修改
	  [prop: string]: any, 		// 自定义属性
  	}
  }
};
```

> 以上格式说明用了 TS 的类型声明，虽然实际项目没有用 TS

不同类型的节点可能存在一些独特的自定义属性

对于子系统节点，存在一些特殊的属性：

```ts
type SubSystem = {
  text: "子系统",
  type: "sub-system",
  showConfig: {
  	position: { 				// 节点的位置参数
  	  x: number,
  	  y: number
  	},
  	properties: {
  	  showType: "edit", 		// ※无需修改
	  collision: boolean,		// 是否闭环
	  detectable: boolean,		// 是否可测
	  fuzzible: boolean,		// 是否为模糊节点
	  fuzzy_state: number, 		// 模糊分数
	  state: number, 			// 故障分数
	  width: number, 			// 节点宽度，※无需修改
  	  nodeSize: { 				// 子系统大小
  		width: number,
  		height: number
  	  },
  	  isFold: boolean, 			// 折叠 & 展开，加载时的默认状态
	  [prop: string]: any, 		// 自定义属性
  	}
  },
  children: string[] 			// 子节点的名称
}
```

> 以上格式说明用了 TS 的类型声明，虽然实际项目没有用 TS

## 拓展

### 节点

增加新的自定义节点只需在 `src/components/logicflowConfig/node` 文件夹中添加新的节点自定义 js 文件即可

节点自定义 js 文件可以参考 `src/components/logicflowConfig/node/BaseNode.js` ，也可以直接继承已有的节点或[LogicFlow的基础节点](http://logic-flow.org/guide/basic/node.html)做细节修改

具体自定义方式参考：[nodeModelApi](http://logic-flow.org/api/nodeModelApi.html)

```js
import BaseNode from './BaseNode'

class 节点模型类 extends BaseNode.model {
	// 在此做细节自定义
}
class 节点视图类 extends BaseNode.view {
	// 在此做细节自定义
}

export default {
  type: '自定义节点名',
  model: 节点模型类,
  view: 节点视图类
}
```

### 子系统/分组

子系统一般应该不需要定义多个，有需要的话参考 `src/components/logicflowConfig/group/SubSystem.js`

新增自定义子系统方式同节点

### 连线/边

连线样式自定义参考 `src/components/logicflowConfig/edge/CustomEdge.js`

新增自定义连线样式方式同节点

### 修改默认的导入导出方式

如果数据结构变动比较大，可能会需要修改绘图数据导入与导出的函数，这时候可以修改或重写 `src/components/logicflowConfig/common/methods.js` 中的 `importStruct` 与 `exportStruct` 函数

## 开发日志

### 代办
- [ ] 支持子系统的复制和粘贴功能 也是大坑
- [ ] 支持子系统封装与解锁(有点难度，但是非常必要) 重点在于解开子系统时，子系统内部的组件在父系统中如何摆放 输入与输出模块的重排等等 是个大坑woc
- [ ] 在root系统创建输入输出模块时，会提示警告信息，且不会创建输入输出模块
- [ ] 

### 2023.1.21
“基本重构完了 但是还差多层次建模 感觉这块工作量也会非常的大（感觉也很有挑战性），本来打算把这部分也弄了，不过最近几天我必须得去先做标书了😂，标书初五ddl，比较急 我还一个字没写 哈人，写完标书 我再回来接着弄吧”

### 2023.02.08 绘
基本重构完毕，整体上应该能满足多信号流图的设计需求，细节部分等需求更新再补充，可能存在少部分没有注意到的bug，，，有了请戳我修

### 2023.02.10 绘
- 新增导入数据时的自动布局（触发条件是存在没有定位的节点） 浛哥写的，绘整合测试 & 微调
- 新增算法节点
- 根据浛哥的需求增加了故障节点的故障等级选择与算法节点的算法选择
- 删除测试节点的输出端（测试节点只能流入，不能流出）
- 修复在子系统嵌套时，解除内部子系统后，子系统内节点不会自动加入上一级子系统的 bug

### 2023.02.13 绘
- 新增绘图检查与指标分析，这两项功能与后端有交互
    - 根据绘图检查与指标分析的结果，所有节点的颜色会发生相应的变化
    - 想要取消检查或分析改变节点颜色的效果，可以点击重绘还原绘图

### 2023.02.18 绘
- 新特性：在分析后，鼠标悬停在节点上时会显示分析结果（节点名&故障分数&模糊分数）
- 整体代码重构，提高项目的易用性和可移植性
- 撰写 README.md 文档，为后续基于该平台进行个性化提供指导

### 2023.03.21 绘
- 更新 README 文档

### 2023.03.26 绘
- 新增 Dockerfile 文件支持创建 Docker 镜像
- 修复了一个由于大小写不一致可能引发的 bug
	- 后续如果遇到组件加载出错大概率还是这个问题

### 2023.12.23 冯
- 新增子系统建模功能 基本已经实现
- 待完善
	- 在根系统中，加入输入和输出模块后，存在找不到父系统的问题(应该采用什么逻辑去解决呢？)
	- 无法框选一堆组件然后构建子系统，
	- 子系统模块有点丑陋
	- 面对新的数据结构需要重新编写导出流图 载入流图的逻辑，以及后端生成D矩阵的逻辑
	- 代码很丑陋 待重构

子系统建模实现逻辑
维护一个G_DATA的全局变量，currentSystemId表示当前所在的系统，SystemData表示系统的数据，每个系统的数据结构如下，非嵌套式，data中的数据就是this.lf.getGraphData()的数据，
```js
    this.G_DATA = {
      currentSystemId: 1,
      SystemData:[
      {
        system_id:1,
      name:"root",
      parent_id:null,
      data:{},
	  }
	  {
        system_id:2,
      name:"sub2",
      parent_id:1,
      data:{},
	  },
],
	}
```