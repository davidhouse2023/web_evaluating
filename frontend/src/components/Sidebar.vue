<template>
  <div>
    <div style="padding: 24px 0; text-align: center; font-weight: bold; font-size: 20px; letter-spacing: 2px; color: #18408b;">模型评测</div>
    <el-menu default-active="1" class="el-menu-vertical-demo">
      <el-menu-item index="1" @click="$emit('change', 'general')">通用测评</el-menu-item>
      <el-menu-item index="2" @click="$emit('change', 'domain')">领域测评</el-menu-item>
      <el-menu-item index="3" @click="$emit('change', 'manual')">自定义测评</el-menu-item>
    </el-menu>
  </div>
</template> 