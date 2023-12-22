<template>
  <div class="logic-flow-view">
  <div class="model—tree">
    <el-tree :data="module_tree" :props="defaultProps" @node-click="handleNodeClick" class="module-tree"></el-tree>
  </div>
    <Control
      class="demo-control"
      v-if="lf"
      :lf="lf"
    />
    <NodePanel v-if="lf" :lf="lf" :nodeList="nodeList" />
    <div ref="container" class="LF-view"></div>
    <EditDialog
      :dialog-visible.sync="dialogVisible"
      :form-data="formData"
      @data-update="$_dataUpdate" />
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
  data () {
    return {
      module_tree: [],
        defaultProps: {
          children: 'children',
          label: 'label'
        },
      // 全局数据
      G_DATA: [
        {"system_id":1,
        "name":"root",
        "parent_id":null,
        "data":[1,2]},
        {"system_id":2,
        "name":"root",
        "parent_id":1,
        "data":[1,2]},
        {"system_id":3,
        "name":"root",
        "parent_id":2,
        "data":[1,2]},
      
      ],
      lf: null,
      dialogVisible: false,
      nodeList,
      formData: {},
    }
  },
  mounted () {
    this.$_initLf()
    this.module_tree =   this.getModuleTree(this.G_DATA)
    console.log("data",this.module_tree)
  },
  methods: {

    // 从G_DATA中解析module_tree
    getModuleTree(G_DATA){

      let root  = G_DATA.filter(item => item.parent_id == null)[0]

      let root_node = {
        label: root.name,
        id:root.system_id,
        children: []
      }

      function getModuleTreeRecursive(node,G_DATA){
        
        let children = G_DATA.filter(item => item.parent_id == node.id)
        console.log("digui",children)
        if(children.length == 0){
          console.log("jieshi")
          return null
        }
        children.forEach(item => {
          let child_node = {
            label: item.name,
            id:item.system_id,
            children: []
          }
          node.children.push(child_node)
          getModuleTreeRecursive(child_node,G_DATA)
        })
      }
    
    console.log("start",root_node,G_DATA)
    getModuleTreeRecursive(root_node,G_DATA)
      return [root_node]
  },

    ...methods,
    $_dataUpdate (_node) {
      let node = this.lf.graphModel.getNodeModelById(_node.id)
      node.updateText(_node.text.value)
      node.setProperties({..._node.properties})
    },
          handleNodeClick(data) {
        console.log(data);
      }
  }
}
</script>

<style scoped>
.logic-flow-view {
  height: 95%;
  position: relative;
}
.model—tree{
  position: absolute;
  top: 400px;
  left: 0px;
  outline: none;
}
.demo-control {
  position: absolute;
  top: 0px;
  right: 50px;
  z-index: 2;
}
.LF-view {
  position: absolute;
  top: 0px;
  left: 150px;
  width: calc(100% - 200px);
  height: 100%;
  outline: none;
}
.node-panel {
  position: absolute;
  top: 0px;
}
</style>