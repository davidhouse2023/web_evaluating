<template>
  <div>
    <el-tabs v-model="activeTab">
      <el-tab-pane label="大模型评测" name="auto">
        <!-- 大模型评测原有表单和逻辑 -->
        <el-form :model="form" label-width="120px" style="max-width: 600px">
          <el-form-item label="自有模型" :error="modelPathError">
            <el-input v-model="form.modelPath" placeholder="请输入自有模型路径" style="width: 320px; margin-right: 10px;" />
            <el-upload
              class="upload-demo"
              :action="null"
              :auto-upload="false"
              :before-upload="beforeModelUpload"
              :on-change="onModelFileChange"
              style="display: inline-block; vertical-align: middle;"
            >
              <el-button size="small" type="primary" style="width: 80px;">上传</el-button>
            </el-upload>
          </el-form-item>
          <el-form-item label="数据集" :error="dataPathError">
            <el-input v-model="form.dataPath" placeholder="请输入数据集路径" style="width: 320px; margin-right: 10px;" />
            <el-upload
              class="upload-demo"
              :action="null"
              :auto-upload="false"
              :before-upload="beforeDataUpload"
              :on-change="onDataFileChange"
              style="display: inline-block; vertical-align: middle;"
            >
              <el-button size="small" type="primary" style="width: 80px;">上传</el-button>
            </el-upload>
          </el-form-item>
          <el-form-item label="评测大模型">
            <el-select v-model="form.evalModel" style="width: 320px;">
              <el-option label="GPT" value="gpt" />
              <el-option label="DeepSeek" value="deepseek" />
            </el-select>
          </el-form-item>
          <el-form-item label="自定义提示词" :error="promptError">
            <el-input v-model="form.prompt" type="textarea" :rows="9" placeholder="请输入自定义提示词（可选）" style="width: 320px;" :maxlength="5000" show-word-limit />
            <div style="margin-top: 10px;">
              <el-button size="small" type="success" @click="openSavePromptDialog" style="width: 120px; margin-right: 10px;">保存提示词</el-button>
              <el-button size="small" @click="showPromptHistory = true" style="width: 120px;">历史版本</el-button>
            </div>
          </el-form-item>
          <el-button type="primary" @click="submit" :loading="loading" style="width: 120px;">提交领域测评</el-button>
        </el-form>
        <div v-if="taskId" style="margin-top: 20px">
          <el-progress :percentage="progress" v-if="progress<100" />
          <el-alert v-if="error" :title="error" type="error" />
          <el-button v-if="resultReady" @click="download">下载结果</el-button>
          <el-card v-if="resultData" style="margin-top: 20px">
            <div v-for="(v, k) in resultData" :key="k">
              <b>{{ k }}:</b> {{ v }}
            </div>
          </el-card>
        </div>
        <div v-if="autoResults.length" style="margin: 30px 0 10px 0; font-weight: bold;">
          <span>正确率：{{ autoStats.accuracy }}%，不正确率：{{ autoStats.inaccuracy }}%</span>
          <el-button type="primary" @click="exportAutoResults" style="margin-left: 20px;">下载详细统计</el-button>
        </div>
        <el-table v-if="autoResults.length" :data="autoResults" style="width: 100%;">
          <el-table-column prop="question" label="题目" width="200" />
          <el-table-column prop="answer" label="标准答案" width="180" />
          <el-table-column prop="modelAnswer" label="模型回复" width="180" />
          <el-table-column prop="correct" label="是否正确" width="100">
            <template #default="scope">
              <el-tag :type="scope.row.correct ? 'success' : 'danger'">{{ scope.row.correct ? '正确' : '不正确' }}</el-tag>
            </template>
          </el-table-column>
        </el-table>
        <!-- 保存提示词弹窗 -->
        <el-dialog v-model="savePromptDialog" title="保存提示词" width="400px">
          <el-form>
            <el-form-item label="版本名称" label-width="80px">
              <el-input v-model="promptVersionName" maxlength="50" placeholder="请输入版本名称" />
            </el-form-item>
          </el-form>
          <template #footer>
            <el-button @click="savePromptDialog = false">取消</el-button>
            <el-button type="primary" @click="savePrompt">保存</el-button>
          </template>
        </el-dialog>
        <!-- 历史版本弹窗（重设计+编辑删除） -->
        <el-dialog v-model="showPromptHistory" title="提示词历史版本" width="700px">
          <el-table :data="promptHistory" style="width: 100%" @row-click="viewPromptDetail">
            <el-table-column prop="name" label="版本名称" width="120" />
            <el-table-column prop="time" label="保存时间" width="180" />
            <el-table-column label="操作" width="200">
              <template #default="scope">
                <el-button size="small" @click.stop="viewPromptDetail(scope.row)">查看</el-button>
                <el-button size="small" type="warning" @click.stop="editPrompt(scope.$index, scope.row)" style="margin-left: 8px;">编辑</el-button>
                <el-button size="small" type="danger" @click.stop="deletePrompt(scope.$index)" style="margin-left: 8px;">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
          <template #footer>
            <el-button @click="showPromptHistory = false">关闭</el-button>
          </template>
        </el-dialog>
        <!-- 查看完整提示词内容弹窗 -->
        <el-dialog v-model="showPromptDetail" :title="'版本：' + (promptDetail?.name || '')" width="600px">
          <div style="white-space: pre-wrap; word-break: break-all; max-height: 400px; overflow-y: auto;">
            <b>保存时间：</b>{{ promptDetail?.time }}<br />
            <b>内容：</b>
            <div style="margin-top: 10px;">{{ promptDetail?.content }}</div>
          </div>
          <template #footer>
            <el-button @click="showPromptDetail = false">关闭</el-button>
          </template>
        </el-dialog>
        <!-- 编辑提示词弹窗 -->
        <el-dialog v-model="editPromptDialog" title="编辑提示词版本" width="600px">
          <el-form>
            <el-form-item label="版本名称" label-width="80px">
              <el-input v-model="editPromptData.name" maxlength="50" placeholder="请输入版本名称" />
            </el-form-item>
            <el-form-item label="内容" label-width="80px">
              <el-input v-model="editPromptData.content" type="textarea" :rows="9" :maxlength="5000" show-word-limit style="width: 100%" />
            </el-form-item>
          </el-form>
          <template #footer>
            <el-button @click="editPromptDialog = false">取消</el-button>
            <el-button type="primary" @click="saveEditPrompt">保存</el-button>
          </template>
        </el-dialog>
      </el-tab-pane>
      <el-tab-pane label="人工评测" name="manual">
        <el-form :model="manualForm" label-width="120px" style="max-width: 600px">
          <el-form-item label="评测集" :error="manualDataError">
            <el-input v-model="manualForm.dataPath" placeholder="请输入评测集路径" style="width: 320px; margin-right: 10px;" />
            <el-upload
              class="upload-demo"
              :action="null"
              :auto-upload="false"
              :before-upload="beforeManualDataUpload"
              :on-change="onManualDataFileChange"
              style="display: inline-block; vertical-align: middle;"
            >
              <el-button size="small" type="primary" style="width: 80px;">上传</el-button>
            </el-upload>
            <span v-if="manualForm.dataFileName" style="margin-left: 10px; color: #888;">{{ manualForm.dataFileName }}</span>
          </el-form-item>
          <el-form-item label="模型" :error="manualModelError">
            <el-input v-model="manualForm.modelPath" placeholder="请输入模型路径" style="width: 320px; margin-right: 10px;" />
            <el-upload
              class="upload-demo"
              :action="null"
              :auto-upload="false"
              :before-upload="beforeManualModelUpload"
              :on-change="onManualModelFileChange"
              style="display: inline-block; vertical-align: middle;"
            >
              <el-button size="small" type="primary" style="width: 80px;">上传</el-button>
            </el-upload>
            <span v-if="manualForm.modelFileName" style="margin-left: 10px; color: #888;">{{ manualForm.modelFileName }}</span>
          </el-form-item>
          <el-button type="primary" @click="manualEvaluate" :loading="manualLoading" style="width: 120px;">生成结果</el-button>
        </el-form>
        <el-table :data="manualResultsPage" style="width: 100%; margin-top: 30px;">
          <el-table-column prop="answer" label="参考回复" width="240">
            <template #default="scope">
              <el-tooltip class="item" effect="dark" :content="scope.row.answer" placement="top">
                <span style="display: inline-block; max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{{ scope.row.answer }}</span>
              </el-tooltip>
            </template>
          </el-table-column>
          <el-table-column prop="modelAnswer" label="模型生成回复" width="240">
            <template #default="scope">
              <el-tooltip class="item" effect="dark" :content="scope.row.modelAnswer" placement="top">
                <span style="display: inline-block; max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{{ scope.row.modelAnswer }}</span>
              </el-tooltip>
            </template>
          </el-table-column>
          <el-table-column label="一致性判定" width="200">
            <template #default="scope">
              <el-button-group>
                <el-button size="small" type="success" :plain="scope.row.consistent!==true" @click="setConsistent(scope.row, true)">一致</el-button>
                <el-button size="small" type="danger" :plain="scope.row.consistent!==false" @click="setConsistent(scope.row, false)">不一致</el-button>
              </el-button-group>
            </template>
          </el-table-column>
        </el-table>
        <el-pagination
          v-if="manualResults.length > 5"
          style="margin: 16px 0; text-align: right;"
          background
          layout="prev, pager, next"
          :page-size="5"
          :total="manualResults.length"
          v-model:current-page="manualPage"
        />
        <div v-if="manualResults.length" style="margin: 20px 0; font-weight: bold; display: flex; align-items: center;">
          <span>一致：{{ manualStats.consistent }}，不一致：{{ manualStats.inconsistent }}</span>
          <el-button type="danger" @click="clearManualResults" style="margin-left: 20px;">重置统计</el-button>
          <el-button type="primary" @click="exportManualResults" style="margin-left: 20px;">导出结果</el-button>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>
<script setup>
import { ref, reactive, computed } from 'vue'
import axios from 'axios'

const form = reactive({
  modelPath: '',
  modelFile: null,
  dataPath: '',
  dataFile: null,
  evalModel: 'gpt',
  prompt: ''
})
const loading = ref(false)
const taskId = ref('')
const progress = ref(0)
const resultReady = ref(false)
const resultData = ref(null)
const error = ref('')
const modelPathError = ref('')
const dataPathError = ref('')
const promptError = ref('')
let pollTimer = null

// 提示词保存与历史
const savePromptDialog = ref(false)
const promptVersionName = ref('')
const promptHistory = ref(JSON.parse(localStorage.getItem('promptHistory') || '[]'))
const showPromptHistory = ref(false)
const showPromptDetail = ref(false)
const promptDetail = ref(null)
const editPromptDialog = ref(false)
const editPromptData = reactive({ name: '', content: '', index: -1 })

function openSavePromptDialog() {
  promptVersionName.value = ''
  savePromptDialog.value = true
}
function savePrompt() {
  if (!promptVersionName.value) return
  const now = new Date()
  promptHistory.value.unshift({
    name: promptVersionName.value,
    time: now.toLocaleString(),
    content: form.prompt
  })
  // 最多保存20条
  if (promptHistory.value.length > 20) promptHistory.value.length = 20
  localStorage.setItem('promptHistory', JSON.stringify(promptHistory.value))
  savePromptDialog.value = false
}
function viewPromptDetail(row) {
  promptDetail.value = row
  showPromptDetail.value = true
}
function deletePrompt(index) {
  promptHistory.value.splice(index, 1)
  localStorage.setItem('promptHistory', JSON.stringify(promptHistory.value))
}
function editPrompt(index, row) {
  editPromptData.name = row.name
  editPromptData.content = row.content
  editPromptData.index = index
  editPromptDialog.value = true
}
function saveEditPrompt() {
  if (editPromptData.index >= 0) {
    promptHistory.value[editPromptData.index].name = editPromptData.name
    promptHistory.value[editPromptData.index].content = editPromptData.content
    localStorage.setItem('promptHistory', JSON.stringify(promptHistory.value))
    editPromptDialog.value = false
  }
}

function beforeModelUpload(file) {
  form.modelFile = file
  return false
}
function onModelFileChange(file) {
  form.modelFile = file.raw
}
function beforeDataUpload(file) {
  form.dataFile = file
  return false
}
function onDataFileChange(file) {
  form.dataFile = file.raw
}

function submit() {
  modelPathError.value = ''
  dataPathError.value = ''
  promptError.value = ''
  if (!form.modelPath && !form.modelFile) {
    modelPathError.value = '请上传模型文件或填写模型路径';
  }
  if (!form.dataPath && !form.dataFile) {
    dataPathError.value = '请上传数据集或填写数据集路径';
  }
  if (!form.prompt || !form.prompt.trim()) {
    promptError.value = '自定义提示词不能为空';
  }
  if (modelPathError.value || dataPathError.value || promptError.value) {
    return;
  }
  loading.value = true
  error.value = ''
  resultReady.value = false
  resultData.value = null
  progress.value = 0
  const formData = new FormData()
  if (form.modelPath) formData.append('model_path', form.modelPath)
  if (form.modelFile) formData.append('model_file', form.modelFile)
  if (form.dataPath) formData.append('data_path', form.dataPath)
  if (form.dataFile) formData.append('data_file', form.dataFile)
  formData.append('eval_model', form.evalModel)
  formData.append('prompt', form.prompt)
  axios.post('/api/evaluate/domain', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
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
  })
}
function download() {
  window.open(`/api/evaluate/download/${taskId.value}`)
}

const activeTab = ref('auto')
// 人工评测相关
const manualForm = reactive({ dataPath: '', dataFile: null, dataFileName: '', modelPath: '', modelFile: null, modelFileName: '' })
const manualDataError = ref('')
const manualModelError = ref('')
const manualLoading = ref(false)
const manualResults = ref([])
const manualPage = ref(1)
const manualResultsPage = computed(() => {
  const start = (manualPage.value - 1) * 5
  return manualResults.value.slice(start, start + 5)
})
const manualStats = computed(() => {
  let consistent = 0, inconsistent = 0
  manualResults.value.forEach(r => {
    if (r.consistent === true) consistent++
    else if (r.consistent === false) inconsistent++
  })
  return { consistent, inconsistent }
})
function beforeManualDataUpload(file) {
  manualForm.dataFile = file
  manualForm.dataFileName = file.name
  return false
}
function onManualDataFileChange(file) {
  manualForm.dataFile = file.raw
  manualForm.dataFileName = file.name
}
function beforeManualModelUpload(file) {
  manualForm.modelFile = file
  manualForm.modelFileName = file.name
  return false
}
function onManualModelFileChange(file) {
  manualForm.modelFile = file.raw
  manualForm.modelFileName = file.name
}
function manualEvaluate() {
  manualDataError.value = ''
  manualModelError.value = ''
  if (!manualForm.dataPath && !manualForm.dataFile) {
    manualDataError.value = '请上传评测集或填写路径';
    return
  }
  if (!manualForm.modelPath && !manualForm.modelFile) {
    manualModelError.value = '请上传模型或填写路径';
    return
  }
  manualLoading.value = true
  // 生成模拟数据
  setTimeout(() => {
    manualResults.value = [
      { answer: '参考回复A', modelAnswer: '模型生成回复A', consistent: null },
      { answer: '参考回复B', modelAnswer: '模型生成回复B', consistent: null },
      { answer: '参考回复C', modelAnswer: '模型生成回复C', consistent: null }
    ]
    manualLoading.value = false
  }, 800)
}
function clearManualResults() {
  manualResults.value = []
  manualPage.value = 1 // 重置分页
}
function setConsistent(row, val) {
  row.consistent = val
}
function exportManualResults() {
  // 导出表格内容和统计内容为CSV
  let csv = '参考回复,模型生成回复,一致性\n'
  manualResults.value.forEach(r => {
    csv += `${r.answer},${r.modelAnswer},${r.consistent===true?'一致':r.consistent===false?'不一致':''}\n`
  })
  csv += `\n统计,一致,${manualStats.value.consistent}\n统计,不一致,${manualStats.value.inconsistent}\n`
  const blob = new Blob([csv], { type: 'text/csv' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = '人工评测结果.csv'
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

const autoResults = ref([])
const autoStats = computed(() => {
  if (!autoResults.value.length) return { accuracy: 0, inaccuracy: 0 }
  const correct = autoResults.value.filter(r => r.correct).length
  const total = autoResults.value.length
  return {
    accuracy: ((correct / total) * 100).toFixed(2),
    inaccuracy: (((total - correct) / total) * 100).toFixed(2)
  }
})
function exportAutoResults() {
  let csv = '题目,标准答案,模型回复,是否正确\n'
  autoResults.value.forEach(r => {
    csv += `${r.question},${r.answer},${r.modelAnswer},${r.correct ? '正确' : '不正确'}\n`
  })
  csv += `\n统计,正确率,${autoStats.value.accuracy}%\n统计,不正确率,${autoStats.value.inaccuracy}%\n`
  const blob = new Blob([csv], { type: 'text/csv' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = '大模型评测统计.csv'
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}
</script> 