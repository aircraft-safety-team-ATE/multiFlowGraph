import { h } from '@logicflow/core'
import BaseNode from './BaseNode'

const typeColor_open = '#96c24e'
const typeColor_close = '#E74C3C'

class SwitchNodeModel extends BaseNode.model {
  initNodeData (data) {
    super.initNodeData(data)
  }
  setAttributes () {
    super.setAttributes()
    if (this.properties.normalState) {
      this.defaultFill = typeColor_open
    } else {
      this.defaultFill = typeColor_close
    }
    const circleOnlyAsTarget = {
      message: "只允许从右边的锚点连出",
      validate: (sourceNode, targetNode, sourceAnchor, targetAnchor) => {
        return sourceAnchor.type === "right"
      }
    }
    this.sourceRules.push(circleOnlyAsTarget)
    this.targetRules.push({
      message: "只允许连接左边或上下两侧的锚点",
      validate: (sourceNode, targetNode, sourceAnchor, targetAnchor) => {
        return targetAnchor.type === "left" || 'top' || 'bottom'
      }
    })
  }
  getDefaultAnchor () {
    const { x, y, id, width, height } = this
    const anchors = [
      {
        x: x + width / 2,
        y: y,
        id: `${id}_right`,
        type: "right"
      },
      {
        x: x - width / 2,
        y: y,
        id: `${id}_left`,
        type: "left"
      },
      {
        x: x,
        y: y - height / 2,
        id: `${id}_top`,
        type: "top"
      },
      {
        x: x,
        y: y + height / 2,
        id: `${id}_bottom`,
        type: "bottom"
      }
    ]
    return anchors
  }
}


class SwitchNodeView extends BaseNode.view {}


export default {
  type: 'switch-node',
  model: SwitchNodeModel,
  view: SwitchNodeView
}