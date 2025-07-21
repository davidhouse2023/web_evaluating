<template>
  <div>
    <el-form :model="form" label-width="100px" style="max-width: 500px">
      <el-form-item label="模型路径" :error="modelPathError">
        <el-input v-model="form.modelPath" />
      </el-form-item>
      <el-form-item label="评测类型">
        <el-select v-model="form.type">
          <el-option label="CMMLU" value="cmmlu" />
          <el-option label="MMLU-Pro" value="mmlu_pro" />
        </el-select>
      </el-form-item>
      <el-form-item label="few-shot">
        <el-input-number v-model="form.numFewShot" :min="0" :max="10" />
      </el-form-item>
      <el-form-item label="max_length">
        <el-input-number v-model="form.maxLength" :min="128" :max="4096" />
      </el-form-item>
      <el-form-item label="COT">
        <el-switch v-model="form.cot" />
      </el-form-item>
      <el-button type="primary" @click="submit" :loading="loading">提交评测</el-button>
      <el-button @click="testApi" style="margin-left: 10px">测试接口</el-button>
    </el-form>
    <div v-if="taskId" style="margin-top: 20px">
      <el-progress :percentage="progress" v-if="progress<100" />
      <el-alert v-if="error" :title="error" type="error" />
      <el-button v-if="resultReady" @click="download">下载结果</el-button>
      <div v-if="resultData">
        <v-chart :option="chartOption" style="height:400px" />
      </div>
    </div>
    <div v-if="testTaskId" style="margin-top: 20px; max-width: 500px;">
      <el-progress :percentage="testProgress" v-if="testStatus!=='finished'" />
      <el-card v-if="testStatus==='finished' && testResult">
        <div v-for="(v, k) in testResult" :key="k">
          <b>{{ k }}:</b> {{ v }}
        </div>
      </el-card>
    </div>
  </div>
</template>
<script setup>
import { ref, reactive } from 'vue'
import axios from 'axios'
import * as echarts from 'echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, TitleComponent } from 'echarts/components'
use([CanvasRenderer, BarChart, GridComponent, TooltipComponent, TitleComponent])

const form = reactive({
  modelPath: '',
  type: 'cmmlu',
  numFewShot: 5,
  maxLength: 2048,
  cot: false
})
const loading = ref(false)
const taskId = ref('')
const progress = ref(0)
const resultReady = ref(false)
const resultData = ref(null)
const error = ref('')
const chartOption = ref({})
const modelPathError = ref('')

// test接口相关
const testTaskId = ref('')
const testProgress = ref(0)
const testStatus = ref('')
const testResult = ref(null)
let testTimer = null

let pollTimer = null

function submit() {
  modelPathError.value = ''
  if (!form.modelPath) {
    modelPathError.value = '模型路径不能为空';
    return;
  }
  loading.value = true
  error.value = ''
  resultReady.value = false
  resultData.value = null
  progress.value = 0
  const url = `/api/evaluate/${form.type}`
  axios.post(url, {
    model_path: form.modelPath,
    num_few_shot: form.numFewShot,
    max_length: form.maxLength,
    cot: form.cot
  }).then(res => {
    taskId.value = res.data.task_id
    pollStatus()
  }).catch(e => {
    error.value = e.message
    loading.value = false
  })
}

function pollStatus() {
  pollTimer && clearTimeout(pollTimer)
  axios.get(`/api/evaluate/status/${taskId.value}`).then(res => {
    progress.value = res.data.progress || (res.data.status === 'finished' ? 100 : 0)
    if(res.data.status==='pending') {
      pollTimer = setTimeout(pollStatus, 2000)
    } else if(res.data.status==='finished') {
      resultReady.value = true
      fetchResult()
    } else if(res.data.status==='error') {
      error.value = res.data.error
      loading.value = false
    }
  })
}

function fetchResult() {
  axios.get(`/api/evaluate/result/${taskId.value}`).then(res => {
    resultData.value = res.data
    loading.value = false
    if(Array.isArray(res.data)) {
      chartOption.value = {
        title: { text: '评测准确率' },
        tooltip: {},
        xAxis: { type: 'category', data: res.data.map(i=>i.subject||i.category||'') },
        yAxis: { type: 'value' },
        series: [{ type: 'bar', data: res.data.map(i=>i.acc||i.accuracy||0) }]
      }
    }
  })
}

function download() {
  window.open(`/api/evaluate/download/${taskId.value}`)
}

function testApi() {
  testTaskId.value = ''
  testProgress.value = 0
  testStatus.value = ''
  testResult.value = null
  axios.post('/api/evaluate/test').then(res => {
    testTaskId.value = res.data.task_id
    pollTestStatus()
  })
}

function pollTestStatus() {
  testTimer && clearTimeout(testTimer)
  axios.get(`/api/evaluate/test_status/${testTaskId.value}`).then(res => {
    testProgress.value = res.data.progress || 0
    testStatus.value = res.data.status
    if(res.data.status === 'pending') {
      testTimer = setTimeout(pollTestStatus, 700)
    } else if(res.data.status === 'finished') {
      testResult.value = res.data.result
    }
  })
}
</script>
<script>
import { defineComponent } from 'vue'
import VChart from 'vue-echarts'
export default defineComponent({
  components: { VChart }
})
</script> 