<template>
  <div style="max-width: 700px; margin: 0 auto;">
    <el-form :model="form" label-width="100px">
      <el-form-item label="输入问题" :error="questionError">
        <div style="display: flex; align-items: flex-start;">
          <el-input v-model="form.question" type="textarea" :rows="3" placeholder="请输入要评测的问题" style="width: 500px; margin-right: 10px;" />
          <el-button type="primary" @click="submit" :loading="loading" style="width: 100px;">发送</el-button>
        </div>
      </el-form-item>
      <el-form-item label="模型列表">
        <el-select v-model="selectedModels" multiple style="width: 320px; margin-right: 10px;" placeholder="请选择参与评测的模型">
          <el-option v-for="m in modelList" :key="m.value" :label="m.label" :value="m.value" />
        </el-select>
        <el-button icon="el-icon-plus" circle @click="openAddModelDialog" style="margin-left: 10px;" >+</el-button>
      </el-form-item>
    </el-form>
    <el-row :gutter="20" style="margin-top: 30px;">
      <el-col :span="12">
        <el-card>
          <div style="font-weight:bold;">回复A：</div>
          <div style="min-height: 60px; margin: 10px 0; white-space: pre-wrap;">{{ answerA }}</div>
          <el-rate v-model="scoreA" :max="5" show-score style="margin-bottom: 10px;" />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <div style="font-weight:bold;">回复B：</div>
          <div style="min-height: 60px; margin: 10px 0; white-space: pre-wrap;">{{ answerB }}</div>
          <el-rate v-model="scoreB" :max="5" show-score style="margin-bottom: 10px;" />
        </el-card>
      </el-col>
    </el-row>
    <div v-if="answerA || answerB" style="margin: 20px 0; text-align: center;">
      <el-button type="primary" @click="chooseBetter('A')" style="margin: 0 10px; width: 100px;">A更好</el-button>
      <el-button type="primary" @click="chooseBetter('B')" style="margin: 0 10px; width: 100px;">B更好</el-button>
      <el-button type="info" @click="chooseBetter('tie')" style="margin: 0 10px; width: 100px;">平手</el-button>
      <el-button type="warning" @click="chooseBetter('bothbad')" style="margin: 0 10px; width: 100px;">一样差</el-button>
    </div>
    <el-divider />
    <div style="margin: 20px 0;">
      <div style="font-weight:bold;">累计打分统计：</div>
      <el-table :data="scoreStats" style="width: 100%; margin-top: 10px;">
        <el-table-column prop="label" label="模型" width="120" />
        <el-table-column prop="count" label="被选为更好次数" width="180" />
        <el-table-column prop="avgScore" label="平均得分" />
      </el-table>
      <el-button type="danger" @click="clearStats" style="margin-top: 10px;">重新计分</el-button>
      <el-button type="primary" @click="exportStats" style="margin-top: 10px; margin-left: 10px;">导出结果</el-button>
    </div>
    <!-- 新增模型弹窗 -->
    <el-dialog v-model="addModelDialog" title="新增模型" width="400px">
      <el-form>
        <el-form-item label="模型名称" label-width="80px">
          <el-input v-model="addModelForm.label" maxlength="30" placeholder="请输入模型名称" />
        </el-form-item>
        <el-form-item label="模型路径" label-width="80px">
          <el-input v-model="addModelForm.path" maxlength="200" placeholder="请输入模型路径（可选）" />
        </el-form-item>
        <el-form-item label="上传模型" label-width="80px">
          <el-upload
            class="upload-demo"
            :action="null"
            :auto-upload="false"
            :before-upload="beforeModelFileUpload"
            :on-change="onModelFileChange"
          >
            <el-button size="small" type="primary">上传模型文件</el-button>
          </el-upload>
          <span v-if="addModelForm.fileName" style="margin-left: 10px; color: #888;">{{ addModelForm.fileName }}</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addModelDialog = false">取消</el-button>
        <el-button type="primary" @click="addModel">添加</el-button>
      </template>
    </el-dialog>
  </div>
</template>
<script setup>
import { ref, reactive, computed } from 'vue'

const form = reactive({ question: '' })
const questionError = ref('')
const loading = ref(false)
const answerA = ref('')
const answerB = ref('')
const scoreA = ref(0)
const scoreB = ref(0)
const selectedModels = ref([])

const defaultModels = [
  { label: 'GPT', value: 'gpt' },
  { label: 'DeepSeek', value: 'deepseek' },
  { label: '自有模型A', value: 'customA' },
  { label: '自有模型B', value: 'customB' }
]
const modelList = ref(JSON.parse(localStorage.getItem('customModelList') || 'null') || defaultModels)

const addModelDialog = ref(false)
const addModelForm = reactive({ label: '', path: '', file: null, fileName: '' })

function openAddModelDialog() {
  addModelForm.label = ''
  addModelForm.path = ''
  addModelForm.file = null
  addModelForm.fileName = ''
  addModelDialog.value = true
}
function beforeModelFileUpload(file) {
  addModelForm.file = file
  addModelForm.fileName = file.name
  return false
}
function onModelFileChange(file) {
  addModelForm.file = file.raw
  addModelForm.fileName = file.name
}
function addModel() {
  if (!addModelForm.label) return
  const value = 'custom_' + Date.now()
  modelList.value.push({ label: addModelForm.label, value, path: addModelForm.path, fileName: addModelForm.fileName })
  localStorage.setItem('customModelList', JSON.stringify(modelList.value))
  addModelDialog.value = false
}

// 匿名打分统计
const scoreStatsRaw = ref(JSON.parse(localStorage.getItem('customScoreStats') || '[]'))
const scoreStats = computed(() => {
  const stats = {}
  scoreStatsRaw.value.forEach(item => {
    [item.modelA, item.modelB].forEach((m, idx) => {
      if (!stats[m.value]) stats[m.value] = { label: m.label, count: 0, totalScore: 0, scoreCount: 0 }
      if (item.better === (idx === 0 ? 'A' : 'B')) stats[m.value].count++
      stats[m.value].totalScore += item['score' + (idx === 0 ? 'A' : 'B')]
      stats[m.value].scoreCount++
    })
  })
  return Object.values(stats).map(s => ({
    label: s.label,
    count: s.count,
    avgScore: s.scoreCount ? (s.totalScore / s.scoreCount).toFixed(2) : '0.00'
  }))
})

let lastPair = ref([])
function submit() {
  questionError.value = ''
  answerA.value = ''
  answerB.value = ''
  scoreA.value = 0
  scoreB.value = 0
  if (!form.question || !form.question.trim()) {
    questionError.value = '请输入要评测的问题';
    return
  }
  if (selectedModels.value.length < 2) {
    questionError.value = '请选择至少两个模型参与评测';
    return
  }
  loading.value = true
  // 随机选两个模型
  const pool = modelList.value.filter(m => selectedModels.value.includes(m.value))
  const shuffled = pool.slice().sort(() => Math.random() - 0.5)
  lastPair.value = [shuffled[0], shuffled[1]]
  setTimeout(() => {
    answerA.value = `【匿名模型A】对问题的回答：\n${form.question}\n（模拟内容）`
    answerB.value = `【匿名模型B】对问题的回答：\n${form.question}\n（模拟内容）`
    loading.value = false
  }, 800)
}
function chooseBetter(better) {
  scoreStatsRaw.value.unshift({
    modelA: lastPair.value[0],
    modelB: lastPair.value[1],
    scoreA: scoreA.value,
    scoreB: scoreB.value,
    better
  })
  if (scoreStatsRaw.value.length > 100) scoreStatsRaw.value.length = 100
  localStorage.setItem('customScoreStats', JSON.stringify(scoreStatsRaw.value))
  answerA.value = ''
  answerB.value = ''
  scoreA.value = 0
  scoreB.value = 0
}
function clearStats() {
  scoreStatsRaw.value = []
  localStorage.removeItem('customScoreStats')
}
function exportStats() {
  let csv = '模型A,模型B,分数A,分数B,更好\n'
  scoreStatsRaw.value.forEach(r => {
    csv += `${r.modelA.label},${r.modelB.label},${r.scoreA},${r.scoreB},${r.better}\n`
  })
  csv += '\n统计:\n'
  scoreStats.value.forEach(s => {
    csv += `${s.label},被选为更好次数,${s.count},平均得分,${s.avgScore}\n`
  })
  const blob = new Blob([csv], { type: 'text/csv' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = '自定义评测统计.csv'
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}
</script> 