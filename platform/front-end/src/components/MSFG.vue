<template>
  <div class="logic-flow-view">
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
import NodePanel from './MSFGComponents/NodePanel'
import Control from './MSFGComponents/Control'
import EditDialog from './MSFGComponents/EditDialog.vue'
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
      lf: null,
      dialogVisible: false,
      nodeList,
      formData: {},
    }
  },
  mounted () {
    this.$_initLf()
  },
  methods: {
    ...methods,
    $_dataUpdate (_node) {
      let node = this.lf.graphModel.getNodeModelById(_node.id)
      node.updateText(_node.text.value)
      node.setProperties({..._node.properties})
    }
  }
}
</script>

<style scoped>
.logic-flow-view {
  height: 95%;
  position: relative;
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