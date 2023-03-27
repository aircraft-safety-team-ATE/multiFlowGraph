import { h } from '@logicflow/core'
import BaseNode from './BaseNode'


class FaultNodeModel extends BaseNode.model {
  initNodeData (data) {
    super.initNodeData(data)
  }
  setAttributes () {
    super.setAttributes()
    const circleOnlyAsTarget = {
      message: "只允许从右边的锚点连出",
      validate: (sourceNode, targetNode, sourceAnchor, targetAnchor) => {
        return sourceAnchor.type === "right"
      }
    }
    this.sourceRules.push(circleOnlyAsTarget)
    this.targetRules.push({
      message: "只允许连接左边的锚点",
      validate: (sourceNode, targetNode, sourceAnchor, targetAnchor) => {
        return targetAnchor.type === "left"
      }
    })
  }
}


class FaultNodeView extends BaseNode.view {}


export default {
  type: 'fault-node',
  model: FaultNodeModel,
  view: FaultNodeView
}