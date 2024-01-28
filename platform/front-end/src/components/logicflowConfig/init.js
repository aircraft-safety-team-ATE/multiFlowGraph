/**
 * 公有初始化属性
 */
const common = {
  showType: 'edit',
  collision : false,
  detectable: true,
  fuzzible: false,
  fuzzy_state: 0,
  state: 0
}

/**
 * 节点初始化
 */
const nodeList = [
  {
    type: 'test-node',
    text: '测试',
    properties: {
      // common
      ...common,
      icon: require("@/assets/images/delay.svg"),
      typeColor: '#eea2a4',
      // special
    }
  },
  {
    type: 'fault-node',
    text: '故障',
    properties: {
      // common
      ...common,
      icon: require("@/assets/images/delay.svg"),
      typeColor: '#edc3ae',
      // special
      flevel: 0, //故障等级
    }
  },
  {
    type: 'switch-node',
    text: '开关',
    properties: {
      // common
      ...common,
      icon: require("@/assets/images/delay.svg"),
      typeColor: '#96c24e',
      // special
      normalState: true, // true | false 开关常态（常开|常闭）
      control: null, // 控制节点
    }
  },
  {
    type: 'algorithm-node',
    text: '算法',
    properties: {
      // common
      ...common,
      icon: require("@/assets/images/delay.svg"),
      typeColor: '#85C1E9',
      // special
      algorithm: 0, // 算法
    }
  },
  {
    type:"subsystem-node",
    text:"子系统",
    properties: {
      // common
      ...common,
      icon: require("@/assets/images/delay.svg"),
      typeColor: '#85C1E9',

        tableName: "子系统",
        fields: {
          input: 0,
          output: 0
        }

    }
  },
  {
    type:"input-node",
    text:"输入",
    properties: {
      // common
      ...common,
      icon: require("@/assets/images/delay.svg"),
      typeColor: '#85C1E9',
      // special
      index: 1, // 输入序号

    }
  },{
    type:"output-node",
    text:"输出",
    properties: {
      // common
      ...common,
      icon: require("@/assets/images/delay.svg"),
      typeColor: '#85C1E9',
      // special
      index:1,
    }
  }
]

export { nodeList }
