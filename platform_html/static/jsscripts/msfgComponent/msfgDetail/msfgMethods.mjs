// import lf & plugins
//import LogicFlow from './@logicflow/core'
//import './@logicflow/core/dist/style/index.css'
//import { Menu, Group, DndPanel, Snapshot, SelectionSelect } from './@logicflow/extension'

// import commonConfig
import { editConfig, keyboardConfig, gridConfig, extraConfig } from './common/commonConfig.mjs'

// import nodes
//const nodeModulesFiles = require.context('./node', true, /.js$/)
let registerNodeList = []
/**nodeModulesFiles.keys().forEach((modulePath) => {
  registerNodeList.push(nodeModulesFiles(modulePath))
})**/
import BaseNodeModelConfig from './node/BaseNode.mjs'
registerNodeList.push(BaseNodeModelConfig)
import FaultNodeModelConfig from './node/FaultNode.mjs'
registerNodeList.push(FaultNodeModelConfig)
import SwitchNodeModelConfig from './node/SwitchNode.mjs'
registerNodeList.push(SwitchNodeModelConfig)
import TestNodeModelConfig from './node/TestNode.mjs'
registerNodeList.push(TestNodeModelConfig)
import InputNodeModelConfig from './node/InputNode.mjs'
registerNodeList.push(InputNodeModelConfig)
import OutputNodeModelConfig from './node/OutputNode.mjs'
registerNodeList.push(OutputNodeModelConfig)
import SubSystemNodeModelConfig from './node/SubsystemNode.mjs'
registerNodeList.push(SubSystemNodeModelConfig)

// import group
//const groupModulesFiles = require.context('./group', true, /.js$/)
let registerGroupList = []
/**groupModulesFiles.keys().forEach((modulePath) => {
  registerGroupList.push(groupModulesFiles(modulePath))
})**/
import SubSystemConfig from './group/SubSystem.mjs'
registerGroupList.push(SubSystemConfig)

// import edge
//const edgeModulesFiles = require.context('./edge', true, /.js$/)
let registerEdgeList = []
/**edgeModulesFiles.keys().forEach((modulePath) => {
  registerEdgeList.push(edgeModulesFiles(modulePath))
})**/
import CustomEdgeConfig from './edge/CustomEdge.mjs'
registerEdgeList.push(CustomEdgeConfig)

import { utils } from './tools/util.mjs'
import { listeners } from './tools/listeners.mjs'
import { menu } from './tools/menu.mjs'

const msfgMethods = {
  // 初始化 LogicFlow
  $_initLf() {
    // 画布配置
    const lf = new LogicFlow({
      container: this.$refs.container,
      // 页面编辑状态选项
      ...editConfig,
      // 自定义键盘快捷键
      keyboard: keyboardConfig,
      // 网格
      grid: gridConfig.enabled ? gridConfig : false,
      // 插件
      plugins: [
        Menu,
        Group,
        Snapshot,
        DndPanel,
        SelectionSelect
      ]
    })
    this.gData = {
      currentSystemId: 1,
      SystemData: [
        {
          system_id: 1,
          name: "root",
          parent_id: null,
          data: {}
        },
      ]
    },
      this.lf = lf
    this.lf.extension.selectionSelect.setSelectionSense(extraConfig.SelectionSense.isWholeEdge, extraConfig.SelectionSense.isWholeNode)
    this.$_registerNode()
  },
  // 注册节点
  $_registerNode() {
    // node register
    registerNodeList.forEach((node) => {
      this.lf.register(node)//.default)
    })
    // group register
    registerGroupList.forEach((group) => {
      this.lf.register(group)//.default)
    })
    // edge register
    registerEdgeList.forEach((edge) => {
      this.lf.register(edge)//.default)
    })

    this.lf.setDefaultEdgeType(extraConfig.defaultEdgeType)
    this.$_render()
  },
  ...menu,
  ...listeners,
  ...utils
}

const common = {
  showType: 'edit',
  collision: false,
  detectable: true,
  fuzzible: false,
  fuzzy_state: 0,
  state: 0
}

const nodePanelList = [{
  type: 'test-node',
  text: '测试',
  properties: {
    // common
    ...common,
    icon: "/static/images/test.png",
    typeColor: '#eea2a4',
    // special
  }
},
{
  type: 'fault-node',
  text: '故障',
  properties: {
    // common
    ...common,
    icon: "/static/images/fault.png",
    typeColor: '#edc3ae',
    // special
    flevel: 0, //故障等级
  }
},
{
  type: 'switch-node',
  text: '开关',
  properties: {
    // common
    ...common,
    icon: "/static/images/switch.png",
    typeColor: '#96c24e',
    // special
    normalState: true, // true | false 开关常态（常开|常闭）
    control: null, // 控制节点
  }
},
{
  type: "subsystem-node",
  text: "子系统",
  properties: {
    // common
    ...common,
    icon: "/static/images/fault.png",
    typeColor: '#85C1E9',

    tableName: "子系统",
    fields: {
      input: 0,
      output: 0
    }

  }
},
{
  type: "input-node",
  text: "输入",
  properties: {
    // common
    ...common,
    icon: "/static/images/input.png",
    typeColor: '#85C1E9',
    // special
    index: 1, // 输入序号

  }
}, {
  type: "output-node",
  text: "输出",
  properties: {
    // common
    ...common,
    icon: "/static/images/output.png",
    typeColor: '#85C1E9',
    // special
    index: 1,
  }
}
]

/**
 * 子系统初始化
 */
const subsystemInit = {
  type: "sub-system",
  text: '子系统',
  properties: {
    ...common
  }
}

export { msfgMethods, nodePanelList, subsystemInit }