<template>
  <div class="node-panel">
    <div class="red-ui-palette-node ui-draggable ui-draggable-handle" @mousedown="$_dragNode(item)"
      v-for="(item, index) in nodeList" :key="index" :style="{ backgroundColor: item.properties.typeColor }">
      <div class="red-ui-palette-label">{{ item.text }}</div>
      <div class="red-ui-palette-icon-container">
        <div class="red-ui-palette-icon" :style="{ backgroundImage: `url(${item.properties.icon})` }"></div>
      </div>
      <!-- <div class="red-ui-palette-port red-ui-palette-port-input"></div>
      <div class="red-ui-palette-port red-ui-palette-port-output"></div> -->
    </div>
  </div>
</template>

<script>

var properties = {
  tableName: "",
  SubsystemId: 0,
  fields: {
    input: 0,
    output: 0
  }

}


export default {
  name: 'NodePanel',
  props: {
    lf: Object,
    nodeList: Array,
    G_DATA: Object
  },
  methods: {


    $_dragNode(item) {

      if (item.type == 'subsystem-node') {
        // 1.创建新的的system 
        let new_system = {
          system_id: this.$props.G_DATA.SystemData.at(-1).system_id + 1,
          name: "子系统"+(this.$props.G_DATA.SystemData.at(-1).system_id + 1),
          parent_id: this.$props.G_DATA.currentSystemId,
          data: {}
        }

        // 3. 更新G_DATA
        this.$emit("updata-g-data", new_system)

        properties.SubsystemId = new_system.system_id

        this.$props.lf.dnd.startDrag({
          text: "子系统" + new_system.system_id,
          type: item.type,
          properties: properties
        })

      } else if (item.type == 'input-node') {
        // 禁止在根系统中创建输入或者输出节点
        let current_system = this.$props.G_DATA.SystemData.find(item => item.system_id == this.$props.G_DATA.currentSystemId)
        if (current_system.parent_id == null) {
          this.$message({
            message: '禁止在根系统中创建输入或者输出节点',
            type: 'warning'
          });
          return
        }

        // 1.获取当前画布中 存在多少个input-node
        let input_node_num = this.$props.lf.getGraphData().nodes.filter(item => item.type == 'input-node').length
        // 2.修改所属子系统的input
        this.$emit("updata-g-data-subsystem", {
          system_id: this.$props.G_DATA.currentSystemId,
          type: 'input',
          value: input_node_num + 1
        })
        // 3.开始拖拽
        item.properties.index = input_node_num + 1
        this.$props.lf.dnd.startDrag({
          type: item.type,
          text: item.text + (input_node_num + 1),
          properties: item.properties
        })


      } else if (item.type == 'output-node') {
        // 禁止在根系统中创建输入或者输出节点
        let current_system = this.$props.G_DATA.SystemData.find(item => item.system_id == this.$props.G_DATA.currentSystemId)
        if (current_system.parent_id == null) {
          this.$message({
            message: '禁止在根系统中创建输入或者输出节点',
            type: 'warning'
          });
          return
        }

        // 1.获取当前画布中 存在多少个input-node
        let output_node_num = this.$props.lf.getGraphData().nodes.filter(item => item.type == 'output-node').length
        // 2.修改所属子系统的output
        this.$emit("updata-g-data-subsystem", {
          system_id: this.$props.G_DATA.currentSystemId,
          type: 'output',
          value: output_node_num + 1
        })
        // 3.开始拖拽
        item.properties.index = output_node_num + 1
        this.$props.lf.dnd.startDrag({
          type: item.type,
          text: item.text + (output_node_num + 1),
          properties: item.properties
        })
      }

      else {
        this.$props.lf.dnd.startDrag({
          type: item.type,
          text: item.text,
          properties: item.properties
        })
      }

    }
  },
}
</script>

<style>
.node-panel {
  position: absolute;
  top: 100px;
  left: 0px;
  width: 150px;
  padding: 20px 10px;
  background-color: white;
  box-shadow: 0 0 10px 1px rgb(228, 224, 219);
  border-radius: 6px;
  text-align: center;
  z-index: 101;
}

.node-item {
  margin-bottom: 20px;
}

.node-item-icon {
  width: 30px;
  height: 30px;
  margin-left: 20px;
  background-size: cover;
}

.node-label {
  font-size: 12px;
  margin-top: 5px;
  user-select: none;
}

.red-ui-palette-node {
  cursor: move;
  background: #fff;
  margin: 10px auto;
  height: 25px;
  border-radius: 5px;
  border: 1px solid #999;
  background-position: 5% 50%;
  background-repeat: no-repeat;
  width: 120px;
  background-size: contain;
  position: relative;
}

.red-ui-palette-label {
  color: #333;
  font-size: 13px;
  margin: 4px 0 4px 32px;
  line-height: 20px;
  overflow: hidden;
  text-align: center;
  -webkit-user-select: none;
  -khtml-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
  user-select: none;
}

.red-ui-palette-icon-container {
  position: absolute;
  text-align: center;
  top: 0;
  bottom: 0;
  left: 0;
  width: 30px;
  border-right: 1px solid rgba(0, 0, 0, .05);
  background-color: rgba(0, 0, 0, .05);
}

.red-ui-palette-icon {
  display: inline-block;
  width: 20px;
  height: 100%;
  background-position: 50% 50%;
  background-size: contain;
  background-repeat: no-repeat;
}

/* .red-ui-palette-port-output {
  left: auto;
  right: -6px;
}
.red-ui-palette-port {
  position: absolute;
  top: 8px;
  left: -5px;
  box-sizing: border-box;
  -moz-box-sizing: border-box;
  background: #d9d9d9;
  border-radius: 3px;
  width: 10px;
  height: 10px;
  border: 1px solid #999;
}
.red-ui-palette-port-output {
  left: auto;
  right: -6px;
} */
</style>
