from flask import Flask, request, jsonify, send_from_directory, session
from flask_cors import CORS
import threading, uuid, os
from evaluate.cmmlu_runner import run_cmmlu
from evaluate.mmlu_pro_runner import run_mmlu_pro
import time

# 用于存储测试任务的进度
test_progress = {}

app = Flask(__name__, static_folder="static")
CORS(app)
tasks = {}

@app.route('/api/evaluate/cmmlu', methods=['POST'])
def evaluate_cmmlu():
    data = request.json
    task_id = str(uuid.uuid4())
    tasks[task_id] = {'status': 'pending'}
    def task():
        try:
            result_path = run_cmmlu(data)
            tasks[task_id] = {'status': 'finished', 'result': result_path}
        except Exception as e:
            tasks[task_id] = {'status': 'error', 'error': str(e)}
    threading.Thread(target=task).start()
    return jsonify({'task_id': task_id})

@app.route('/api/evaluate/mmlu_pro', methods=['POST'])
def evaluate_mmlu_pro():
    data = request.json
    task_id = str(uuid.uuid4())
    tasks[task_id] = {'status': 'pending'}
    def task():
        try:
            result_path = run_mmlu_pro(data)
            tasks[task_id] = {'status': 'finished', 'result': result_path}
        except Exception as e:
            tasks[task_id] = {'status': 'error', 'error': str(e)}
    threading.Thread(target=task).start()
    return jsonify({'task_id': task_id})

@app.route('/api/evaluate/test', methods=['POST'])
def test_api_start():
    task_id = str(uuid.uuid4())
    test_progress[task_id] = 0
    def run():
        for p in [20, 40, 60, 80, 100]:
            time.sleep(0.7)
            test_progress[task_id] = p
    threading.Thread(target=run).start()
    return jsonify({'task_id': task_id})

@app.route('/api/evaluate/test_status/<task_id>', methods=['GET'])
def test_api_status(task_id):
    p = test_progress.get(task_id, 0)
    if p < 100:
        return jsonify({'progress': p, 'status': 'pending'})
    else:
        # 进度100时返回完整数据
        data = {
            'model': 'test-model',
            'status': 'ready',
            'progress': 100,
            'accuracy': 0.88,
            'message': '测试接口返回成功'
        }
        return jsonify({'progress': 100, 'status': 'finished', 'result': data})

@app.route('/api/evaluate/domain', methods=['POST'])
def evaluate_domain():
    model_path = request.form.get('model_path')
    data_path = request.form.get('data_path')
    eval_model = request.form.get('eval_model')
    prompt = request.form.get('prompt')
    model_file = request.files.get('model_file')
    data_file = request.files.get('data_file')
    task_id = str(uuid.uuid4())
    tasks[task_id] = {'status': 'pending', 'progress': 0}
    # 保存上传模型文件（如有）
    if model_file:
        upload_dir = os.path.join('results', 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        model_file_path = os.path.join(upload_dir, f'{task_id}_model_{model_file.filename}')
        model_file.save(model_file_path)
    else:
        model_file_path = model_path
    # 保存上传数据集文件（如有）
    if data_file:
        upload_dir = os.path.join('results', 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        data_file_path = os.path.join(upload_dir, f'{task_id}_data_{data_file.filename}')
        data_file.save(data_file_path)
    else:
        data_file_path = data_path
    def task():
        try:
            # 模拟评测进度
            for p in [20, 40, 60, 80, 100]:
                time.sleep(1)
                tasks[task_id]['progress'] = p
            # 模拟评测结果
            result = {
                'model_path': model_file_path,
                'data_path': data_file_path,
                'eval_model': eval_model,
                'prompt': prompt,
                'accuracy': 0.92 if eval_model == 'gpt' else 0.88,
                'message': f'领域测评完成，评测大模型：{eval_model}'
            }
            tasks[task_id] = {'status': 'finished', 'progress': 100, 'result': result}
        except Exception as e:
            tasks[task_id] = {'status': 'error', 'progress': 0, 'error': str(e)}
    threading.Thread(target=task).start()
    return jsonify({'task_id': task_id})

@app.route('/api/evaluate/status/<task_id>')
def get_status(task_id):
    return jsonify(tasks.get(task_id, {'status': 'not_found'}))

@app.route('/api/evaluate/result/<task_id>')
def get_result(task_id):
    info = tasks.get(task_id)
    if info and info['status'] == 'finished':
        import pandas as pd
        df = pd.read_csv(info['result'])
        return df.to_json(orient='records', force_ascii=False)
    return jsonify({'error': 'Result not ready'})

@app.route('/api/evaluate/download/<task_id>')
def download_result(task_id):
    info = tasks.get(task_id)
    if info and info['status'] == 'finished':
        dir_path, filename = os.path.split(info['result'])
        return send_from_directory(dir_path, filename, as_attachment=True)
    return jsonify({'error': 'Result not ready'})

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_vue(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(debug=True) 