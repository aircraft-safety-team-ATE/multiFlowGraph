<template>
  <div class="logic-flow-view">
  <!-- 显示一些文本 -->
  <div style="float: left" class="current-system-breadcrumb">
					<span> 所在系统：</span>
					<span v-for="(item, itemid) in current_system_breadcrumb" >
						<el-tag v-if="item.name" @click="handleTagClick(item.id)" size="mini" type="primary">
							{{ item.name }}
						</el-tag> 
						<span v-if="itemid !== current_system_breadcrumb.length-1">{{'>'}}</span>
					</span>
				</div>
  <div class="model—tree">
    <el-tree :data="module_tree" :expand-on-click-node="false" :indent="8" :default-expand-all="true" :props="defaultProps" @node-click="handleNodeClick" class="module-tree"></el-tree>
  </div>
    <Control
      class="demo-control"
      v-if="lf"
      :lf="lf"
    />
    <NodePanel v-if="lf" :lf="lf" :nodeList="nodeList" :G_DATA="G_DATA" @updata-g-data="hangdle_update_gdata" @updata-g-data-subsystem="hangdle_update_gdata_subsystem"/>
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
      current_system_breadcrumb:'root',
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
  mounted () {
    this.$_initLf()
    this.module_tree =   this.getModuleTree(this.G_DATA.SystemData)
    console.log("data",this.module_tree)
    
    let root_system = this.G_DATA.SystemData.find(item => item.parent_id == null)

    this.current_system_breadcrumb = [{name:root_system.name,id:root_system.system_id}]
  },
  methods: {
    // 面包屑处理
    handleTagClick(sysid) {
				
				this.handleNodeClick({id: sysid});
			},
    // 跟新G_data数据 更新子系统的input或output
    hangdle_update_gdata_subsystem(data){
      // 根据子系统的id找到父系统
      let parent_id = this.G_DATA.SystemData.find(item => item.system_id == data.system_id).parent_id
      let parent_system = this.G_DATA.SystemData.find(item => item.system_id == parent_id)

      // 更新parent_system的中对应子系统的input或output
      if(data.type == 'input'){
        parent_system.data.nodes.find(item => item.properties.SubsystemId == data.system_id).properties.fields.input = data.value
      }else if(data.type == 'output'){
        parent_system.data.nodes.find(item => item.properties.SubsystemId == data.system_id).properties.fields.output = data.value
      }

      
    },
    // 更新G_data数据 添加新子系统
    hangdle_update_gdata(new_system){
      console.log("new_system",new_system)
      this.G_DATA.SystemData.push(new_system)
      this.module_tree =   this.getModuleTree(this.G_DATA.SystemData)
    },
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
      // 如果是更新子系统的text 则G_DATA中的数据也要更新
      if (_node.type == 'subsystem-node') {
        this.G_DATA.SystemData.find(item => item.system_id == _node.properties.SubsystemId).name = _node.text.value
        this.module_tree =   this.getModuleTree(this.G_DATA.SystemData)
      }
      console.log("node",_node.type)
    },
    handleNodeClick(data) {
      console.log(data)
        this.G_DATA.currentSystemId = data.id
        
        // 更新面包屑 面包屑结构为 [{name:xxx,id:xxx},{name:xxx,id:xxx}] 从当前系统开始一直到root
        this.current_system_breadcrumb = []
        let current_system= this.G_DATA.SystemData.find(item => item.system_id == data.id)
        while(current_system!=undefined){
          this.current_system_breadcrumb.push({name:current_system.name,id:current_system.system_id})
          current_system = this.G_DATA.SystemData.find(item => item.system_id==current_system.parent_id)
        }

        // 颠倒顺序，从root到当前系统
        this.current_system_breadcrumb = this.current_system_breadcrumb.reverse()

        this.$message({
          message: '当前系统已切换为' + this.current_system_breadcrumb.map(item => item.name).join(' > '),
          type:'success'
        })


        this.lf.render(this.G_DATA.SystemData.find(item => item.system_id == data.id).data)

      }
  }
}
</script>

<style scoped>
.current-system-breadcrumb{
  position: absolute;
  top:0px;
  left:200px;
}
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
  top: 50px;
  right: 50px;
  z-index: 2;
}
.LF-view {
  position: absolute;
  top: 50px;
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