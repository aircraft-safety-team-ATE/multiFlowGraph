<template>
  <div class="logic-flow-view">
    <!-- 显示一些文本 -->
    <div style="float: left" class="current-system-breadcrumb">

      <div>
        <span> 所在系统：</span>
        <span v-for="(item, itemid) in current_system_breadcrumb">
          <el-tag v-if="item.name" @click="handleTagClick(item.id)" size="mini" type="primary">
            {{ item.name }}
          </el-tag>
          <span v-if="itemid !== current_system_breadcrumb.length - 1">{{ '>' }}</span>
        </span>
      </div>

      <div>
        访问我们的 GitHub 项目（欢迎发现bug 并提交issue）：
        <a href="https://github.com/aircraft-safety-team-ATE/multiFlowGraph/tree/feature-subsystemSetting-fengzhaoyu" target="_blank">multiFlowGraph 项目</a>
      </div>
    </div>

    <div class="model—tree">
      <el-tree :data="module_tree" :expand-on-click-node="false" :indent="16" :default-expand-all="true"
        :props="defaultProps" @node-click="handleNodeClick" class="module-tree"></el-tree>
    </div>

    <Control class="demo-control" v-if="lf" :lf="lf" :G_DATA="G_DATA" @updata-import-data="handle_update_import_data" />

    <NodePanel v-if="lf" :lf="lf" :nodeList="nodeList" :G_DATA="G_DATA" @updata-g-data="hangdle_update_gdata"
      @updata-g-data-subsystem="hangdle_update_gdata_subsystem" />

    <div ref="container" class="LF-view"></div>

    <EditDialog :dialog-visible.sync="dialogVisible" :form-data="formData" @data-update="$_dataUpdate" />
  </div>
</template>

<script>
import { nodeList } from './logicflowConfig/init.js'
import NodePanel from './MSFGcomponents/NodePanel.vue'
import Control from './MSFGcomponents/Control.vue'
import EditDialog from './MSFGcomponents/EditDialog.vue'
import '@logicflow/extension/lib/style/index.css'
import './logicflowConfig/tools/style.css'
import { methods } from './logicflowConfig'

export default {
  name: 'MSFG',
  components: {
    NodePanel: NodePanel,
    Control: Control,
    EditDialog: EditDialog
  },
  data() {
    return {
      current_system_breadcrumb: 'root',
      module_tree: [],
      defaultProps: {
        children: 'children',
        label: 'label'
      },
      // 全局数据
      G_DATA: {},
      lf: null,
      dialogVisible: false,
      nodeList,
      formData: {},
    }
  },
  mounted() {
    this.$_initLf()
    this.module_tree = this.getModuleTree(this.G_DATA.SystemData)

    let root_system = this.G_DATA.SystemData.find(item => item.parent_id == null)

    this.current_system_breadcrumb = [{ name: root_system.name, id: root_system.system_id }]
  },
  methods: {
    // 面包屑处理
    handleTagClick(sysid) {

      this.handleNodeClick({ id: sysid });
    },
    // 跟新G_data数据 更新子系统的input或output
    handle_update_import_data(data) {

      let root_system_import = data.value.SystemData.find(item => item.parent_id == null)
      // 1. 删除一切输入和输出节点 以及相关的边
      let inputORoutput_nodes = root_system_import.data.nodes.filter(item => item.type == 'input-node' || item.type == 'output-node')
      // 1.1 删除所有的相关边与节点
      for (let node of inputORoutput_nodes) {

        let edges = root_system_import.data.edges.filter(item => item.sourceNodeId == node.id || item.targetNodeId == node.id)
        for (let edge of edges) {
          root_system_import.data.edges.splice(root_system_import.data.edges.indexOf(edge), 1)
        }
        root_system_import.data.nodes.splice(root_system_import.data.nodes.indexOf(node), 1)
      }

      if (data.type == 'global') {
        this.G_DATA = data.value
        let root_id = this.G_DATA.SystemData.find(item => item.parent_id == null).system_id
        this.handleNodeClick({ id: root_id })

        //
      } else if (data.type == 'part_incremental') {
        //1.将当前系统与导入的根系统进行合并
        let current_system = this.G_DATA.SystemData.find(item => item.system_id == this.G_DATA.currentSystemId)
        let root_system_import = data.value.SystemData.find(item => item.parent_id == null)
        function isEmptyObject(obj) {
          return Object.keys(obj).length === 0 && obj.constructor === Object;
        }

        if (isEmptyObject(current_system.data)) {
          current_system.data = root_system_import.data
        } else if (current_system.data.nodes.length == 0) {
          current_system.data = root_system_import.data
        }
        else {


          let current_system_rectangle = {
            x_leftUP: 1000000,
            y_leftUP: 1000000,
            x_rightDOWN: -1000000,
            y_rightDOWN: -1000000,

          }
          let root_system_import_rectangle = {
            x_leftUP: 1000000,
            y_leftUP: 1000000,
            x_rightDOWN: -1000000,
            y_rightDOWN: -1000000,
          }

          current_system.data.nodes.forEach(item => {
            if (item.x < current_system_rectangle.x_leftUP) {
              current_system_rectangle.x_leftUP = item.x
            }
            if (item.y < current_system_rectangle.y_leftUP) {
              current_system_rectangle.y_leftUP = item.y
            }
            if (item.x > current_system_rectangle.x_rightDOWN) {
              current_system_rectangle.x_rightDOWN = item.x
            }
            if (item.y > current_system_rectangle.y_rightDOWN) {
              current_system_rectangle.y_rightDOWN = item.y
            }
          })

          for (const item of root_system_import.data.nodes) {
            if (item.x < root_system_import_rectangle.x_leftUP) {
              root_system_import_rectangle.x_leftUP = item.x;
            }
            if (item.y < root_system_import_rectangle.y_leftUP) {
              root_system_import_rectangle.y_leftUP = item.y;
            }
            if (item.x > root_system_import_rectangle.x_rightDOWN) {
              root_system_import_rectangle.x_rightDOWN = item.x;
            }
            if (item.y > root_system_import_rectangle.y_rightDOWN) {
              root_system_import_rectangle.y_rightDOWN = item.y;
            }

            // 修复重复导入bug
            if (current_system.data.nodes.find(item2 => item2.id === item.id) !== undefined) {
              this.$message({
                message: '禁止重复导入 (有残余模块也会触发)',
                type: 'warning'
              });
              console.log('重复导入');
              return; // 这会停止整个函数的执行
            }
          }

          let x_offset = current_system_rectangle.x_rightDOWN - root_system_import_rectangle.x_leftUP + 300
          let y_offset = current_system_rectangle.y_leftUP - root_system_import_rectangle.y_leftUP

          // 将导入的根系统的节点坐标进行偏移
          root_system_import.data.nodes.forEach(item => {
            item.x += x_offset
            item.y += y_offset
            if (item.type == 'subsystem-node') {
              item.text.x += x_offset
              item.text.y += y_offset

            }

            current_system.data.nodes.push(item)
          })
          // 将导入的根系统的边进行偏移
          root_system_import.data.edges.forEach(item => {
            item.startPoint.x += x_offset
            item.startPoint.y += y_offset
            item.endPoint.x += x_offset
            item.endPoint.y += y_offset
            item.pointsList.forEach(point => {
              point.x += x_offset
              point.y += y_offset
            })
            current_system.data.edges.push(item)
          })

        }
        //2.将导入的子系统添加到this.G_DATA
        function getSubSystemRecursive(old_system_id, new_system_id, import_G_DATA, G_DATA) {
          // 调整子系统节点的systemid
          let current_system = G_DATA.SystemData.find(item => item.system_id == new_system_id)
          let current_system_subsystem_nodes = current_system.data.nodes.filter(item => item.type == 'subsystem-node')

          let children = import_G_DATA.SystemData.filter(item => item.parent_id == old_system_id)
          function deepClone(obj) {
            let _obj = JSON.stringify(obj),
              objClone = JSON.parse(_obj);
            return objClone
          }
          children.forEach(item => {


            let item_copy = deepClone(item)
            let old_system_id = item_copy.system_id
            item_copy.system_id = G_DATA.SystemData.length + 1
            item_copy.parent_id = new_system_id
            if (current_system_subsystem_nodes.find(item => item.properties.SubsystemId == old_system_id) !== undefined) {
              current_system_subsystem_nodes.find(item => item.properties.SubsystemId == old_system_id).properties.SubsystemId = item_copy.system_id
            }

            G_DATA.SystemData.push(item_copy)


            getSubSystemRecursive(old_system_id, item_copy.system_id, import_G_DATA, G_DATA)
          })

        }

        getSubSystemRecursive(root_system_import.system_id, current_system.system_id, data.value, this.G_DATA)
        this.handleNodeClick({ id: this.G_DATA.currentSystemId })
      }
      this.module_tree = this.getModuleTree(this.G_DATA.SystemData)
    },

    hangdle_update_gdata_subsystem(data) {
      // 根据子系统的id找到父系统
      let parent_id = this.G_DATA.SystemData.find(item => item.system_id == data.system_id).parent_id
      let parent_system = this.G_DATA.SystemData.find(item => item.system_id == parent_id)
      // 更新parent_system的中对应子系统的input或output
      if (data.type == 'input') {
        parent_system.data.nodes.find(item => item.properties.SubsystemId == data.system_id).properties.fields.input = data.value
      } else if (data.type == 'output') {
        parent_system.data.nodes.find(item => item.properties.SubsystemId == data.system_id).properties.fields.output = data.value
      }


    },
    // 更新G_data数据 添加新子系统
    hangdle_update_gdata(new_system) {
      this.G_DATA.SystemData.push(new_system)
      this.module_tree = this.getModuleTree(this.G_DATA.SystemData)
    },
    // 从G_DATA中解析module_tree
    getModuleTree(G_DATA) {

      let root = G_DATA.filter(item => item.parent_id == null)[0]

      let root_node = {
        label: root.name,
        id: root.system_id,
        children: []
      }

      function getModuleTreeRecursive(node, G_DATA) {

        let children = G_DATA.filter(item => item.parent_id == node.id)
        if (children.length == 0) {
          return null
        }
        children.forEach(item => {
          let child_node = {
            label: item.name,
            id: item.system_id,
            children: []
          }
          node.children.push(child_node)
          getModuleTreeRecursive(child_node, G_DATA)
        })
      }

      getModuleTreeRecursive(root_node, G_DATA)
      return [root_node]
    },

    ...methods,
    $_dataUpdate(_node) {
      let node = this.lf.graphModel.getNodeModelById(_node.id)
      node.updateText(_node.text.value)
      node.setProperties({ ..._node.properties })
      // 如果是更新子系统的text 则G_DATA中的数据也要更新
      if (_node.type == 'subsystem-node') {
        this.G_DATA.SystemData.find(item => item.system_id == _node.properties.SubsystemId).name = _node.text.value
        this.module_tree = this.getModuleTree(this.G_DATA.SystemData)
      }
    },
    handleNodeClick(data) {
      this.G_DATA.currentSystemId = data.id

      // 更新面包屑 面包屑结构为 [{name:xxx,id:xxx},{name:xxx,id:xxx}] 从当前系统开始一直到root
      this.current_system_breadcrumb = []
      let current_system = this.G_DATA.SystemData.find(item => item.system_id == data.id)
      while (current_system != undefined) {
        this.current_system_breadcrumb.push({ name: current_system.name, id: current_system.system_id })
        current_system = this.G_DATA.SystemData.find(item => item.system_id == current_system.parent_id)
      }

      // 颠倒顺序，从root到当前系统
      this.current_system_breadcrumb = this.current_system_breadcrumb.reverse()

      this.$message({
        message: '当前系统已切换为' + this.current_system_breadcrumb.map(item => item.name).join(' > '),
        type: 'success'
      })


      // 临时补丁，当子系统的属性如input或output发生变化时，先渲染一次，更新子系统的外观属性，手动重新调整 线的起点和终点位置 然后再渲染一次
      // 1. 第一次渲染 并获取渲染后的绘图数据
      this.lf.render(this.G_DATA.SystemData.find(item => item.system_id == data.id).data)
      let current_system_data = this.lf.getGraphData()

      // 2. 调整与子系统相关的连线的起点和终点位置
      let subsystem_nodes = current_system_data.nodes.filter(item => item.type == 'subsystem-node')

      for (let node of subsystem_nodes) {
        for (let anchor of node.anchors) {
          if (anchor.type == 'left') {
            // 调整连线的终点位置
            let relative_edges = current_system_data.edges.filter(item => item.targetAnchorId == anchor.id)
            relative_edges.forEach(item => {

              item.pointsList = []

              item.endPoint.x = anchor.x
              item.endPoint.y = anchor.y
            })
          } else if (anchor.type == 'right') {
            // 调整连线的起点位置
            let relative_edges = current_system_data.edges.filter(item => item.sourceAnchorId == anchor.id)
            relative_edges.forEach(item => {
              item.pointsList = []
              item.startPoint.x = anchor.x
              item.startPoint.y = anchor.y
            })
          }

        }
      }
      // 3. 再一次渲染
      this.lf.render(current_system_data)


    }
  }
}
</script>

<style scoped>
.logic-flow-view {
  height: 100vh;
  position: relative;
  overflow-y: hidden;
}

.current-system-breadcrumb {
  width: calc(100% - 150px);
  height: 40px;
  position: absolute;
  top: 0px;
  left: 150px;
  padding: 0px 20px;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
}

.model—tree {
  height: calc(100% - 300px);
  width: 150px;
  position: absolute;
  top: 300px;
  left: 0px;
  outline: none;
}

.demo-control {
  position: absolute;
  top: 40px;
  right: 20px;
  z-index: 2;
}

.LF-view {
  position: absolute;
  top: 40px;
  left: 150px;
  width: calc(100% - 150px);
  height: calc(100% - 40px);
  outline: none;
}

.node-panel {
  position: absolute;
  top: 0px;
}
</style>