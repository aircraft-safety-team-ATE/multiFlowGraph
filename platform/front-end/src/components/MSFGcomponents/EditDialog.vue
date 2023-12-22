<template>
  <el-dialog
    title="编辑节点属性"
    width="60%"
    :visible.sync="dialogVisible"
    :before-close="closeDialog"
    @open="openDialog">

    <el-form
      :model="form"
      :rules="rules"
      ref="form">
      <!-- 共通 -->
      <el-form-item label="ID" prop="id" :label-width="'120px'">
        <el-input v-model="form.id" :disabled="true"></el-input>
      </el-form-item>
      <el-form-item label="类型" prop="type" :label-width="'120px'">
        <el-input v-model="form.type" :disabled="true"></el-input>
      </el-form-item>
      <el-form-item label="名称" prop="text.value" :label-width="'120px'">
        <el-input v-model="form.text.value"></el-input>
      </el-form-item>
      <!-- fault-node -->
      <el-form-item
        v-if="form.type === 'fault-node'"
        label="故障等级"
        prop="properties.flevel"
        :label-width="'120px'"
        style="text-align: left;">
        <el-select
          v-model="form.properties.flevel"
          placeholder="请选择故障等级"
          clearable>
          <el-option
            v-for="level in faultLevelList"
            :key="level.value"
            :label="level.text"
            :value="level.value"
          ></el-option>
        </el-select>
      </el-form-item>
      <!-- switch-node -->
      <el-form-item
        v-if="form.type === 'switch-node'"
        label="常闭/常开"
        prop="properties.normalState"
        :label-width="'120px'"
        style="text-align: left;">
        <el-switch
          v-model="form.properties.normalState"
          active-color="#13ce66"
          inactive-color="#ff4949">
        </el-switch>
      </el-form-item>
      <!-- algorithm-node -->
      <el-form-item
        v-if="form.type === 'algorithm-node'"
        label="算法"
        prop="properties.algorithm"
        :label-width="'120px'"
        style="text-align: left;">
        <el-select
          v-model="form.properties.algorithm"
          placeholder="请选择算法"
          clearable>
          <el-option
            v-for="algorithm in algorithmList"
            :key="algorithm.value"
            :label="algorithm.text"
            :value="algorithm.value"
          ></el-option>
        </el-select>
      </el-form-item>
      <!--  -->
    </el-form>

    <span slot="footer" class="dialog-footer">
      <el-button @click="closeDialog">取 消</el-button>
      <el-button type="primary" @click="formDataUpdate">确 定</el-button>
    </span>
  </el-dialog>
</template>

<script>
export default {
  name: 'EditDialog',
  props: {
    dialogVisible: {
      type: Boolean
    },
    formData: {
      type: Object,
      required: true
    },
  },
  data () {
    return {
      form: {
        text: {
          value: ''
        },
        properties: {
          normalState: true,
          flevel: 0
        }
      },
      // 验证规则
      rules: {
        'text.value': [{ required: true, message: '请输入节点名称', trigger: 'blur' }],
        'properties.flevel': [{ required: true, message: '请选择故障等级', trigger: 'change' }],
        'properties.algorithm': [{ required: true, message: '请选择算法', trigger: 'change' }],
      },
      faultLevelList: [
        {
          value: 0,
          text: '无故障'
        },
        {
          value: 1,
          text: '一级故障'
        },
        {
          value: 2,
          text: '二级故障'
        },
        {
          value: 3,
          text: '三级故障'
        },
      ],
      algorithmList: [
        {
          value: 0,
          text: '无算法'
        },
        {
          value: 'lof',
          text: '离群因子算法'
        },
        {
          value: 'dsPot',
          text: '漂移峰值阈值算法'
        },
      ]
    }
  },
  computed: {

  },
  methods: {
    formDataUpdate () {
      this.$refs['form'].validate((valid, errs) => {
        if (valid) {
          this.$emit('data-update', this.form)
          this.closeDialog()
        } else {

        }
      })
    },
    closeDialog () {
      this.$emit('update:dialogVisible', false)
    },
    openDialog () {
      this.form = {...this.formData}
    },
  },
  watch: {

  }
}
</script>