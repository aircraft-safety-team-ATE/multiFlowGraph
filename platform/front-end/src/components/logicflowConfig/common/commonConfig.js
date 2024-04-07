/**
 * 页面编辑状态选项 参考 http://logic-flow.org/api/editConfigModelApi.html
 */
const editConfig = {
  // 是否为静默模式
  isSilentMode: false, // option value: true | false

  // 禁止缩放画布
  stopZoomGraph: false, // option value: true | false

  // 禁止鼠标滚动移动画布
  stopScrollGraph: false, // option value: true | false

  // 禁止拖动画布
  stopMoveGraph: false, // option value: true | false

  // 允许调整边
  adjustEdge: false, // option value: true | false

  // 只对折线生效，只允许调整边的中间线段，不允许调整与起点终点相连的线段
  adjustEdgeMiddle: false, // option value: true | false

  // 允许调整边起点/终点
  adjustEdgeStartAndEnd: false, // option value: true | false

  // 允许拖动节点
  adjustNodePosition: true, // option value: true | false

  // 隐藏节点所有锚点
  hideAnchors: false, // option value: true | false

  // 允许节点文本可以编辑
  nodeTextEdit: false, // option value: true | false

  // 允许边文本可以编辑
  edgeTextEdit: false, // option value: true | false

  // 允许节点文本可以拖拽
  nodeTextDraggable: false, // option value: true | false

  // 允许边文本可以拖拽
  edgeTextDraggable: false, // option value: true | false

  // 允许按照 meta 键多选元素
  metaKeyMultipleSelected: false // option value: true | false
}

/**
 * 自定义键盘快捷键 参考 http://logic-flow.org/guide/basic/keyboard.html
 */
const keyboardConfig = {
  // 启用键盘快捷键
  enabled: true, // option value: true | false
}

/**
 * 网格配置 参考 http://logic-flow.org/guide/basic/grid.html
 */
const gridConfig = {
  // 启用网格
  enabled: true, // option value: true | false

  // 设置网格大小
  size: 10, // option value: number

  // 设置是否可见，若设置为 false 则不显示网格线但是仍然保留 size 栅格的效果
  visible: true, // option value: true | false

  // 设置网格类型，目前支持 dot 点状和 mesh 线状两种
  type: 'mesh', // option value: 'dot' | 'mesh'
  config: {
    // 设置网格的颜色
    color: '#eeeeee', // option value: HEX | RGB

    // 设置网格线的宽度
    thickness: 1, // option value: number
  }
}

/**
 * 杂项配置
 */
const extraConfig = {
  // 选区灵敏度
  SelectionSense: {
    // 是否要边的起点终点都在选区范围才算选中
    isWholeEdge: true, // option value: true | false

    // 是否要节点的全部点都在选区范围才算选中
    isWholeNode: true, // option value: true | false
  },

  // 默认连线类型
  defaultEdgeType: 'flow-bazier-edge' // option value: 'line' | 'polyline' | 'bezier' | 自定义连线类型
}

export {
  editConfig,
  keyboardConfig,
  gridConfig,
  extraConfig
}