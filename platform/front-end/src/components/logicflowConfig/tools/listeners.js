/**
 * 添加事件监听参考 http://logic-flow.org/guide/basic/event.html
 * LogicFlow 提供的事件参考 http://logic-flow.org/api/eventCenterApi.html
 * 也可以监听基于 LogicFlow eventCenter 抛出的自定义事件，如何抛出自定义事件参考 http://logic-flow.org/api/graphModelApi.html#eventcenter
 */
const listeners = {
  $_LfEvent () {
    // 单击节点 测试用
    this.lf.on('node:click', ({ data }) => {
      console.log(data) // for test
    })
    // 双击节点
    this.lf.on('node:dbclick', ({ data }) => {
      this.formData = data
      this.dialogVisible = true
    })
    // ※节点信息编辑
    this.lf.on('node:edit', (data) => {
      this.formData = data
      this.dialogVisible = true
    })
    // 鼠标进入节点
    this.lf.on('node:mouseenter', ({ data }) => {
      if (data.properties.showType === 'analyse' && data.type !== 'sub-system') {
        const { transformModel } = this.lf.graphModel
        const [x, y] = transformModel.CanvasPointToHtmlPoint([
          data.x,
          data.y
        ])
        let left = x + 150 + data.properties.width / 2
        let top = y - 37
        let element = document.createElement('div')
        element.className = "popper"
        element.style.left = `${left}px`
        element.style.top = `${top}px`
        // let para = document.createElement('p')
        // para.appendChild(document.createTextNode(`名称: ${data.text.value}`))
        // element.appendChild(para)
        // para = document.createElement('p')
        // para.appendChild(document.createTextNode(`故障分数: ${data.properties.state * 100}`))
        // element.appendChild(para)
        // para = document.createElement('p')
        // para.appendChild(document.createTextNode(`模糊分数: ${data.properties.fuzzy_state * 100}`))
        // element.appendChild(para)
        element.innerHTML = `
          <p>名称: ${data.text.value}</p>
          <p>故障分数: ${data.properties.state * 100}</p>
          <p>模糊分数: ${data.properties.fuzzy_state * 100}</p>
        `
        let view = document.querySelector('.logic-flow-view')
        view.appendChild(element)
      }
    })
    // 鼠标离开节点
    this.lf.on('node:mouseleave', (node) => {
      let element = document.querySelector('.popper')
      if (element) { element.remove() }
    })
    // 连线删除
    this.lf.on('edge:delete', ({data}) => {
      let node = this.lf.graphModel.getNodeModelById(data.targetNodeId)
      if (node.type === 'switch-node' && node.properties.control === data.sourceNodeId) {
        node.properties.control = null
      }
    })
    // 锚点连线拖动连线成功时触发，主要用于添加额外的连线验证
    this.lf.on('anchor:drop', (data) => {
      let model = data.edgeModel
      let edges = this.lf.getEdgeModels({
        sourceNodeId: model.sourceNodeId,
        targetNodeId: model.targetNodeId
      })
      if (edges.length > 1) {
        this.$alert('重复连线')
        this.lf.deleteEdge(model.id)
      } else {
        // 开关的控制节点接入
        if (model.targetNodeId + '_top' === model.targetAnchorId || model.targetNodeId + '_bottom' === model.targetAnchorId) {
          let node = this.lf.graphModel.getNodeModelById(model.targetNodeId)
          if (node.properties.control === null) {
            node.properties.control = model.sourceNodeId
          } else {
            this.$alert('该开关已有控制节点')
            this.lf.deleteEdge(model.id)
          }
        }
      }
    })
    // ※子系统折叠 & 展开
    this.lf.on('group:fold', (data) => {
      if (data.isFolded === true) {
        data.foldGroup(false)
        this.foldAllChild(data.children)
        data.foldGroup(true)
      } else {
        this.unfoldAllChild(data.children)
      }
    })
  }
}

export { listeners }