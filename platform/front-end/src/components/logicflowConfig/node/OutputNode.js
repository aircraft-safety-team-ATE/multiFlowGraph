import { h } from '@logicflow/core'
import BaseNode from './BaseNode'


class OutputNodeView extends BaseNode.view {
  getIcon () {
    const {
      width,
      height,
    } = this.props.model
    return h('image', {
      width: 30,
      height: 30,
      x: - width / 2,
      y: - height / 2,
      href: "https://cdn.jsdelivr.net/gh/Logic-Flow/logicflow-node-red-vue3@master/public/images/delay.svg"
    })
  }
}


class OutputNodeModel extends BaseNode.model {
  initNodeData (data) {
    super.initNodeData(data)
    this.defaultFill = '#10aec2'
  }
  setAttributes () {
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
  getConnectedSourceRules () {
    const rules = super.getConnectedSourceRules()
    const notAsTarget = {
      message: '终止节点不能作为连线的起点',
      validate: () => false
    }
    rules.push(notAsTarget)
    return rules
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


export default {
  type: 'output-node',
  model: OutputNodeModel,
  view: OutputNodeView
}