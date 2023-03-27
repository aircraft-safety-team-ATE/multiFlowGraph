import { h } from '@logicflow/core'
import BaseNode from './BaseNode'


class TestNodeModel extends BaseNode.model {
  initNodeData (data) {
    super.initNodeData(data)
  }
  setAttributes () {
    super.setAttributes()
    this.targetRules.push({
      message: "只允许连接左边的锚点",
      validate: (sourceNode, targetNode, sourceAnchor, targetAnchor) => {
        return targetAnchor.type === "left"
      }
    })
  }
  getDefaultAnchor () {
    const { x, y, id, width, height } = this
    const anchors = [
      {
        x: x - width / 2,
        y: y,
        id: `${id}_left`,
        type: "left"
      }
    ]
    return anchors
  }
}


class TestNodeView extends BaseNode.view {}


export default {
  type: 'test-node',
  model: TestNodeModel,
  view: TestNodeView
}