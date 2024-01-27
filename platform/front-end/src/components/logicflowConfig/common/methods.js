import { sankey } from "d3-sankey"

const WIDTH = 100
const HEIGHT = 30
const PADDING = 100

function getuuid(index) {
  if (!index) {
    index = 0
  }
  return index.toString(16) + "-" + Date.now().toString(16)
}

function getScale(nodes_pure, idMap_pure, nodes, idMap, k, maxDepth, maxHeight, w) {
  if (nodes[k].type != "sub-system") {
    let j = idMap_pure.indexOf(nodes[k].id)
    return [
      Math.round(Math.max((nodes_pure[j].depth / maxDepth) * w * 0.8, nodes_pure[j].depth * (PADDING + WIDTH)) - WIDTH / 2),
      Math.round(Math.max((nodes_pure[j].depth / maxDepth) * w * 0.8, nodes_pure[j].depth * (PADDING + WIDTH)) + WIDTH / 2),
      Math.round(Math.max((nodes_pure[j].height / maxHeight) * w * 0.4, nodes_pure[j].height * (PADDING + HEIGHT)) - HEIGHT / 2),
      Math.round(Math.max((nodes_pure[j].height / maxHeight) * w * 0.4, nodes_pure[j].height * (PADDING + HEIGHT)) + HEIGHT / 2)
    ]
  } else {
    let allScale = nodes[k].children.map(itm => { return getScale(nodes_pure, idMap_pure, nodes, idMap, idMap.indexOf(itm), maxDepth, w) })
    return [
      Math.min(...allScale.map(itm => itm[0])) - PADDING,
      Math.max(...allScale.map(itm => itm[1])) + PADDING,
      Math.min(...allScale.map(itm => itm[2])) - PADDING,
      Math.max(...allScale.map(itm => itm[3])) + PADDING
    ]
  }
}

function autoArrange(graphStruct, h, w) {
  let nodes_pure = graphStruct.nodes.filter(itm => { return itm.type !== "sub-system" })
  let nodes_ = nodes_pure.map(itm => { return { id: itm.id } })
  let idMap_pure = nodes_pure.map(itm => itm.id)
  let edgeStock = nodes_pure.map((itm, k) => [k]);
  let edges_ = [];
  graphStruct.edges.forEach(itm => {
    let sId = idMap_pure.indexOf(itm.sourceNodeId);
    let tId = idMap_pure.indexOf(itm.targetNodeId);
    if (!(edgeStock[tId].includes(sId))) {
      edgeStock[sId].push(tId);
      edgeStock[tId].forEach(inId => {
        edgeStock[sId].push(inId);
      })
      edges_.push({ source: sId, target: tId })
    }
  })
  nodes_.push({ id: "useless-root" })
  edgeStock.forEach((itm, k) => {
    if (itm.length == 1) {
      edges_.push({ source: nodes_.length - 1, target: k })
    }
  })
  /**
  let edges_ = graphStruct.edges.map(itm => {
    return {
      source: idMap_pure.indexOf(itm.sourceNodeId), 
      target: idMap_pure.indexOf(itm.targetNodeId)
      }
    })
  **/
  let nodes = sankey().nodeWidth(WIDTH).nodePadding(3).size([h, w]).nodes(nodes_).links(edges_)().nodes
  var maxDepth = Math.max(1, ...nodes.map(itm => itm.depth)) - 1
  var maxHeight = Math.max(1, ...nodes.map(itm => itm.height))
  let idMap = graphStruct.nodes.map(itm => itm.id)
  graphStruct.nodes.forEach((itm, k) => {
    if (itm.type !== "sub-system") {
      graphStruct.nodes[k].x = Math.round(Math.max((nodes[k].depth / maxDepth) * w * 0.8), nodes[k].depth * (PADDING + WIDTH))
      graphStruct.nodes[k].y = Math.round(Math.max((nodes[k].height / maxHeight) * w * 0.4), nodes[k].height * (PADDING + HEIGHT))
      graphStruct.nodes[k].text.x = Math.round(graphStruct.nodes[k].x + WIDTH / 2)
      graphStruct.nodes[k].text.y = Math.round(graphStruct.nodes[k].y)
    } else {
      let recScale = getScale(nodes, idMap_pure, graphStruct.nodes, idMap, k, maxDepth, maxHeight, w)
      graphStruct.nodes[k].x = Math.round((recScale[0] + recScale[1]) / 2)
      graphStruct.nodes[k].y = Math.round((recScale[2] + recScale[3]) / 2)
      graphStruct.nodes[k].properties.nodeSize.width = recScale[1] - recScale[0]
      graphStruct.nodes[k].properties.nodeSize.height = recScale[3] - recScale[2]
    }
  })
  graphStruct.edges.forEach((itm, k) => {
    let Sindex = idMap.indexOf(graphStruct.edges[k].sourceNodeId)
    let Eindex = idMap.indexOf(graphStruct.edges[k].targetNodeId)
    if (graphStruct.nodes[Sindex].type == "switch-node") {
      graphStruct.edges[k].startPoint = {
        x: graphStruct.nodes[Sindex].x + WIDTH / 2,
        y: graphStruct.nodes[Sindex].y
      }
      graphStruct.edges[k].endPoint = { x: graphStruct.nodes[Eindex].x, y: null }
      if (graphStruct.nodes[Sindex].y > graphStruct.edges[k].endPoint.y) {
        graphStruct.edges[k].endPoint.y = graphStruct.nodes[Eindex].y + HEIGHT / 2
      } else {
        graphStruct.edges[k].endPoint.y = graphStruct.nodes[Eindex].y - HEIGHT / 2
      }
      graphStruct.edges[k].pointsList = []
    } else {
      graphStruct.edges[k].startPoint = {}
      graphStruct.edges[k].endPoint = {}
      graphStruct.edges[k].startPoint = {
        x: graphStruct.nodes[Sindex].x + WIDTH / 2,
        y: graphStruct.nodes[Sindex].y
      }
      graphStruct.edges[k].endPoint = {
        x: graphStruct.nodes[Eindex].x - WIDTH / 2,
        y: graphStruct.nodes[Eindex].y
      }
      graphStruct.edges[k].pointsList = []
    }
    graphStruct.edges[k].type = "custom-edge";
  })
  console.log(graphStruct)
  return graphStruct
}

function exportStruct(graphStruct) {
  let nodeList = []
  let linkList = []
  let idMap = {}

  graphStruct.nodes.forEach(itm => {
    idMap[itm.id] = itm.text.value
  })

  graphStruct.nodes.forEach(itm => {
    let node = {
      text: itm.text.value,
      type: itm.type,
      showConfig: {
        position: { x: itm.x, y: itm.y },
        properties: itm.properties,
      }
    }

    if (itm.type == "switch-node") {
      node.control = idMap[itm.properties.control]
      node.switchType = itm.properties.normalState ? "常闭" : "常开"
    } else if (itm.type == "sub-system") {
      node.children = itm.children.map(itm_ => { return idMap[itm_] })
    } else {

    }
    nodeList.push(node)
  })

  graphStruct.edges.forEach(itm => {
    linkList.push({
      id: itm.id,
      from: idMap[itm.sourceNodeId],
      to: idMap[itm.targetNodeId],
      type: itm.type,
      showConfig: {
        startAnchor: itm.startPoint,
        endAnchor: itm.endPoint,
        interAnchors: itm.pointsList,
        properties: itm.properties,
      },
    })
  })
  return {
    nodes: nodeList,
    edges: linkList
  }
}

function importStruct(graphStruct, showType = 'edit', h = 900, w = 1200) {
  let nodeList = []
  let linkList = []
  let idMap = []
  let count = 0
  let autopos = false

  graphStruct.nodes.forEach(itm => {
    count += 1
    idMap[itm.text] = getuuid(count * 2)
  })

  graphStruct.nodes.forEach(itm => {
    if (
      itm.showConfig === null || typeof itm.showConfig === "undefined" ||
      itm.showConfig.position === null || typeof itm.showConfig.position === "undefined" ||
      itm.showConfig.position.x === null || typeof itm.showConfig.position.x === "undefined" ||
      itm.showConfig.position.y === null || typeof itm.showConfig.position.y === "undefined"
    ) {
      autopos = true
      itm.showConfig = {
        position: {
          x: null,
          y: null
        },
        properties: {
          showType: null,
          collision: false,
          detectable: true,
          fuzzible: false,
          fuzzy_state: 0,
          state: 0,
          width: 100,
          icon: "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAsIDAsIDQwLCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBjb2xvcj0iIzAwMCIgdHJhbnNmb3JtPSJ0cmFuc2xhdGUoLTU0MCAtOTg3LjM2KSI+PHBhdGggZD0iTTU2NS40MyAxMDAxLjljNi41NjIgMi4wODkgMTEuMzE2IDguMjMzIDExLjMxNiAxNS40ODggMCA4Ljk3NS03LjI3NSAxNi4yNS0xNi4yNSAxNi4yNXMtMTYuMjUtNy4yNzUtMTYuMjUtMTYuMjVjMC0yLjgwMi43MS01LjQzOCAxLjk1OC03Ljc0IiBmaWxsPSJub25lIiBzdHJva2U9IiNmZmYiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIgc3Ryb2tlLXdpZHRoPSIzIiBzdHlsZT0iaXNvbGF0aW9uOmF1dG87bWl4LWJsZW5kLW1vZGU6bm9ybWFsIi8+PGNpcmNsZSBjeD0iNTYwIiBjeT0iMTAwMS40IiByPSIxLjUiIGZpbGw9Im5vbmUiIHN0cm9rZT0iI2ZmZiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIiBzdHJva2Utd2lkdGg9IjMiIHN0eWxlPSJpc29sYXRpb246YXV0bzttaXgtYmxlbmQtbW9kZTpub3JtYWwiLz48cGF0aCBkPSJNNTYwIDEwMTQuNGMtMS4yMDYgMC0xMS0xMC45OTktMTIuMzU0LTkuOTc1UzU1NyAxMDE2LjE0OCA1NTcgMTAxNy40czEuMzYgMyAzIDMgMy0xLjM2MSAzLTMtMS43OTQtMy0zLTN6IiBmaWxsPSIjZmZmIi8+PC9nPjwvc3ZnPgo=",
          typeColor: itm.type === "test-node" ? "#eea2a4" : "#edc3ae",
          ui: "node-red"
        }
      }
    }
    let node = {
      id: idMap[itm.text],
      text: {
        value: itm.text,
        x: itm.showConfig.position.x + WIDTH / 2,
        y: itm.showConfig.position.y,
      },
      type: itm.type,
      x: itm.showConfig.position.x,
      y: itm.showConfig.position.y,
      properties: itm.showConfig.properties,
    }
    // show type config
    node.properties.showType = showType
    if (showType === 'check') {
      node.properties.collision = itm.collision
      node.properties.fuzzible = itm.fuzzible
      node.properties.detectable = itm.detectable
    } else if (showType === 'analyse') {
      node.properties.state = itm.state
      node.properties.fuzzy_state = itm.fuzzy_state
    }
    // special properties
    if (itm.type == "switch-node") {
      node.properties.control = idMap[itm.control]
      node.properties.normalState = itm.switchType.includes("闭")
    } else if (itm.type == "sub-system") {
      node.children = itm.children.map(itm_ => { return idMap[itm_] })
    }
    nodeList.push(node)
  })
  graphStruct.edges.forEach(itm => {
    count += 1
    if (itm.showConfig === null || typeof itm.showConfig === "undefined") {
      itm.showConfig = { startAnchor: null, endAnchor: null, interAnchors: [], properties: {} }
    }
    linkList.push({
      id: idMap[itm.from] + "-" + idMap[itm.to] + "-" + getuuid(count * 2 + 1),
      sourceNodeId: idMap[itm.from],
      targetNodeId: idMap[itm.to],
      type: itm.type,
      startPoint: itm.showConfig.startAnchor,
      endPoint: itm.showConfig.endAnchor,
      pointsList: itm.showConfig.interAnchors,
      properties: itm.showConfig.properties,
    })
  })

  let _graphStruct = {
    nodes: nodeList,
    edges: linkList
  }

  if (autopos) {
    _graphStruct = autoArrange(_graphStruct, h, w)
  }

  return _graphStruct
}
// function renderNodeColor

function getColorRGB_check(collision, fuzzible, detectable, typeColor) {
  if (collision) {
    return "rgb(255, 0, 0)"
  } else if (fuzzible) {
    return "rgb(0, 0, 255)"
  } else if (!detectable) {
    return "rgb(150, 150, 150)"
  } else {
    return typeColor //Replace by Type-Defined Color  
  }
}

function getColorRGB_analyse(state, fuzzy_state, fuzzy_ratio) {
  if (fuzzy_state == null) {
    fuzzy_state = 0
  }
  if (fuzzy_ratio == null) {
    fuzzy_ratio = 0.75
  }
  fuzzy_state *= fuzzy_ratio
  if (state == null) {
    return "rgb(150, 150, 150)"
  } else if (state < 0.5) {
    return 'rgb(' + parseInt((1 - fuzzy_state) * state * 255 + fuzzy_state * 128) + ","
      + parseInt((1 - fuzzy_state) * 255 + fuzzy_state * 128) + ","
      + parseInt(fuzzy_state * 128) + ")"
  } else {
    return 'rgb(' + parseInt((1 - fuzzy_state) * 255 + fuzzy_state * 128) + ","
      + parseInt((1 - fuzzy_state) * (1 - state) * 255 + fuzzy_state * 128) + ","
      + parseInt(fuzzy_state * 128) + ")"
  }
}

function getColorRGB_check_sub(collision, fuzzible, detectable, typeColor) {
  if (collision) {
    return "rgba(255, 0, 0, 0.45)"
  } else if (fuzzible) {
    return "rgba(0, 0, 255, 0.45)"
  } else if (!detectable) {
    return "rgba(150, 150, 150, 0.45)"
  } else {
    return typeColor //Replace by Type-Defined Color
  }
}

function getColorRGB_analyse_sub(state, fuzzy_state, fuzzy_ratio) {
  if (fuzzy_state == null) {
    fuzzy_state = 0
  }
  if (fuzzy_ratio == null) {
    fuzzy_ratio = 0.75
  }
  fuzzy_state *= fuzzy_ratio
  if (state == null) {
    return "rgba(150, 150, 150, 0.45)"
  } else if (state < 0.5) {
    return 'rgba(' + parseInt((1 - fuzzy_state) * state * 255 + fuzzy_state * 128) + ","
      + parseInt((1 - fuzzy_state) * 255 + fuzzy_state * 128) + ","
      + parseInt(fuzzy_state * 128) + ", 0.45)"
  } else {
    return 'rgba(' + parseInt((1 - fuzzy_state) * 255 + fuzzy_state * 128) + ","
      + parseInt((1 - fuzzy_state) * (1 - state) * 255 + fuzzy_state * 128) + ","
      + parseInt(fuzzy_state * 128) + ", 0.45)"
  }
}

function renderStructColor(struct, showType = 'check') {
  console.log("ate new struct",struct )
  //遍历struct
  

  for (let system of struct) {
    console.log("ate new struct",system)
    for (let node of system.data.nodes) {
      if (node.type === 'fault-node'||node.type === 'test-node') {
        if (showType === 'check') {
          node.properties.typeColor = getColorRGB_check(node.properties.collision, node.properties.fuzzible, node.properties.detectable, node.properties.typeColor)
          console.log("ate new color",node.properties.typeColor )
        
        } else if (showType === 'analyse') {
          node.properties.typeColor = getColorRGB_analyse(node.properties.state, node.properties.fuzzy_state)
          console.log("ate new color",node.properties.typeColor )
        
        }
      }
    }
  }
  return struct
}



function getBytesLength(word) {
  if (!word) {
    return 0
  }
  let totalLength = 0
  for (let i = 0; i < word.length; i++) {
    const c = word.charCodeAt(i)
    if ((word.match(/[A-Z]/))) {
      totalLength += 1.5
    } else if ((c >= 0x0001 && c <= 0x007e) || (c >= 0xff60 && c <= 0xff9f)) {
      totalLength += 1
    } else {
      totalLength += 1.8
    }
  }
  return totalLength
}

export {
  importStruct,
  exportStruct,
  getColorRGB_check,
  getColorRGB_analyse,
  getColorRGB_check_sub,
  getColorRGB_analyse_sub,
  getBytesLength,
  renderStructColor
}