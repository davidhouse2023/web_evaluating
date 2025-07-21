# web_evaluating

本项目为基于Flask+Vue的多模型评测平台，支持CMMLU和MMLU-Pro评测。

## 目录结构

```
web_evaluating/
  backend/         # Flask后端
    app.py
    evaluate/
      cmmlu_runner.py
      mmlu_pro_runner.py
    static/        # 前端打包文件
    results/       # 评测结果存放
  frontend/        # Vue前端
    src/
      components/
        Sidebar.vue
        GeneralEvaluation.vue
        DomainEvaluation.vue
        ManualEvaluation.vue
      App.vue
      main.js
    public/
    package.json
```

## 启动方式

### 1. 后端
```bash
cd web_evaluating/backend
pip install -r requirements.txt
python app.py
```

### 2. 前端
```bash
cd web_evaluating/frontend
npm install
npm run serve
```

## 功能说明
- 侧边栏：通用测评、领域测评、人工测评
- 通用测评：支持CMMLU和MMLU-Pro评测，输入模型路径即可评测，支持结果可视化和下载 