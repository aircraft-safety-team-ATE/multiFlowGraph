//import { HtmlNode, HtmlNodeModel, h } from "@logicflow/core"

function toHexColor(color) {
  // 标准化颜色字符串
  color = color.trim().toLowerCase();

  // 短格式十六进制颜色码转换为长格式
  if (/^#[0-9a-f]{3}$/.test(color)) {
    color = color.split('').map(function (hex) {
      return hex === '#' ? hex : hex + hex;
    }).join('');
  }

  // 长格式十六进制颜色码，直接返回
  if (/^#[0-9a-f]{6}$/.test(color)) {
    return color.toUpperCase();
  }

  // RGB(A) 格式
  const rgbaMatch = color.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*[0-9.]+)?\)/);
  if (rgbaMatch) {
    const r = parseInt(rgbaMatch[1]);
    const g = parseInt(rgbaMatch[2]);
    const b = parseInt(rgbaMatch[3]);
    return "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1).toUpperCase();
  }

  // 如果无法识别颜色格式，返回 null 或默认颜色
  return null; // 或者可以选择返回一个默认的颜色值或错误信息
}

function changeTableColorBeforeBackground(rgbColor, container) {

  // 创建一个 <style> 元素
  const colorClass = rgbColor.replace('#', '');
  const style = document.createElement('style');
  // 设置 <style> 元素的类型
  style.type = 'text/css';
  // 构造 CSS 规则
  const cssRule = `.table-node.table-color-${colorClass}::before { background: ${rgbColor}; }`;
  console.log(cssRule)
  // 将 CSS 规则添加到 <style> 元素中
  if (style.styleSheet) {
    // 适用于 IE
    style.styleSheet.cssText = cssRule;
  } else {
    // 适用于 Chrome, Firefox 等
    style.appendChild(document.createTextNode(cssRule));
  }
  // 将 <style> 元素添加到 <head> 中，以应用样式
  container.appendChild(style);
}


class SubsystemNode extends HtmlNode {
  /**
   * 1.1.7版本后支持在view中重写锚点形状。
   * 重写锚点新增
   */
  getAnchorShape(anchorData) {
    const { x, y, type } = anchorData
    return h("rect", {
      x: x - 5,
      y: y - 5,
      width: 10,
      height: 10,
      className: `custom-anchor ${type === "left" ? "incomming-anchoranchor" : "outgoing-anchor"
        }`
    })
  }
  setHtml(rootEl) {
    rootEl.innerHTML = ""
    const {
      properties: { fields, tableName, typeColor }
    } = this.props.model
    rootEl.setAttribute("class", "table-container")
    const container = document.createElement("div")

    let rgbColor = ''
    // 如果不存在typeColor则默认为紫色
    if (!toHexColor(typeColor)) {
      rgbColor = toHexColor('#9673a6')
    } else {
      rgbColor = toHexColor(typeColor)
    }
    changeTableColorBeforeBackground(rgbColor, container)
    container.className = `table-node table-color-${rgbColor.replace('#', '')}`


    const tableNameElement = document.createElement("div")
    tableNameElement.innerText = tableName
    tableNameElement.className = "table-name"
    container.appendChild(tableNameElement)
    const fragment = document.createDocumentFragment()

    const max_length = fields.input > fields.output ? fields.input : fields.output
    for (let i = 0; i < max_length; i++) {
      const itemElement = document.createElement("div")
      itemElement.className = "table-feild"
      const itemInput = document.createElement("span")
      if (fields.input > i) {
        itemInput.innerText = "IN " + (i + 1)
      } else {
        itemInput.innerText = ' '
      }
      itemInput.className = "input-feild-type"
      const itemOutput = document.createElement("span")
      if (fields.output > i) {
        itemOutput.innerText = "OUT " + (i + 1)
      } else {
        itemOutput.innerText = ' '
      }

      itemOutput.className = "output-feild-type"
      itemElement.appendChild(itemInput)
      itemElement.appendChild(itemOutput)
      fragment.appendChild(itemElement)
    }
    container.appendChild(fragment)
    rootEl.appendChild(container)
  }
}


class SubsystemNodeModel extends HtmlNodeModel {
  getData() {
    // 记录数据时也将锚点id记录下来
    const data = super.getData()
    data.anchors = this.anchors
    return data;
  }
  getOutlineStyle() {
    const style = super.getOutlineStyle()
    style.stroke = "none"
    style.hover.stroke = "none"
    return style
  }
  // 如果不用修改锚地形状，可以重写颜色相关样式
  getAnchorStyle(anchorInfo) {
    const style = super.getAnchorStyle()
    if (anchorInfo.type === "left") {
      style.fill = "red"
      style.hover.fill = "transparent"
      style.hover.stroke = "transpanrent"
      style.className = "lf-hide-default"
    } else {
      style.fill = "green"
    }
    return style
  }
  setAttributes() {
    this.width = 200
    const {
      properties: { fields }
    } = this
    const max_length = fields.input > fields.output ? fields.input : fields.output
    this.height = 60 + max_length * 24
    const circleOnlyAsTarget = {
      message: "只允许从右边的锚点连出",
      validate: (sourceNode, targetNode, sourceAnchor, targetAnchor) => {
        return sourceAnchor.type === "right"
      }
    }
    this.sourceRules.push(circleOnlyAsTarget)
    this.targetRules.push({
      message: "只允许连接左边的锚点",
      validate: (sourceNode, targetNode, sourceAnchor, targetAnchor) => {
        return targetAnchor.type === "left"
      }
    })
  }
  getDefaultAnchor() {
    const {
      id,
      x,
      y,
      width,
      height,
      isHovered,
      isSelected,
      properties: { fields, isConnection }
    } = this
    const anchors = []
    // 如果是连出，就不显示左边的锚点
    // if (isConnection || !(isHovered || isSelected)) {
    for (var i = 0; i < fields.input; i++) {
      anchors.push({
        x: x - width / 2 + 10,
        y: y - height / 2 + 60 + i * 24,
        id: `${id}_${i}_left`,
        edgeAddable: false,
        type: "left"
      })
    }
    // }
    // if (!isConnection ) {
    for (var i = 0; i < fields.output; i++) {
      anchors.push({
        x: x - width / 2 + 190,
        y: y - height / 2 + 60 + i * 24,
        id: `${id}_${i}_right`,
        type: "right"
      })
    }
    // }
    return anchors
  }
}


export default {
  type: "subsystem-node",
  model: SubsystemNodeModel,
  view: SubsystemNode
}
