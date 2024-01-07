import { BezierEdge,BezierEdgeModel  } from '@logicflow/core'

class FlowBazierEdgeModel extends BezierEdgeModel {
  getData() {
    const data = super.getData();
    data.sourceAnchorId = this.sourceAnchorId;
    data.targetAnchorId = this.targetAnchorId;
    return data;
  }
  setAttributes () {
    this.isAnimation = true
  }
  getEdgeAnimationStyle () {
    const style = super.getEdgeAnimationStyle()
    style.strokeDasharray = "5 5"
    style.animationDuration = "100s"
    return style
  }
}





class FlowBazierEdge extends BezierEdge {}


export default {
  type: "flow-bazier-edge",
  model: FlowBazierEdgeModel,
  view: FlowBazierEdge
}