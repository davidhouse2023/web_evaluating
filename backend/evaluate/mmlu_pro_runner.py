import os

def run_mmlu_pro(params):
    """
    params: dict, 包含模型路径等参数
    返回结果json路径
    """
    model_path = params.get('model_path')
    output_dir = params.get('output_dir', '../results/mmlu_pro')
    selected_subjects = params.get('selected_subjects', 'all')
    # 以evaluate_from_local.py为例
    script = '../../evaluating/MMLU-Pro/evaluate_from_local.py'
    cmd = f"python {script} --model_path {model_path} --output_dir {output_dir} --selected_subjects {selected_subjects}"
    os.system(cmd)
    # 假设结果为output_dir下的summary.json
    result_path = os.path.join(output_dir, 'summary.json')
    return result_path 