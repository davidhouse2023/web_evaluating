<template>
  <el-container style="height: 100vh">
    <el-aside width="200px">
      <Sidebar @change="current= $event" />
    </el-aside>
    <el-main>
      <GeneralEvaluation v-if="current==='general'" />
      <DomainEvaluation v-if="current==='domain'" />
      <ManualEvaluation v-if="current==='manual'" />
    </el-main>
  </el-container>
</template>
<script>
import Sidebar from './components/Sidebar.vue'
import GeneralEvaluation from './components/GeneralEvaluation.vue'
import DomainEvaluation from './components/DomainEvaluation.vue'
import ManualEvaluation from './components/CustomEvaluation.vue'
export default {
  components: { Sidebar, GeneralEvaluation, DomainEvaluation, ManualEvaluation },
  data() { return { current: 'general' } }
}
</script> 