// import lf & plugins
import LogicFlow from '@logicflow/core'
import '@logicflow/core/dist/style/index.css'
import { Menu, Group, DndPanel, Snapshot, SelectionSelect } from '@logicflow/extension'

// import commonConfig
import { editConfig, keyboardConfig, gridConfig, extraConfig } from './common/commonConfig.js'

// import nodes
const nodeModulesFiles = require.context('./node', true, /.js$/)
let registerNodeList = []
nodeModulesFiles.keys().forEach((modulePath) => {
  registerNodeList.push(nodeModulesFiles(modulePath))
})

// import group
const groupModulesFiles = require.context('./group', true, /.js$/)
let registerGroupList = []
groupModulesFiles.keys().forEach((modulePath) => {
  registerGroupList.push(groupModulesFiles(modulePath))
})

// import edge
const edgeModulesFiles = require.context('./edge', true, /.js$/)
let registerEdgeList = []
edgeModulesFiles.keys().forEach((modulePath) => {
  registerEdgeList.push(edgeModulesFiles(modulePath))
})

import { listeners } from './tools/listeners.js'
import { menu } from './tools/menu.js'

const methods = {
  // 初始化 LogicFlow
  $_initLf () {
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
    this.G_DATA = {
      currentSystemId: 1,
      SystemData:[
      {
        system_id:1,
      name:"root",
      parent_id:null,
      data:{}},
],
  },
    this.lf = lf
    this.lf.extension.selectionSelect.setSelectionSense(extraConfig.SelectionSense.isWholeEdge, extraConfig.SelectionSense.isWholeNode)
    this.$_registerNode()
  },
  // 注册节点
  $_registerNode () {
    // node register
    registerNodeList.forEach((node) => {
      this.lf.register(node.default)
    })
    // group register
    registerGroupList.forEach((group) => {
      this.lf.register(group.default)
    })
    // edge register
    registerEdgeList.forEach((edge) => {
      this.lf.register(edge.default)
    })

    this.lf.setDefaultEdgeType(extraConfig.defaultEdgeType)
    this.$_render()
  },
  ...menu,
  ...listeners,
}

export { methods }