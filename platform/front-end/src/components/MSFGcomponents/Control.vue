<template>
  <div>
    <el-button-group>
      <!-- <el-button type="plain" size="small" @click="$_test">测试用</el-button> -->
      <el-button v-if="controlConfig.zoomIn" type="plain" size="small" @click="$_zoomIn">放大</el-button>
      <el-button v-if="controlConfig.zoomOut" type="plain" size="small" @click="$_zoomOut">缩小</el-button>
      <el-button v-if="controlConfig.zoomReset" type="plain" size="small" @click="$_zoomReset">大小适应</el-button>
      <el-button v-if="controlConfig.translateRest" type="plain" size="small" @click="$_translateRest">定位还原</el-button>
      <el-button v-if="controlConfig.reset" type="plain" size="small" @click="$_reset">还原(大小&定位)</el-button>
      <el-button v-if="controlConfig.undo" type="plain" size="small" @click="$_undo"
        :disabled="undoDisable">撤销(ctrl+z)</el-button>
      <el-button v-if="controlConfig.redo" type="plain" size="small" @click="$_redo"
        :disabled="redoDisable">重做(ctrl+y)</el-button>
      <el-button v-if="controlConfig.clear" type="plain" size="small" @click="$_clear">清空</el-button>
      <el-button v-if="controlConfig.reDraw" type="plain" size="small" @click="$_reDraw">重绘</el-button>
      <el-button v-if="controlConfig.exportData" type="plain" size="small"
        @click="exportData_dialogVisible = true">导出流图</el-button>
      <el-button v-if="controlConfig.importData" type="plain" size="small"
        @click="importData_dialogVisible = true">载入流图</el-button>
    </el-button-group>

    <el-upload v-if="controlConfig.importFMECA" style="display:inline-block; margin-left: -5px;" action=""
      :auto-upload="false"
      accept="application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
      :multiple="false" :show-file-list="false" :on-change="$_importFMECA">
      <el-button type="plain" size="small">载入FMECA</el-button>
    </el-upload>

    <el-upload v-if="controlConfig.importSimulink" style="display:inline-block; margin-left: -5px;" action=""
      :auto-upload="false" accept=".mdl" :multiple="false" :show-file-list="false" :on-change="$_importSimulink">
      <el-button type="plain" size="small">载入Simulink</el-button>
    </el-upload>

    <el-button v-if="controlConfig.check" type="plain" size="small" @click="$_check"
      style="display:inline-block; margin-left: -5px;">流图评价</el-button>

    <el-button v-if="controlConfig.optimizeCkpt" type="plain" size="small" @click="$_optimizeCkpt"
      style="display:inline-block; margin-left: -5px;">测点优化</el-button>

    <el-upload v-if="controlConfig.analyse" style="display:inline-block; margin-left: -5px;" action=""
      :auto-upload="false" accept=".csv" :multiple="false" :show-file-list="false" :on-change="$_analyse">
      <el-button type="plain" size="small">故障分析</el-button>
    </el-upload>

    <el-dialog width="60%" :title="'流图载入方式'" :visible.sync="importData_dialogVisible" :modal="false">

      <div style="display:flex;flex-direction:column;justify-content:space-between;align-items:center;gap:10px">

        <el-button type="plain" @click="$_importData_global">载入全局数据</el-button>

        <el-button type="plain" @click="$_importData_part_incremental">载入局部数据（增量式）</el-button>

        <el-button type="primary" @click="importData_dialogVisible = false">关 闭</el-button>
      </div>
    </el-dialog>

    <el-dialog width="60%" :title="'流图导出方式'" :visible.sync="exportData_dialogVisible" :modal="false">
      <div style="display:flex;flex-direction:column;justify-content:space-between;align-items:center;gap:10px">
        <el-button type="primary" @click="$_exportData('global')">导出全局数据</el-button>
        <el-button type="primary" @click="$_exportData('part')">导出局部数据</el-button>
        <el-button type="primary" @click="exportData_dialogVisible = false">关 闭</el-button>
      </div>
    </el-dialog>

    <el-dialog width="60%" :title="dialogTitle" :visible.sync="Visible" :modal="false">
      <el-descriptions title="性能指标" :column="3" border v-if="dialogType === 'check'">
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
      <el-table :data="result.D_mat" size="mini" v-if="dialogType === 'check'" border>
        <el-table-column v-for="k in result.col_names" :label="k === 'row_name' ? '' : k" :key="k" :prop="k">
          <template slot-scope="scope">
            <span v-if="scope.row[k] === 1" style="background-color: red; color: white;">{{ scope.row[k] }}</span>
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
    lf: Object || String,
    G_DATA: Object
  },
  data() {
    return {
      controlConfig,
      undoDisable: true,
      redoDisable: true,
      a: document.createElement('a'),
      fileName: 'data',
      jsonText: '',
      reader: null,
      importData_dialogVisible: false,
      exportData_dialogVisible: false,
      Visible: false,
      dialogType: 'check',
      result: {
        detect_isolat_ratio: [1, 1, 1, 1],
        col_names: []
      },
    }
  },
  computed: {
    dialogTitle() {
      if (this.dialogType === 'check') {
        return '信号流图模型评价'
      } else {
        return '信号流图模型评价'
      }
    }
  },
  mounted() {
    this.$props.lf.on('history:change', ({ data: { undoAble, redoAble } }) => {
      this.$data.undoDisable = !undoAble
      this.$data.redoDisable = !redoAble
    })
  },
  methods: {
    $_zoomIn() {
      this.$props.lf.zoom(true)
    },
    $_zoomOut() {
      this.$props.lf.zoom(false)
    },
    $_zoomReset() {
      this.$props.lf.resetZoom()
    },
    $_translateRest() {
      this.$props.lf.resetTranslate()
    },
    $_reset() {
      this.$props.lf.resetZoom()
      this.$props.lf.resetTranslate()
    },
    $_undo() {
      this.$props.lf.undo()
    },
    $_redo() {
      this.$props.lf.redo()
    },
    $_clear() {
      this.$props.lf.clearData()
    },
    $_reDraw() {
      let data = this.$props.lf.getGraphRawData()
      data.nodes.forEach((node) => {
        node.properties.showType = 'edit'
      })
      this.$props.lf.render(data)
    },
    $_exportData(type) {

      if (type === 'global') {
        // 全局导出
        let data = this.$props.G_DATA
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
            this.a.href = window.URL.createObjectURL(new Blob([this.jsonText], { type: 'text/json' }))
            this.a.dispatchEvent(new MouseEvent('click'))
          }
        })
      } else if (type === 'part') {
        // 局部导出
        function deepClone(obj) {
          let _obj = JSON.stringify(obj),
            objClone = JSON.parse(_obj);
          return objClone
        }

        let data = {
          currentSystemId: deepClone(this.$props.G_DATA.currentSystemId),
          SystemData: []
        }

        // 1.获取当前系统的数据
        let currentSystemData_copy = deepClone(this.$props.G_DATA.SystemData.find(item => item.system_id == data.currentSystemId))
        // 当前系统变为root系统
        currentSystemData_copy.parent_id = null
        // 2. 删除一切输入和输出节点 以及相关的边
        let inputORoutput_nodes = currentSystemData_copy.data.nodes.filter(item => item.type == 'input-node' || item.type == 'output-node')
        // 2.1 删除所有的相关边与节点
        for (let node of inputORoutput_nodes) {

          let edges = currentSystemData_copy.data.edges.filter(item => item.sourceNodeId == node.id || item.targetNodeId == node.id)
          for (let edge of edges) {
            currentSystemData_copy.data.edges.splice(currentSystemData_copy.data.edges.indexOf(edge), 1)
          }
          currentSystemData_copy.data.nodes.splice(currentSystemData_copy.data.nodes.indexOf(node), 1)
        }
        data.SystemData.push(currentSystemData_copy)

        // 3. 递归获取当前系统的所有子系统的数据
        /**
         * 递归获取当前系统的所有子系统的数据
         * @param {number} system_id  当前系统的id
         * @param {object} G_SyatemData 全局数据
         * @param {object} data 需要改变的对象
         */
        function getChildrenSystemData(system_id, G_SystemData, data) {

          let childrenSystems = deepClone(G_SystemData.filter(item => item.parent_id == system_id))
          if (childrenSystems.length > 0) {
            for (let child of childrenSystems) {
              data.SystemData.push(child)
              getChildrenSystemData(child.system_id, G_SystemData, data)
            }
          }
        }
        getChildrenSystemData(data.currentSystemId, this.$props.G_DATA.SystemData, data)

        // 1.
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
            this.a.href = window.URL.createObjectURL(new Blob([this.jsonText], { type: 'text/json' }))
            this.a.dispatchEvent(new MouseEvent('click'))
          }
        })
      }
    },

    /**
     * 导入数据
     * @param {'global' | 'part_incremental'} mode 导入模式
     */
    $_importData(mode) {
      const input = document.createElement('input');
      input.type = 'file';
      input.accept = '.json';
      input.onchange = () => {
        const file = input.files && input.files[0];
        if (file) {
          const reader = new FileReader();
          reader.onerror = (error) => {
            this.$message.error('读取流图文件解析失败');
          }
          reader.onload = () => {
            const json = reader.result;
            try {
              const data = JSON.parse(json);
              this.$emit("updata-import-data", {
                type: mode,
                value: data
              });
            } catch (e) {
              this.$message.error('读取流图文件解析失败');
            }
          };
          reader.readAsText(file);
          this.importData_dialogVisible = false;
        }
      };
      input.click();
    },

    $_importData_global() {
      this.$_importData('global');
    },

    $_importData_part_incremental() {
      this.$_importData('part_incremental');
    },
    
    $_importFMECA(file) {
      let fd = new FormData()
      fd.append('modelFile', file.raw)
      this.$axios({
        url: '/multi-info-edit/upload-fmeca/',
        method: 'post',
        data: fd
      }).then((res) => {
        (res)
        this.$emit("updata-import-data", {
            type: 'global',
            value: {
              SystemData: res.data,
              currentSystemId: 0
            }
          })
        // this.$props.lf.render(importStruct(res.data))
        //this.Visible = true
      })
    },
    $_importSimulink(file) {
      let fd = new FormData()
      fd.append('modelFile', file.raw)
      this.$axios({
        url: '/multi-info-edit/upload-simulink/',
        method: 'post',
        data: fd
      }).then((res) => {
        (res)
        this.$emit("updata-import-data", {
          type: 'global',
          value: res.data
        })
        // this.$props.lf.render(importStruct(res.data))
        //this.Visible = true
      })
    },
    $_optimizeCkpt() {
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
          (res)
          this.$props.lf.render(importStruct(res.data))
          //this.Visible = true
        })
      }
    },

    $_check() {
      let data = this.$props.G_DATA.SystemData

      if (this.$props.lf.getGraphData().nodes.length === 0) {
        this.$alert('流图为空')
      } else {
        let fd = new FormData()
        fd.append('graphStruct', JSON.stringify(data))
        this.$axios({
          url: '/multi-info-edit/check-graph/',
          method: 'post',
          data: fd
        }).then((res) => {
          this.dialogType = 'check'
          this.result.detect_isolat_ratio = res.detect_isolat_ratio
          res.col_names.forEach((colName, index) => {
            if (colName != 'row_name') {
              res.col_names[index] = index+":"+colName
            }
          })
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
          // this.$emit("updata-import-data", {
          //   type: 'global',
          //   value: {
          //     SystemData: res.data,
          //     currentSystemId: this.$props.G_DATA.currentSystemId
          //   }
          // })

          this.Visible = true;
          //this.$forceUpdate();
        })
      }
    },
    $_analyse(file) {
      let data = this.$props.G_DATA.SystemData
      let fd = new FormData()
      fd.append('graphStruct', JSON.stringify(data))
      fd.append('dataFile', file.raw)
      this.$axios({
        url: '/multi-info-analyse/analyse-data/',
        method: 'post',
        data: fd
      }).then((res) => {
        this.dialogType = 'analyse'
        // this.Visible = true
        this.$emit("updata-import-data", {
          type: 'global',
          value: {
            SystemData: res.data,
            currentSystemId: this.$props.G_DATA.currentSystemId
          }
        })

      })
    },
    $_test() {

    },
  }
}
</script>

<style scoped></style>
