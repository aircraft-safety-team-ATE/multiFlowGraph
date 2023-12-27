/**
 * 自定义菜单栏 参考 http://logic-flow.org/guide/extension/component-menu.html
 */
const menu = {
  $_render() {
    // 自定义常规右键菜单
    this.lf.extension.menu.setMenuConfig({
      // 节点右键菜单
      nodeMenu: [
        {
          text: '删除',
          callback: (node) => {
            this.lf.deleteNode(node.id)
            // 删除子系统需要特殊处理
            if (node.type === "subsystem-node") {
              // 1.在G_DATA中删除该子系统,递归的删除该子系统下的所有节点
              function deleteSubsystem(delete_system_id, G_DATA) {

                G_DATA.SystemData = G_DATA.SystemData.filter((item) => {
                  return item.system_id !== delete_system_id
                })

                let list_systems = G_DATA.SystemData.filter((item) => {
                  return item.parent_id == delete_system_id
                })

                list_systems.forEach((item) => {
                  deleteSubsystem(item.system_id, G_DATA)
                })
              }

              deleteSubsystem(node.properties.SubsystemId, this.G_DATA)

              // 2. 更新module tree
              this.module_tree = this.getModuleTree(this.G_DATA.SystemData)
            } else if (node.type === "input-node") {
              // 1. 将剩余input节点的index重新排序和命名
              let graph_data = this.lf.getGraphData()
              let input_nodes = graph_data.nodes.filter((item) => {
                return item.type === "input-node"
              })

              input_nodes.forEach((item, index) => {
                item.properties.index = index + 1
                item.text = "输入" + (index + 1)
              })
              // 2. 将父系统中的子系统组件的input属性更新


              // 根据子系统的id找到父系统
              let parent_id = this.G_DATA.SystemData.find(item => item.system_id == this.G_DATA.currentSystemId).parent_id
              let parent_system = this.G_DATA.SystemData.find(item => item.system_id == parent_id)

              // 更新parent_system的中对应子系统的input或output
              let subsystem_node = parent_system.data.nodes.find(item => item.properties.SubsystemId == this.G_DATA.currentSystemId)
              subsystem_node.properties.fields.input = input_nodes.length
              // 更新parent_system的中对应子系统的input或output连线的锚点数据
              // 1. 删除相关连线
              let input_anchors = subsystem_node.anchors.filter(item => item.type == "left")
              let delete_edge_index = parent_system.data.edges.findIndex(item => item.targetAnchorId == input_anchors[node.properties.index - 1].id)
              if (delete_edge_index != -1) {
                parent_system.data.edges.splice(delete_edge_index, 1)
              }
              // 2. 重排其他连线的顺序
              for (let i = node.properties.index; i < input_anchors.length; i++) {
                let edge_index = parent_system.data.edges.findIndex(item => item.targetAnchorId == input_anchors[i].id)
                if (edge_index != -1) {
                  parent_system.data.edges[edge_index].targetAnchorId = input_anchors[i - 1].id
                }
              }



              // 3. 重新渲染页面
              this.lf.render(graph_data)
            } else if (node.type === "output-node") {
              // 1. 将剩余input节点的index重新排序和命名
              let graph_data = this.lf.getGraphData()
              let output_nodes = graph_data.nodes.filter((item) => {
                return item.type === "output-node"
              })

              output_nodes.forEach((item, index) => {
                item.properties.index = index + 1
                item.text = "输出" + (index + 1)
              })
              // 2. 将父系统中的子系统组件的input属性更新

              // 根据子系统的id找到父系统
              let parent_id = this.G_DATA.SystemData.find(item => item.system_id == this.G_DATA.currentSystemId).parent_id
              let parent_system = this.G_DATA.SystemData.find(item => item.system_id == parent_id)

              // 更新parent_system的中对应子系统的input或output
              let subsystem_node = parent_system.data.nodes.find(item => item.properties.SubsystemId == this.G_DATA.currentSystemId)
              subsystem_node.properties.fields.output = output_nodes.length
              // 更新parent_system的中对应子系统的input或output连线的锚点数据
              // 1. 删除相关连线
              let output_anchors = subsystem_node.anchors.filter(item => item.type == "right")
              let delete_edge_index = parent_system.data.edges.findIndex(item => item.sourceAnchorId == output_anchors[node.properties.index - 1].id)
              if (delete_edge_index != -1) {
                parent_system.data.edges.splice(delete_edge_index, 1)
              }
              // 2. 重排其他连线的顺序
              for (let i = node.properties.index; i < output_anchors.length; i++) {
                let edge_index = parent_system.data.edges.findIndex(item => item.sourceAnchorId == output_anchors[i].id)
                if (edge_index != -1) {
                  parent_system.data.edges[edge_index].sourceAnchorId = output_anchors[i - 1].id
                }
              }


              // 3. 重新渲染页面
              this.lf.render(graph_data)

            }
            // 删除 输入或输出节点需要特殊处理
          }
        },
        {
          text: '编辑节点属性',
          callback: (node) => {
            this.lf.graphModel.eventCenter.emit('node:edit', node)
          }
        }
      ],
      // 边右键菜单
      edgeMenu: [
        {
          text: '删除',
          callback: (edge) => {
            this.lf.deleteEdge(edge.id)
          }
        }
      ]
    })
    // 自定义选区右键菜单
    this.lf.extension.menu.setMenuByType({
      type: 'lf:defaultSelectionMenu',
      menu: [
        {
          text: '删除',
          callback: (select) => {
            select.nodes.map((item) => {
              this.lf.deleteNode(item.id)
              // 删除子系统需要特殊处理
              if (item.type === "subsystem-node") {
                // 1.在G_DATA中删除该子系统,递归的删除该子系统下的所有节点
                function deleteSubsystem(delete_system_id, G_DATA) {

                  G_DATA.SystemData = G_DATA.SystemData.filter((item) => {
                    return item.system_id !== delete_system_id
                  })

                  let list_systems = G_DATA.SystemData.filter((item) => {
                    return item.parent_id == delete_system_id
                  })

                  list_systems.forEach((item) => {
                    deleteSubsystem(item.system_id, G_DATA)
                  })
                }

                deleteSubsystem(item.properties.SubsystemId, this.G_DATA)

                // 2. 更新module tree
                this.module_tree = this.getModuleTree(this.G_DATA.SystemData)
              } else if (item.type === "input-node") {
                // 1. 将剩余input节点的index重新排序和命名
                let graph_data = this.lf.getGraphData()
                let input_nodes = graph_data.nodes.filter((item) => {
                  return item.type === "input-node"
                })

                input_nodes.forEach((item, index) => {
                  item.properties.index = index + 1
                  item.text = "输入" + (index + 1)
                })
                // 2. 将父系统中的子系统组件的input属性更新

                // 根据子系统的id找到父系统
                let parent_id = this.G_DATA.SystemData.find(item => item.system_id == this.G_DATA.currentSystemId).parent_id
                let parent_system = this.G_DATA.SystemData.find(item => item.system_id == parent_id)

                // 更新parent_system的中对应子系统的input或output

                parent_system.data.nodes.find(item => item.properties.SubsystemId == this.G_DATA.currentSystemId).properties.fields.input = input_nodes.length

                // 3. 重新渲染页面
                this.lf.render(graph_data)
              } else if (item.type === "output-node") {
                // 1. 将剩余input节点的index重新排序和命名
                let graph_data = this.lf.getGraphData()
                let output_nodes = graph_data.nodes.filter((item) => {
                  return item.type === "output-node"
                })

                output_nodes.forEach((item, index) => {
                  item.properties.index = index + 1
                  item.text = "输出" + (index + 1)
                })
                // 2. 将父系统中的子系统组件的input属性更新

                // 根据子系统的id找到父系统
                let parent_id = this.G_DATA.SystemData.find(item => item.system_id == this.G_DATA.currentSystemId).parent_id
                let parent_system = this.G_DATA.SystemData.find(item => item.system_id == parent_id)

                // 更新parent_system的中对应子系统的input或output

                parent_system.data.nodes.find(item => item.properties.SubsystemId == this.G_DATA.currentSystemId).properties.fields.output = output_nodes.length

                // 3. 重新渲染页面
                this.lf.render(graph_data)
              }
              // 删除 输入或输出节点需要特殊处理
            })
            select.edges.map((item) => { this.lf.deleteEdge(item.id) })
          }
        },
        {
          text: '分组',
          callback: this.createSub
        }
      ]
    })
    // 自定义子系统右键菜单
    this.lf.extension.menu.setMenuByType({
      type: 'sub-system',
      menu: [
        {
          text: '删除子系统',
          callback: (node) => {
            this.lf.deleteNode(node.id)
          }
        },
        {
          text: '解除子系统',
          callback: (node) => {
            let sub = this.lf.getNodeModelById(node.id)
            let { nodes } = this.lf.getGraphRawData()
            nodes.some((itm) => {
              if (itm.type === 'sub-system' && itm.children.indexOf(node.id) !== -1) {
                let parent = this.lf.getNodeModelById(itm.id)
                node.children.forEach((child) => { parent.addChild(child) })
                return true
              } else {
                return false
              }
            })
            node.children.forEach((child) => { sub.removeChild(child) })
            this.lf.deleteNode(node.id)
          }
        }
      ]
    })
    // 自定义侧边栏 参考 http://logic-flow.org/guide/extension/component-dnd-panel.html
    this.lf.extension.dndPanel.setPatternItems([
      {
        label: '选区',
        icon: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAAH6ji2bAAAABGdBTUEAALGPC/xhBQAAAOVJREFUOBGtVMENwzAIjKP++2026ETdpv10iy7WFbqFyyW6GBywLCv5gI+Dw2Bluj1znuSjhb99Gkn6QILDY2imo60p8nsnc9bEo3+QJ+AKHfMdZHnl78wyTnyHZD53Zzx73MRSgYvnqgCUHj6gwdck7Zsp1VOrz0Uz8NbKunzAW+Gu4fYW28bUYutYlzSa7B84Fh7d1kjLwhcSdYAYrdkMQVpsBr5XgDGuXwQfQr0y9zwLda+DUYXLaGKdd2ZTtvbolaO87pdo24hP7ov16N0zArH1ur3iwJpXxm+v7oAJNR4JEP8DoAuSFEkYH7cAAAAASUVORK5CYII=',
        callback: () => {
          this.lf.extension.selectionSelect.openSelectionSelect()
          this.lf.once('selection:selected', () => {
            this.lf.extension.selectionSelect.closeSelectionSelect()
          })
        }
      },
      {
        label: '分组',
        icon: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAAH6ji2bAAAABGdBTUEAALGPC/xhBQAAA1BJREFUOBFtVE1IVUEYPXOf+tq40Y3vPcmFIdSjIorWoRG0ERWUgnb5FwVhYQSl72oUoZAboxKNFtWiwKRN0M+jpfSzqJAQclHo001tKkjl3emc8V69igP3znzfnO/M9zcDcKT67azmjYWTwl9Vn7Vumeqzj1DVb6cleQY4oAVnIOPb+mKAGxQmKI5CWNJ2aLPatxWa3aB9K7/fB+/Z0jUF6TmMlFLQqrkECWQzOZxYGjTlOl8eeKaIY5yHnFn486xBustDjWT6dG7pmjHOJd+33t0iitTPkK6tEvjxq4h2MozQ6WFSX/LkDUGfFwfhEZj1Auz/U4pyAi5Sznd7uKzznXeVHlI/Aywmk6j7fsUsEuCGADrWARXXwjxWQsUbIupDHJI7kF5dRktg0eN81IbiZXiTESic50iwS+t1oJgL83jAiBupLDCQqwziaWSoAFSeIR3P5Xv5az00wyIn35QRYTwdSYbz8pH8fxUUAtxnFvYmEmgI0wYXUXcCCSpeEVpXlsRhBnCEATxWylL9+EKCAYhe1NGstUa6356kS9NVvt3DU2fd+Wtbm/+lSbylJqsqkSm9CRhvoJVlvKPvF1RKY/FcPn5j4UfIMLn8D4UYb54BNsilTDXKnF4CfTobA0FpoW/LSp306wkXM+XaOJhZaFkcNM82ASNAWMrhrUbRfmyeI1FvRBTpN06WKxa9BK0o2E4Pd3zfBBEwPsv9sQBnmLVbLEIZ/Xe9LYwJu/Er17W6HYVBc7vmuk0xUQ+pqxdom5Fnp55SiytXLPYoMXNM4u4SNSCFWnrVIzKG3EGyMXo6n/BQOe+bX3FClY4PwydVhthOZ9NnS+ntiLh0fxtlUJHAuGaFoVmttpVMeum0p3WEXbcll94l1wM/gZ0Ccczop77VvN2I7TlsZCsuXf1WHvWEhjO8DPtyOVg2/mvK9QqboEth+7pD6NUQC1HN/TwvydGBARi9MZSzLE4b8Ru3XhX2PBxf8E1er2A6516o0w4sIA+lwURhAON82Kwe2iDAC1Watq4XHaGQ7skLcFOtI5lDxuM2gZe6WFIotPAhbaeYlU4to5cuarF1QrcZ/lwrLaCJl66JBocYZnrNlvm2+MBCTmUymPrYZVbjdlr/BxlMjmNmNI3SAAAAAElFTkSuQmCC',
        callback: this.createSub
      }
    ])
    this.lf.render({})
    this.$_LfEvent()
  }
}

/**
 * 按钮组自定义，设置是否提供该功能的按钮
 */
const controlConfig = {
  // 放大
  zoomIn: true,  // option value: true | false

  // 缩小
  zoomOut: true,  // option value: true | false

  // 大小适应
  zoomReset: true,  // option value: true | false

  // 定位还原
  translateRest: true,  // option value: true | false

  // 还原(大小&定位)
  reset: true,  // option value: true | false

  // 撤销
  undo: true,  // option value: true | false

  // 重做
  redo: true,  // option value: true | false

  // 清空
  clear: true,  // option value: true | false

  // 重绘
  reDraw: true,  // option value: true | false

  // 导出流图
  exportData: true,  // option value: true | false

  // 载入流图
  importData: true,  // option value: true | false

  // 载入FMECA
  importFMECA: true,  // option value: true | false

  // 流图评价 ※需要与后台交互
  check: true,  // option value: true | false

  // 测点优化
  optimizeCkpt: true,

  // 故障分析 ※需要与后台交互
  analyse: true  // option value: true | false

  
}

export { menu, controlConfig }