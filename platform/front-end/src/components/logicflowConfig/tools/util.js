import { subsystemInit } from "../init"

const utils = {
  createSub () {
    const { nodes } = this.lf.getSelectElements()
    if (nodes.length === 0) {
      this.$alert('未选中任何节点，无法创建子系统！')
    } else {
      this.lf.clearSelectElements()
      const { startPoint, endPoint } = this.lf.extension.selectionSelect
      // startPoint 和 endPoint 是 dom 坐标，需要转换成 canvas 坐标绘制
      const { transformModel } = this.lf.graphModel
      const [x1, y1] = transformModel.HtmlPointToCanvasPoint([
        startPoint.x,
        startPoint.y
      ])
      const [x2, y2] = transformModel.HtmlPointToCanvasPoint([
        endPoint.x,
        endPoint.y
      ])
      const width = x2 - x1
      const height = y2 - y1
      let node = {...subsystemInit}
      node.x = x1 + width / 2
      node.y = y1 + height / 2
      node.properties.nodeSize = {
        width: width,
        height: height
      }
      node.children = nodes.map((item) => item.id)
      this.lf.addNode(node)
      this.lf.render(this.$data.lf.getGraphRawData())
    }
  },
  foldAllChild (child) {
    child.forEach((nodeID) => {
      let node = this.lf.graphModel.getNodeModelById(nodeID)
      if (node.type === 'sub-system') {
        if (node.isFolded === false) {
          this.foldAllChild(node.children)
          node.foldGroup(true)
        }
        if (node.isFolded === true) {
          node.foldGroup(false)
          this.foldAllChild(node.children)
          node.foldGroup(true)
        }
      }
    })
  },
  unfoldAllChild (child) {
    child.forEach((nodeID) => {
      let node = this.lf.graphModel.getNodeModelById(nodeID)
      if (node.type === 'sub-system') {
        node.foldGroup(false)
        this.unfoldAllChild(node.children)
      }
    })
  },
}

export { utils }