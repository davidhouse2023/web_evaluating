import os

def run_cmmlu(params):
    """
    params: dict, 包含模型路径、few-shot等参数
    返回结果csv路径
    """
    # 示例参数获取
    model_path = params.get('model_path')
    data_dir = params.get('data_dir', '../../evaluating/CMMLU/data')
    save_dir = params.get('save_dir', '../results/cmmlu')
    num_few_shot = params.get('num_few_shot', 5)
    max_length = params.get('max_length', 2048)
    cot = params.get('cot', False)
    # 这里以llama3.py为例，实际可根据需要切换
    script = '../../evaluating/CMMLU/src/llama3.py'
    cmd = f"python {script} --model_path {model_path} --data_dir {data_dir} --save_dir {save_dir} --num_few_shot {num_few_shot} --max_length {max_length} {'--cot' if cot else ''}"
    os.system(cmd)
    # 假设结果为save_dir下的results_overall.csv
    result_path = os.path.join(save_dir + f'_{num_few_shot}_shot', 'results_overall.csv')
    return result_path 