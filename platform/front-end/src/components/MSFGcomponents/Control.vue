<template>
  <div>
     <el-button-group>
      <!-- <el-button type="plain" size="small" @click="$_test">测试用</el-button> -->
      <el-button
        v-if="controlConfig.zoomIn"
        type="plain" size="small" @click="$_zoomIn">放大</el-button>
      <el-button
        v-if="controlConfig.zoomOut"
        type="plain" size="small" @click="$_zoomOut">缩小</el-button>
      <el-button
        v-if="controlConfig.zoomReset"
        type="plain" size="small" @click="$_zoomReset">大小适应</el-button>
      <el-button
        v-if="controlConfig.translateRest"
        type="plain" size="small" @click="$_translateRest">定位还原</el-button>
      <el-button
        v-if="controlConfig.reset"
        type="plain" size="small" @click="$_reset">还原(大小&定位)</el-button>
      <el-button
        v-if="controlConfig.undo"
        type="plain" size="small" @click="$_undo" :disabled="undoDisable">撤销(ctrl+z)</el-button>
      <el-button
        v-if="controlConfig.redo"
        type="plain" size="small" @click="$_redo" :disabled="redoDisable">重做(ctrl+y)</el-button>
      <el-button
        v-if="controlConfig.clear"
        type="plain" size="small" @click="$_clear">清空</el-button>
      <el-button
        v-if="controlConfig.reDraw"
        type="plain" size="small" @click="$_reDraw">重绘</el-button>
      <el-button
        v-if="controlConfig.exportData"
        type="plain" size="small" @click="$_exportData">导出流图</el-button>
    </el-button-group>

    <el-upload
      v-if="controlConfig.importData"
      style="display:inline-block; margin-left: -5px;"
      action=""
      :auto-upload="false"
      accept=".json"
      :multiple="false"
      :show-file-list="false"
      :on-change="$_importData">
      <el-button type="plain" size="small">载入流图</el-button>
    </el-upload>

    <el-upload
      v-if="controlConfig.importFMECA"
      style="display:inline-block; margin-left: -5px;"
      action=""
      :auto-upload="false"
      accept="application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
      :multiple="false"
      :show-file-list="false"
      :on-change="$_importFMECA">
      <el-button type="plain" size="small">载入FMECA</el-button>
    </el-upload>

    <el-button
        v-if="controlConfig.check"
        type="plain" size="small" @click="$_check"
        style="display:inline-block; margin-left: -5px;">流图评价</el-button>

    <el-button
      v-if="controlConfig.optimizeCkpt"
      type="plain" size="small" @click="$_optimizeCkpt"
      style="display:inline-block; margin-left: -5px;">测点优化</el-button>

    <el-upload
      v-if="controlConfig.analyse"
      style="display:inline-block; margin-left: -5px;"
      action=""
      :auto-upload="false"
      accept=".csv"
      :multiple="false"
      :show-file-list="false"
      :on-change="$_analyse">
      <el-button type="plain" size="small">故障分析</el-button>
    </el-upload>

    <el-dialog width="60%" :title="dialogTitle" :visible.sync="Visible" :modal="false">
      <el-descriptions title="性能指标" :column="3" border v-if="dialogType==='check'">
        <el-descriptions-item label="检出率">
          <span>{{ result.detect_isolat_ratio[0] }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="隔离率">
          <span>{{ result.detect_isolat_ratio[1] }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="冗余度">
          <span>{{ result.detect_isolat_ratio[2] }}</span>
        </el-descriptions-item>
      </el-descriptions>
      <el-table
        :data="result.D_mat"
        size="mini"
        v-if="dialogType==='check'"
        border>
        <el-table-column
          v-for="k in result.col_names"
          :label="k ==='row_name'? '' : k"
          :key="k"
          :prop="k">
          <template slot-scope="scope">
            <span v-if="scope.row[k]===1" style="background-color: red; color: white;">{{ scope.row[k] }}</span>
            <span v-else>{{ scope.row[k] }}</span>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script>
import { importStruct, exportStruct } from '../logicflowConfig/common/methods'
import { controlConfig } from '../logicflowConfig/tools/menu'

export default {
  name: 'Control',
  props: {
    lf: Object || String
  },
  data () {
    return {
      controlConfig,
      undoDisable: true,
      redoDisable: true,
      a: document.createElement('a'),
      fileName: 'data',
      jsonText: '',
      reader: null,
      Visible: false,
      dialogType: 'check',
      result: {
        detect_isolat_ratio: [1, 1, 1, 1],
        col_names: []
      },
    }
  },
  computed: {
    dialogTitle () {
      if (this.dialogType === 'check') {
        return '信号流图模型评价'
      } else {
        return '信号流图模型评价'
      }
    }
  },
  mounted () {
    this.$props.lf.on('history:change', ({ data: { undoAble, redoAble } }) => {
      this.$data.undoDisable = !undoAble
      this.$data.redoDisable = !redoAble
    })
  },
  methods: {
    $_zoomIn () {
      this.$props.lf.zoom(true)
    },
    $_zoomOut () {
      this.$props.lf.zoom(false)
    },
    $_zoomReset () {
      this.$props.lf.resetZoom()
    },
    $_translateRest () {
      this.$props.lf.resetTranslate()
    },
    $_reset () {
      this.$props.lf.resetZoom()
      this.$props.lf.resetTranslate()
    },
    $_undo () {
      this.$props.lf.undo()
    },
    $_redo () {
      this.$props.lf.redo()
    },
    $_clear () {
      this.$props.lf.clearData()
    },
    $_reDraw () {
      let data = this.$props.lf.getGraphRawData()
      data.nodes.forEach((node) => {
        node.properties.showType = 'edit'
      })
      this.$props.lf.render(data)
    },
    $_exportData () {
      let data = exportStruct(this.$props.lf.getGraphData())
      this.$Modal.confirm({
          render: (h) => {
            return h('Input', {
              props: {
                value: this.fileName,
                placeholder: '请输入文件名',
                autofocus: true
              },
              on: {
                input: (val) => {
                  this.fileName = val
                }
              }
            })
          },
          onOk: () => {
            this.jsonText = JSON.stringify(data, null, 4)
            this.a.download = this.fileName + '.json'
            this.a.href = window.URL.createObjectURL(new Blob([this.jsonText], {type: 'text/json' }))
            this.a.dispatchEvent(new MouseEvent('click'))
          }
        })
    },
    $_importData (file) {
      return new Promise((resolve, reject) => {
        // 检验是否支持 FileRender
        if (typeof FileReader === 'undefined') {
          reject('当前浏览器不支持FileReader')
        }
        // 执行读取json数据操作
        this.reader = new FileReader()
        this.reader.readAsText(file.raw)
        this.reader.onerror = (error) => {
          reject('读取流图文件解析失败', error)
        }
        this.reader.onload = () => {
          if (this.reader.result) {
            try {
              resolve(JSON.parse(this.reader.result))
            } catch (error) {
              reject('读取流图文件解析失败', error)
            }
          } else {
            reject('读取流图文件解析失败', error)
          }
        }
      }).then((res) => {
        console.log(res)
        let data = importStruct(res)
        this.$props.lf.render(data)
      })
    },

    $_importFMECA (file) {
      let fd = new FormData()
      fd.append('modelFile', file.raw)
      this.$axios({
        url: '/multi-info-edit/upload-fmeca/',
        method: 'post',
        data: fd
      }).then((res) => {
        console.log(res)
        this.$props.lf.render(importStruct(res.data))
        //this.Visible = true
      })
    },

    $_optimizeCkpt () {
      let data = this.$props.lf.getGraphData()
      if (data.nodes.length === 0) {
        this.$alert('流图为空')
      } else {
        let fd = new FormData()
        fd.append('graphStruct', JSON.stringify(exportStruct(data)))
        this.$axios({
          url: '/multi-info-edit/optimize-graph/',
          method: 'post',
          data: fd
        }).then((res) => {
          console.log(res)
          this.$props.lf.render(importStruct(res.data))
          //this.Visible = true
        })
      }
    },

    $_check () {
      let data = this.$props.lf.getGraphData()
      if (data.nodes.length === 0) {
        this.$alert('流图为空')
      } else {
        let fd = new FormData()
        fd.append('graphStruct', JSON.stringify(exportStruct(data)))
        this.$axios({
          url: '/multi-info-edit/check-graph/',
          method: 'post',
          data: fd
        }).then((res) => {
          console.log(res)
          this.dialogType = 'check'
          this.result.detect_isolat_ratio = res.detect_isolat_ratio
          this.result.col_names = ['row_name', ...res.col_names]
          let D_mat = []
          res.row_names.forEach((rowName, index) => {
            let map = { row_name: rowName }
            res.D_mat[index].forEach((val, i) => {
              map[res.col_names[i]] = val
            })
            D_mat.push(map)
          })
          this.result.D_mat = D_mat
          this.$props.lf.render(importStruct(res.data, 'check'))
          this.Visible = true;
          //this.$forceUpdate();
        })
      }
    },
    $_analyse (file) {
      let fd = new FormData()
      fd.append('graphStruct', JSON.stringify(exportStruct(this.$props.lf.getGraphData())))
      fd.append('dataFile', file.raw)
      this.$axios({
        url: '/multi-info-analyse/analyse-data/',
        method: 'post',
        data: fd
      }).then((res) => {
        this.dialogType = 'analyse'
        // this.Visible = true
        this.$props.lf.render(importStruct(res.data, 'analyse'))
      })
    },
    $_test () {

    },
  }
}
</script>

<style scoped>
</style>
