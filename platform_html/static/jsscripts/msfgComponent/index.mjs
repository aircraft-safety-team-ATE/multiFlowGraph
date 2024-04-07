/** Multi-Signal Flow Graph COMPONENTs **/
/** written by J.CHOU@ate-lab 2023-04-19**/
import { msfgMethods, nodePanelList, subsystemInit } from './msfgDetail/msfgMethods.mjs'
import { importStruct, exportStruct, renderStructColor } from './msfgDetail/common/methods.mjs'

function setDefault(val, val_default) {
	if (val === null || val === undefined) {
		return val_default;
	} else {
		return val;
	}
}

let nodePanel = Vue.component(
	'ate-comp-node-panel',
	{
		props: ["lf", "g-data"],
		template: `
			<div class="node-panel">
				<div class="red-ui-palette-node ui-draggable ui-draggable-handle" @mousedown="$_dragNode(item)"
					v-for="(item, index) in nodeList" :key="index" :style="{ backgroundColor: item.properties.typeColor }">
					<div class="red-ui-palette-label">{{ item.text }}</div>
					<div class="red-ui-palette-icon-container">
						<div class="red-ui-palette-icon" :style="{ backgroundImage: 'url('+ item.properties.icon + ')' }"></div>
					</div>
				</div>
			</div>
		`,
		data() {
			return {
				nodeList: nodePanelList,
			}
		},
		methods: {
			setDefault,
			$_dragNode(item) {

				if (item.type == 'subsystem-node') {
					// 1.创建新的的system
					let new_system = {
						system_id: this.$props.gData.SystemData.at(-1).system_id + 1,
						name: "子系统" + (this.$props.gData.SystemData.at(-1).system_id + 1),
						parent_id: this.$props.gData.currentSystemId,
						data: {}
					}

					// 3. 更新gData
					this.$emit("updata-g-data", new_system)
					let properties = {
						tableName: "",
						SubsystemId: new_system.system_id,
						fields: {
							input: 0,
							output: 0
						}
					}

					this.$props.lf.dnd.startDrag({
						text: "子系统" + new_system.system_id,
						type: item.type,
						properties: properties
					})

				} else if (item.type == 'input-node') {
					// 禁止在根系统中创建输入或者输出节点
					let current_system = this.$props.gData.SystemData.find(item => item.system_id == this.$props.gData.currentSystemId)
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
						system_id: this.$props.gData.currentSystemId,
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
					let current_system = this.$props.gData.SystemData.find(item => item.system_id == this.$props.gData.currentSystemId)
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
						system_id: this.$props.gData.currentSystemId,
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
			},
		}
	})
let editDialog = Vue.component(
	'ate-comp-edit-dialog',
	{
		props: ["dialogVisible", "form-data"],
		template: `
			<el-dialog title="编辑节点属性" width="60%" :visible.sync="dialogVisible"
					:before-close="closeDialog" @open="openDialog">

				<el-form :model="form" :rules="rules" ref="NodePanelDialogForm" v-if="form">
					<!-- 共通 -->
					<el-form-item label="ID" label-width='120px'>
						<el-input v-model="form.id" :disabled="true"></el-input>
					</el-form-item>
					<el-form-item label="类型" label-width='120px'>
						<el-input v-model="form.type" :disabled="true"></el-input>
					</el-form-item>
					<el-form-item label="名称" label-width='120px'>
						<el-input v-model="form.text.value"></el-input>
					</el-form-item>
					<!-- fault-node -->
					<el-form-item v-if="form.type === 'fault-node'" label="故障等级"
						:label-width="'120px'" style="text-align: left;">
						<el-select v-model="form.properties.flevel" placeholder="请选择故障等级" clearable>
							<el-option v-for="level in faultLevelList" :key="level.value" :label="level.text"
								:value="level.value">
							</el-option>
						</el-select>
					</el-form-item>
					<!-- switch-node -->
					<el-form-item v-if="form.type === 'switch-node'" label="常闭/常开"
						label-width='120px' style="text-align: left;">
						<el-switch v-model="form.properties.normalState"
							active-color="#13ce66" inactive-color="#ff4949">
						</el-switch>
					</el-form-item>
				</el-form>

				<span slot="footer" class="dialog-footer">
					<el-button @click="closeDialog">取 消</el-button>
					<el-button type="primary" @click="formDataUpdate">确 定</el-button>
				</span>
			</el-dialog>
		`,
		data() {
			return {
				form: {
					id: "elpsycongoroo",
					text: {
						value: ''
					},
					properties: {
						normalState: true,
						flevel: 0
					}
				},
				rules: {
					'text.value': [{ required: true, message: '请输入节点名称', trigger: 'blur' }],
					'properties.flevel': [{ required: true, message: '请选择故障等级', trigger: 'change' }],
					'properties.algorithm': [{ required: true, message: '请选择算法', trigger: 'change' }],
				},
				faultLevelList: [
					{
						value: 0,
						text: '中间事件'
					}, {
						value: 1,
						text: '轻微故障'
					}, {
						value: 2,
						text: '一般故障'
					}, {
						value: 3,
						text: '严重故障'
					},
				],
			}
		},
		methods: {
			setDefault,
			formDataUpdate() {
				this.$refs['NodePanelDialogForm'].validate((valid, errs) => {
					if (valid) {
						this.$emit('data-update', this.form);
						this.closeDialog();
					};
				});
			},
			closeDialog() {
				this.$emit('update:dialogVisible', false);
			},
			openDialog() {
				this.form = { ...this.formData };
			},
		}
	});
let controlPanel = Vue.component(
	'ate-comp-control-panel',
	{
		props: ["lf", "g-data", "zoom-in", "zoom-out", "zoom-reset", "translate-rest",
			"reset", "undo", "redo", "clear", "re-draw", "export-data",
			"import-data", "import-fmeca", "config-check", "optimize-ckpt",
			"analyse"],
		template: `
			<div>
				<el-button-group>
					<el-button type="plain" size="small" @click="$_selectionSelect">选区</el-button>
					<el-button v-if="setDefault(zoomIn, true)" type="plain" size="small" @click="$_zoomIn">放大</el-button>
					<el-button v-if="setDefault(zoomOut, true)" type="plain" size="small" @click="$_zoomOut">缩小</el-button>
					<el-button v-if="setDefault(zoomReset, true)" type="plain" size="small" @click="$_zoomReset">大小适应</el-button>
					<el-button v-if="setDefault(translateRest, true)" type="plain" size="small" @click="$_translateRest">定位还原</el-button>
					<el-button v-if="setDefault(reset, true)" type="plain" size="small" @click="$_reset">还原(大小&定位)</el-button>
					<el-button v-if="setDefault(undo, true)" type="plain" size="small" @click="$_undo" :disabled="undoDisable">撤销(ctrl+z)</el-button>
					<el-button v-if="setDefault(redo, true)" type="plain" size="small" @click="$_redo" :disabled="redoDisable">重做(ctrl+y)</el-button>
					<el-button v-if="setDefault(clear, true)" type="plain" size="small" @click="$_clear">清空</el-button>
					<el-button v-if="setDefault(reDraw, true)" type="plain" size="small" @click="$_reDraw">重绘</el-button>

					<el-button v-if="setDefault(exportData, true)" type="plain" size="small"
						@click="exportData_dialogVisible = true">导出流图</el-button>
					<el-button v-if="setDefault(importData, true)" type="plain" size="small"
						@click="importData_dialogVisible = true">导入流图</el-button>
				</el-button-group>

				<el-upload v-if="setDefault(importFmeca, true)" style="display:inline-block; margin-left: -5px;"
					action="" :auto-upload="false" accept="application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
					:multiple="false" :show-file-list="false" :on-change="$_importFMECA">
					<el-button type="plain" size="small">载入FMECA</el-button>
				</el-upload>

				<el-button v-if="setDefault(configCheck, true)" type="plain" size="small" @click="$_check"
					style="display:inline-block; margin-left: -5px;">
					流图评价
				</el-button>

				<el-button v-if="setDefault(optimizeCkpt, true)" type="plain" size="small" @click="$_optimizeCkpt"
					style="display:inline-block; margin-left: -5px;">
					测点优化
				</el-button>

				<el-upload v-if="setDefault(analyse, true)" style="display:inline-block; margin-left: -5px;" action=""
					:auto-upload="false" accept=".csv" :multiple="false" :show-file-list="false" :on-change="$_analyse">
					<el-button type="plain" size="small">故障分析</el-button>
				</el-upload>

				<el-button v-if="setDefault(optimizeCkpt, true)" type="plain" size="small" @click="$_configGraph"
					style="display:inline-block; margin-left: -5px;">
					流图配置
				</el-button>

				<el-dialog width="60%" :title="'流图载入方式'" :visible.sync="importData_dialogVisible" :modal="false">

					<div style="display:flex;flex-direction:column;justify-content:space-between;align-items:center;gap:10px">

						<el-upload style="display:inline-block; margin-left: -5px;" action="" :auto-upload="false" accept=".json"
						:multiple="false" :show-file-list="false" :on-change="$_importData_global">
							<el-button type="primary" plain>载入全局数据</el-button>
						</el-upload>

						<el-upload style="display:inline-block; margin-left: -5px;" action="" :auto-upload="false" accept=".json"
						:multiple="false" :show-file-list="false" :on-change="$_importData_part_incremental">
							<el-button type="primary" plain>载入局部数据（增量式）</el-button>
						</el-upload>

						<el-button type="primary" @click="exportData_dialogVisible = false">关 闭</el-button>
					</div>
				</el-dialog>

				<el-dialog width="60%" :title="'流图导出方式'" :visible.sync="exportData_dialogVisible" :modal="false">
					<div style="display:flex;flex-direction:column;justify-content:space-between;align-items:center;gap:10px">
						<el-button type="primary" plain @click="$_exportData('global')">导出全局数据</el-button>
						<el-button type="primary" plain @click="$_exportData('part')">导出局部数据</el-button>
						<el-button type="primary" @click="exportData_dialogVisible = false">关 闭</el-button>
					</div>
				</el-dialog>

				<el-dialog width="60%" title="多信号流图评价" :visible.sync="Visible" :modal="false">
					<el-descriptions title="性能指标" :column="3" border v-if="dialogType === 'check'">
						<el-descriptions-item label="检出率">
							<span>{{ Math.round(100000*parseFloat(result.detect_isolat_ratio[0]))/1000 }}%</span>
						</el-descriptions-item>
						<el-descriptions-item label="隔离率">
							<span>{{ Math.round(100000*parseFloat(result.detect_isolat_ratio[1]))/1000 }}%</span>
						</el-descriptions-item>
						<el-descriptions-item label="冗余度">
							<span>{{ Math.round(100000*parseFloat(result.detect_isolat_ratio[2]))/1000 }}%</span>
						</el-descriptions-item>
					</el-descriptions>
					<el-table :data="result.D_mat" size="mini"  v-if="dialogType === 'check'"
						border max-height="200" style="overflow-x: auto;width: 100%!important;">
						<el-table-column v-for="k in result.col_names" :label="k ==='row_name'? '' : k"
							:key="k" :prop="k" :fixed="k ==='row_name'" width="100">
							<template slot-scope="scope">
								<span v-if="scope.row[k]===1" style="background-color: red; color: white;">{{ scope.row[k] }}</span>
								<span v-else>{{ scope.row[k] }}</span>
							</template>
						</el-table-column>
					</el-table>
				</el-dialog>
			</div>
		`,
		data() {
			return {
				obj: "demo",
				undoDisable: true,
				redoDisable: true,
				Visible: false,
				fileName: '多信号流图配置',
				result: {
					detect_isolat_ratio: [1, 1, 1, 1],
					col_names: [],
				},
				jsonText: '',
				reader: null,
				importData_dialogVisible: false,
				exportData_dialogVisible: false,
				visible: false,
				dialogType: 'check',
			}
		},
		mounted() {
			this.$props.lf.on('history:change', ({ data: { undoAble, redoAble } }) => {
				this.undoDisable = !undoAble
				this.redoDisable = !redoAble
			})
		},
		methods: {
			importStruct,
			exportStruct,
			setDefault,
			$_selectionSelect() {
				this.$props.lf.extension.selectionSelect.openSelectionSelect()
				this.$props.lf.once('selection:selected', () => {
					this.$props.lf.extension.selectionSelect.closeSelectionSelect()
				});
			},
			$_zoomIn() {
				this.$props.lf.zoom(true);
			},
			$_zoomOut() {
				this.$props.lf.zoom(false);
			},
			$_zoomReset() {
				this.$props.lf.resetZoom();
			},
			$_translateRest() {
				this.$props.lf.resetTranslate();
			},
			$_reset() {
				this.$props.lf.resetZoom();
				this.$props.lf.resetTranslate();
			},
			$_undo() {
				this.$props.lf.undo();
			},
			$_redo() {
				this.$props.lf.redo();
			},
			$_clear() {
				this.$props.lf.clearData();
			},
			$_reDraw() {
				let data = this.$props.lf.getGraphRawData()
				data.nodes.forEach((node) => {
					node.properties.showType = 'edit';
				});
				this.$props.lf.render(data);
			},
			$_exportData(type) {
				if (type === 'global') {
					// 全局导出
					let data = this.$props.gData;
					/**this.$Modal.confirm({
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
					  onOk: () => {**/
					const a = document.createElement('a');
					let jsonText = JSON.stringify(data, null, 4)
					a.download = this.fileName + '.json'
					a.style.display = 'none';
					a.href = window.URL.createObjectURL(new Blob([jsonText], { type: 'text/json' }))
					document.body.appendChild(a);
					a.click();
					window.URL.revokeObjectURL(a.href);
					document.body.removeChild(a);
					/**  }
					})**/
				} else if (type === 'part') {
					// 局部导出
					function deepClone(obj) {
						let _obj = JSON.stringify(obj),
							objClone = JSON.parse(_obj);
						return objClone
					}

					let data = {
						currentSystemId: deepClone(this.$props.gData.currentSystemId),
						SystemData: []
					}

					// 1.获取当前系统的数据
					let currentSystemData_copy = deepClone(this.$props.gData.SystemData.find(item => item.system_id == data.currentSystemId))
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
					getChildrenSystemData(data.currentSystemId, this.$props.gData.SystemData, data)

					// 1.
					/**this.$Modal.confirm({
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
					  onOk: () => {**/
					const a = document.createElement('a');
					let jsonText = JSON.stringify(data, null, 4)
					a.download = this.fileName + '.json'
					a.style.display = 'none';
					a.href = window.URL.createObjectURL(new Blob([jsonText], { type: 'text/json' }))
					document.body.appendChild(a);
					a.click();
					window.URL.revokeObjectURL(a.href);
					document.body.removeChild(a);
					/**   }
					})**/
				}
			},

			$_importData_global(file) {
				return new Promise((resolve, reject) => {
					// 检验是否支持 FileRender
					if (typeof FileReader === 'undefined') {
						reject('当前浏览器不支持FileReader')
					}
					// 执行读取json数据操作
					let reader = new FileReader()
					reader.readAsText(file.raw)
					reader.onerror = (error) => {
						reject('读取流图文件解析失败', error)
					}
					reader.onload = () => {
						if (reader.result) {
							try {
								resolve(JSON.parse(reader.result))
							} catch (error) {
								reject('读取流图文件解析失败', error)
							}
						} else {
							reject('读取流图文件解析失败', error)
						}
					}
				}).then((res) => {
					// this.$props.lf.render(importStruct(res))
					this.$emit("update-import-data", {
						type: 'global',
						value: res
					})
					this.importData_dialogVisible = false
				})
			},

			$_importData_part_incremental(file) {
				return new Promise((resolve, reject) => {
					// 检验是否支持 FileRender
					if (typeof FileReader === 'undefined') {
						reject('当前浏览器不支持FileReader')
					}
					// 执行读取json数据操作
					let reader = new FileReader()
					reader.readAsText(file.raw)
					reader.onerror = (error) => {
						reject('读取流图文件解析失败', error)
					}
					reader.onload = () => {
						if (reader.result) {
							try {
								resolve(JSON.parse(reader.result))
							} catch (error) {
								reject('读取流图文件解析失败', error)
							}
						} else {
							reject('读取流图文件解析失败', error)
						}
					}
				}).then((res) => {
					// let data = importStruct(res)
					// this.$props.lf.render(data)
					this.$emit("update-import-data", {
						type: 'part_incremental',
						value: res
					})
					this.importData_dialogVisible = false
				})
			},

			$_importFMECA(file) {
				let loading = this.$loading({
					lock: true,
					text: '加载中，请稍候...',
					spinner: 'el-icon-loading',
					background: 'rgba(0, 10, 0, 0.5)'
				})
				let fd = new FormData();
				fd.append('modelFile', file.raw);
				axios.post('/multi-info-edit/upload-fmeca/', fd)
					.then((res) => {
						this.$emit("update-import-data", {
							type: 'global',
							value: res.data
						})
						//this.$props.lf.render(importStruct(res.data));
						loading.close();
						this.$message({
							type: 'success',
							duration: 20,
							message: "解析完毕",
						})
					}).catch(err => {
						loading.close();
						this.$message({
							type: 'error',
							duration: 30,
							message: "解析失败",
						})
					});
			},

			$_optimizeCkpt() {
				let data = this.$props.gData.SystemData;
				let loading = this.$loading({
					lock: true,
					text: '加载中，请稍候...',
					spinner: 'el-icon-loading',
					background: 'rgba(0, 10, 0, 0.5)'
				})
				let fd = new FormData();
				fd.append('graphStruct', JSON.stringify(data));
				axios.post('/multi-info-edit/optimize-graph/', fd)
					.then((response) => {
						let res = response.data;
						this.$emit("update-import-data", {
							type: 'global',
							value: {
								SystemData: renderStructColor(res.data, "optim"), //sysData_,
								currentSystemId: data.currentSystemId
							},
						})
						//this.$props.lf.render(importStruct(res.data));
						this.dialogType = 'check';
						loading.close();
						this.$message({
							type: 'success',
							duration: 20,
							message: "优化完毕",
						})
					}).catch(err => {
						loading.close();
						this.$message({
							type: 'success',
							duration: 30,
							message: "优化失败",
						})
					});
			},

			$_check() {
				let data = this.$props.gData.SystemData;
				if (data.length === 0) {
					this.$message.warning('流图为空')
					return
				}
				let loading = this.$loading({
					lock: true,
					text: '加载中，请稍候...',
					spinner: 'el-icon-loading',
					background: 'rgba(0, 10, 0, 0.5)'
				})
				let fd = new FormData();
				fd.append('graphStruct', JSON.stringify(data));
				axios.post('/multi-info-edit/check-graph/', fd)
					.then((response) => {
						let res = response.data;
						this.result.detect_isolat_ratio = res.detect_isolat_ratio;
						this.result.col_names = ['row_name', ...res.col_names];//.map((itm,itmId)=>{return itmId+itm})];
						let D_mat = [];
						res.row_names.forEach((rowName, index) => {
							let map = { row_name: rowName };
							res.D_mat[index].forEach((val, i) => {
								map[res.col_names[i]] = val;
							});
							D_mat.push(map);
						});
						this.result.D_mat = D_mat;
						//let sysData_ = renderStructColor(res.data, "check");
						this.$emit("update-import-data", {
							type: "global",
							value: {
								SystemData: renderStructColor(res.data, "check"), //sysData_,
								currentSystemId: data.currentSystemId
							},
						})
						this.Visible = true;
						this.dialogType = 'check';
						loading.close();
						this.$message({
							type: 'success',
							duration: 20,
							message: "检查完毕",
						})
					}).catch(err => {
						loading.close();
						this.$message({
							type: 'error',
							duration: 30,
							message: "检查失败",
						})
					});
			},
			$_analyse(file) {
				let fd = new FormData();
				let data = this.$props.gData.SystemData;
				if (data.length === 0) {
					this.$message.warning('流图为空')
					return
				}
				let loading = this.$loading({
					lock: true,
					text: '加载中，请稍候...',
					spinner: 'el-icon-loading',
					background: 'rgba(0, 10, 0, 0.5)'
				})
				fd.append('graphStruct', JSON.stringify(data));
				fd.append('dataFile', file.raw);
				axios.post('/multi-info-analyse/analyse-data/', fd)
					.then((response) => {
						let res = response.data;
						//let sysData_ = renderStructColor(res.data, "analyse");
						this.$emit("update-import-data", {
							type: "global",
							value: {
								SystemData: renderStructColor(res.data, "analyse"), //sysData_,
								currentSystemId: data.currentSystemId,
							}
						});
						this.dialogType = 'analyse';
						loading.close();
						this.$message({
							type: 'success',
							duration: 20,
							message: "推理完毕",
						})
					}).catch(err => {
						loading.close();
						this.$message({
							type: 'error',
							duration: 30,
							message: "推理失败",
						})
					});
			},
			$_configGraph() {
				const formData = new FormData();

				formData.append('graphData', JSON.stringify(this.$props.gData));
				formData.append('obj', this.obj);

				axios.post('/multi-info-edit/config-graph/', formData).then(res => {
					// TODO: complete the function
					this.$message.success('配置成功')
				}).catch(err => {
					this.$message.error('配置失败')
				});
			},
		},
	});
let msfgComp = Vue.component(
	'ate-multi-signal-flow-graph',
	{
		props: ["zoom-in", "zoom-out", "zoom-reset", "translate-rest",
			"reset", "undo", "redo", "clear", "re-draw", "export-data",
			"import-data", "import-fmeca", "config-check", "optimize-ckpt",
			"analyse", "editable", "obj"],
		components: {
			'ate-comp-node-panel': nodePanel,
			'ate-comp-edit-dialog': editDialog,
			'ate-comp-control-panel': controlPanel,
		},
		template: `
			<div class="logic-flow-view">
				<div style="float: left" class="current-system-breadcrumb">
					<span> 所在系统：</span>
					<span v-for="(item, itemid) in current_system_breadcrumb">
						<el-tag v-if="item.name" @click="handleTagClick(item.id)" size="mini" type="primary">
						{{ item.name }}
						</el-tag>
						<span v-if="itemid !== current_system_breadcrumb.length - 1">{{ '>' }}</span>
					</span>
				</div>
				<div class="model—tree">
					<el-tree :data="module_tree" :expand-on-click-node="false"
						:indent="8" :default-expand-all="true" :props="defaultProps"
						@node-click="handleNodeClick" class="module-tree"></el-tree>
				</div>
				<div v-if="setDefault(editable, true)">
					<ate-comp-control-panel class="demo-control" v-if="lf" :lf="lf" :g-data="gData"
						:zoom-in="setDefault(zoomIn, true)" :zoom-out="setDefault(zoomOut, true)"
						:zoom-reset="setDefault(zoomReset, true)" :translate-rest="setDefault(translateRest, true)"
						:reset="setDefault(reset, true)" :undo="setDefault(undo, true)"
						:redo="setDefault(redo, true)" :clear="setDefault(clear, true)"
						:re-draw="setDefault(reDraw, true)" :export-data="setDefault(exportData, true)"
						:import-data="setDefault(importData, true)" :import-fmeca="setDefault(importFmeca, true)"
						:config-check="setDefault(configCheck, true)" :optimize-ckpt="setDefault(optimizeCkpt, true)"
						:analyse="setDefault(analyse, true)" @update-import-data="handleUpdatImportData" />

					<ate-comp-node-panel v-if="lf" :lf="lf" :g-data="gData"
						@updata-g-data="handle_update_gdata"
						@updata-g-data-subsystem="handle_update_gdata_subsystem" />
				</div>
				<div ref="container" class="LF-view"></div>
				<div v-if="setDefault(editable, true)">
					<ate-comp-edit-dialog 
						:dialog-visible.sync="dialogVisible"
						:form-data="formData"
						@data-update="$_dataUpdate" />
				</div>
			</div>
		`,
		data() {
			return {
				current_system_breadcrumb: 'root',
				module_tree: [],
				defaultProps: {
					children: 'children',
					label: 'label'
				},
				gData: {},
				lf: null,
				dialogVisible: false,
				formData: {},
			}
		},
		mounted() {
			this.$_initLf()
			const formData = new FormData();
			formData.append('obj', this.obj);
			axios.post('/multi-info-edit/init-graph/', formData).then(res => {
				// TODO: complete the function
				this.gData = res.data;
				this.module_tree = this.getModuleTree(this.gData.SystemData)
				this.handleUpdatImportData({
					type: 'global',
					value: res.data,
				})
				this.dialogType = 'analyse';
			}).catch(err => {
				this.gData = {
					SystemData: [{
						system_id: 1,
						parent_id: null,
						name: "root",
						data: {
							"nodes": [],
							"edges": []
						}
					}],
					currentSystemId: 1
				};
				this.module_tree = this.getModuleTree(this.gData.SystemData)
				let root_system = this.gData.SystemData.find(item => item.parent_id == null)
				this.current_system_breadcrumb = [{ name: root_system.name, id: root_system.system_id }]
				this.dialogType = 'analyse';
			});
		},
		methods: {
			...msfgMethods,
			setDefault,
			// 跟新gData数据 更新子系统的input或output
			handleTagClick(sysid) {
				this.handleNodeClick({ id: sysid });
			},
			handleUpdatImportData(data) {
				/**let root_system_import = data.value.SystemData.find(item => item.parent_id == null)
				// 1. 删除一切输入和输出节点 以及相关的边
				let inputORoutput_nodes = root_system_import.data.nodes.filter(item => item.type == 'input-node' || item.type == 'output-node')
				// 1.1 删除所有的相关边与节点
				for (let node of inputORoutput_nodes) {

					let edges = root_system_import.data.edges.filter(item => item.sourceNodeId == node.id || item.targetNodeId == node.id)
					for (let edge of edges) {
					root_system_import.data.edges.splice(root_system_import.data.edges.indexOf(edge), 1)
					}
					root_system_import.data.nodes.splice(root_system_import.data.nodes.indexOf(node), 1)
				}**/
				if (data.type == 'global') {
					this.gData = data.value
					let root_id = this.gData.SystemData.find(item => item.parent_id == null).system_id
					this.handleNodeClick({ id: root_id })
				} else if (data.type == 'part_incremental') {
					//1.将当前系统与导入的根系统进行合并
					let current_system = this.gData.SystemData.find(item => item.system_id == this.gData.currentSystemId)
					let root_system_import = data.value.SystemData.find(item => item.parent_id == null)
					function isEmptyObject(obj) {
						return Object.keys(obj).length === 0 && obj.constructor === Object;
					}

					if (isEmptyObject(current_system.data)) {
						current_system.data = root_system_import.data
					} else if (current_system.data.nodes.length == 0) {
						current_system.data = root_system_import.data
					}
					else {
						let current_system_rectangle = {
							x_leftUP: 1000000,
							y_leftUP: 1000000,
							x_rightDOWN: -1000000,
							y_rightDOWN: -1000000,

						}
						let root_system_import_rectangle = {
							x_leftUP: 1000000,
							y_leftUP: 1000000,
							x_rightDOWN: -1000000,
							y_rightDOWN: -1000000,
						}

						current_system.data.nodes.forEach(item => {
							if (item.x < current_system_rectangle.x_leftUP) {
								current_system_rectangle.x_leftUP = item.x
							}
							if (item.y < current_system_rectangle.y_leftUP) {
								current_system_rectangle.y_leftUP = item.y
							}
							if (item.x > current_system_rectangle.x_rightDOWN) {
								current_system_rectangle.x_rightDOWN = item.x
							}
							if (item.y > current_system_rectangle.y_rightDOWN) {
								current_system_rectangle.y_rightDOWN = item.y
							}
						})

						for (const item of root_system_import.data.nodes) {
							if (item.x < root_system_import_rectangle.x_leftUP) {
								root_system_import_rectangle.x_leftUP = item.x;
							}
							if (item.y < root_system_import_rectangle.y_leftUP) {
								root_system_import_rectangle.y_leftUP = item.y;
							}
							if (item.x > root_system_import_rectangle.x_rightDOWN) {
								root_system_import_rectangle.x_rightDOWN = item.x;
							}
							if (item.y > root_system_import_rectangle.y_rightDOWN) {
								root_system_import_rectangle.y_rightDOWN = item.y;
							}

							// 修复重复导入bug
							if (current_system.data.nodes.find(item2 => item2.id === item.id) !== undefined) {
								this.$message({
									message: '禁止重复导入 (有残余模块也会触发)',
									type: 'warning'
								});
								return; // 这会停止整个函数的执行
							}
						}

						let x_offset = current_system_rectangle.x_rightDOWN - root_system_import_rectangle.x_leftUP + 300
						let y_offset = current_system_rectangle.y_leftUP - root_system_import_rectangle.y_leftUP

						// 将导入的根系统的节点坐标进行偏移
						root_system_import.data.nodes.forEach(item => {
							item.x += x_offset
							item.width = 100
							item.y += y_offset
							if (item.type == 'subsystem-node') {
								item.text.x += x_offset
								item.text.y += y_offset
							}

							current_system.data.nodes.push(item)
						})
						// 将导入的根系统的边进行偏移
						root_system_import.data.edges.forEach(item => {
							item.startPoint.x += x_offset
							item.startPoint.y += y_offset
							item.endPoint.x += x_offset
							item.endPoint.y += y_offset
							item.pointsList.forEach(point => {
								point.x += x_offset
								point.y += y_offset
							})
							current_system.data.edges.push(item)
						})

					}
					//2.将导入的子系统添加到this.gData
					function getSubSystemRecursive(old_system_id, new_system_id, import_G_DATA, G_DATA) {
						// 调整子系统节点的systemid
						let current_system = G_DATA.SystemData.find(item => item.system_id == new_system_id)
						let current_system_subsystem_nodes = current_system.data.nodes.filter(item => item.type == 'subsystem-node')

						let children = import_G_DATA.SystemData.filter(item => item.parent_id == old_system_id)
						function deepClone(obj) {
							let _obj = JSON.stringify(obj),
								objClone = JSON.parse(_obj);
							return objClone
						}
						children.forEach(item => {
							let item_copy = deepClone(item)
							let old_system_id = item_copy.system_id
							item_copy.system_id = G_DATA.SystemData.length + 1
							item_copy.parent_id = new_system_id
							if (current_system_subsystem_nodes.find(item => item.properties.SubsystemId == old_system_id) !== undefined) {
								current_system_subsystem_nodes.find(item => item.properties.SubsystemId == old_system_id).properties.SubsystemId = item_copy.system_id
							}

							G_DATA.SystemData.push(item_copy)

							getSubSystemRecursive(old_system_id, item_copy.system_id, import_G_DATA, G_DATA)
						})

					}

					getSubSystemRecursive(root_system_import.system_id, current_system.system_id, data.value, this.gData)
					this.handleNodeClick({ id: this.gData.currentSystemId })
				}

				this.module_tree = this.getModuleTree(this.gData.SystemData)
				// this.$forceUpdate();
			},

			handle_update_gdata_subsystem(data) {
				// 根据子系统的id找到父系统
				let parent_id = this.gData.SystemData.find(item => item.system_id == data.system_id).parent_id
				let parent_system = this.gData.SystemData.find(item => item.system_id == parent_id)
				// 更新parent_system的中对应子系统的input或output
				if (data.type == 'input') {
					parent_system.data.nodes.find(item => item.properties.SubsystemId == data.system_id).properties.fields.input = data.value
				} else if (data.type == 'output') {
					parent_system.data.nodes.find(item => item.properties.SubsystemId == data.system_id).properties.fields.output = data.value
				}
			},

			// 更新gData数据 添加新子系统
			handle_update_gdata(new_system) {
				this.gData.SystemData.push(new_system)
				this.module_tree = this.getModuleTree(this.gData.SystemData)
			},
			// 从gData中解析module_tree
			getModuleTree(gData) {

				let root = gData.filter(item => item.parent_id == null)[0]

				let root_node = {
					label: root.name,
					id: root.system_id,
					children: []
				}

				function getModuleTreeRecursive(node, gData_) {
					// console.log(gData_, gData_.map(item => item.parent_id), node.id)

					let children = gData_.filter(item => item.parent_id == node.id)
					if (children.length == 0) {
						return null
					}
					children.forEach(item => {
						let child_node = {
							label: item.name,
							id: item.system_id,
							children: []
						}
						node.children.push(child_node)
						getModuleTreeRecursive(child_node, gData_)
					})
				}

				getModuleTreeRecursive(root_node, gData)
				return [root_node]
			},

			$_dataUpdate(_node) {
				let node = this.lf.graphModel.getNodeModelById(_node.id)
				node.updateText(_node.text.value)
				node.setProperties({ ..._node.properties })
				// 如果是更新子系统的text 则G_DATA中的数据也要更新
				if (_node.type == 'subsystem-node') {
					this.gData.SystemData.find(item => item.system_id == _node.properties.SubsystemId).name = _node.text.value
					this.module_tree = this.getModuleTree(this.gData.SystemData)
				}
			},
			handleNodeClick(data) {
				this.gData.currentSystemId = data.id

				// 更新面包屑 面包屑结构为 [{name:xxx,id:xxx},{name:xxx,id:xxx}] 从当前系统开始一直到root
				this.current_system_breadcrumb = []
				let current_system = this.gData.SystemData.find(item => item.system_id == data.id)
				while (current_system != undefined) {
					this.current_system_breadcrumb.push({ name: current_system.name, id: current_system.system_id })
					current_system = this.gData.SystemData.find(item => item.system_id == current_system.parent_id)
				}

				// 颠倒顺序，从root到当前系统
				this.current_system_breadcrumb = this.current_system_breadcrumb.reverse()

				this.$message({
					message: '当前系统已切换为' + this.current_system_breadcrumb.map(item => item.name).join(' > '),
					type: 'success'
				})


				// 临时补丁，当子系统的属性如input或output发生变化时，先渲染一次，更新子系统的外观属性，手动重新调整 线的起点和终点位置 然后再渲染一次
				// 1. 第一次渲染 并获取渲染后的绘图数据
				this.lf.render(this.gData.SystemData.find(item => item.system_id == data.id).data)
				let current_system_data = this.lf.getGraphData()

				// 2. 调整与子系统相关的连线的起点和终点位置
				let subsystem_nodes = current_system_data.nodes.filter(item => item.type == 'subsystem-node')

				for (let node of subsystem_nodes) {
					for (let anchor of node.anchors) {
						if (anchor.type == 'left') {
							// 调整连线的终点位置
							let relative_edges = current_system_data.edges.filter(item => item.targetAnchorId == anchor.id)
							relative_edges.forEach(item => {

								item.pointsList = []

								item.endPoint.x = anchor.x
								item.endPoint.y = anchor.y
							})
						} else if (anchor.type == 'right') {
							// 调整连线的起点位置
							let relative_edges = current_system_data.edges.filter(item => item.sourceAnchorId == anchor.id)
							relative_edges.forEach(item => {
								item.pointsList = []
								item.startPoint.x = anchor.x
								item.startPoint.y = anchor.y
							})
						}

					}
				}
				// 3. 再一次渲染
				this.lf.render(current_system_data)

			}
		},
	});
export { msfgComp }