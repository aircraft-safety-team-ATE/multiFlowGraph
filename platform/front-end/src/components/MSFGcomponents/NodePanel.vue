<template>
  <div class="node-panel">
    <div
      class="red-ui-palette-node ui-draggable ui-draggable-handle"
      @mousedown="$_dragNode(item)"
      v-for="(item, index) in nodeList"
      :key="index"
      :style="{ backgroundColor: item.properties.typeColor }"
    >
      <div class="red-ui-palette-label">{{ item.text }}</div>
      <div class="red-ui-palette-icon-container">
        <div class="red-ui-palette-icon" :style="{ backgroundImage: `url(${item.properties.icon})`}"></div>
      </div>
      <!-- <div class="red-ui-palette-port red-ui-palette-port-input"></div>
      <div class="red-ui-palette-port red-ui-palette-port-output"></div> -->
    </div>
  </div>
</template>

<script>
export default {
  name: 'NodePanel',
  props: {
    lf: Object,
    nodeList: Array,
  },
  methods: {
    $_dragNode (item) {
      this.$props.lf.dnd.startDrag({
        type: item.type,
        text: item.text,
        properties: item.properties
      })
    }
  }
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
  border-right: 1px solid rgba(0,0,0,.05);
  background-color: rgba(0,0,0,.05);
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
