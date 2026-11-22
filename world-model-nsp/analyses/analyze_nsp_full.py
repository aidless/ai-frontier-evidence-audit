#!/usr/bin/env python3
"""
分析 nsp-full-result.json，产出对 H1 判据的诚实判定。
关键点：原始判据(slope 最低)会被 token 臂的量化地板假象污染，
因此同时报告"绝对长程误差"与"相对增长倍数"两个互补度量。
所有数字从 JSON 复算；--selftest 注入已知数据验证判定逻辑能红。
"""
import argparse, json, sys

D = None

def load(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)

def analyze(d):
    """返回每个臂的派生量 + 对 H1 的判定。用第 1 个 seed 的稠密曲线。"""
    r = d['per_seed'][0]
    out = {}
    for m in ('token', 'frame', 'state'):
        curve = {int(k): v for k, v in r[m]['mse'].items()}
        h1, hfar = min(curve), max(curve)
        e1, efar = curve[h1], curve[hfar]
        out[m] = {
            'mse_step1': round(e1, 6),
            'mse_far': round(efar, 6),
            'growth_ratio': round(efar / e1, 3),      # 相对增长倍数
            'slope': r[m]['slope'],
        }
    agg = d['aggregate']
    out['comparisons'] = {
        'state_vs_frame_far_error': round(agg['state']['mse_far_mean'] /
                                          agg['frame']['mse_far_mean'], 3),
        'state_vs_token_far_error': round(agg['state']['mse_far_mean'] /
                                          agg['token']['mse_far_mean'], 3),
        'state_step1_vs_token_step1': round(out['state']['mse_step1'] /
                                            out['token']['mse_step1'], 3),
        'action_ablation_ratio_mean': d['verdict']['action_ablation_ratio_mean'],
    }
    # 判定
    slope_lowest = min(('token', 'frame', 'state'), key=lambda m: agg[m]['slope_mean'])
    far_lowest = min(('token', 'frame', 'state'), key=lambda m: agg[m]['mse_far_mean'])
    out['verdict'] = {
        'original_criterion_slope_lowest': slope_lowest,
        'original_criterion_passed': slope_lowest == 'state',
        'absolute_far_error_lowest': far_lowest,
        'absolute_far_error_passed': far_lowest == 'state',
        'action_dependency_confirmed': d['verdict']['action_ablation_ratio_mean'] > 2.0,
    }
    return out

def selftest():
    # 合成：token 撞地板(slope 假低但绝对误差最高)、state 绝对最低
    fake = {
        'per_seed': [{'token': {'mse': {'1': 0.015, '100': 0.034}, 'slope': 0.12},
                      'frame': {'mse': {'1': 0.0008, '100': 0.0115}, 'slope': 0.40},
                      'state': {'mse': {'1': 0.0006, '100': 0.0035}, 'slope': 0.20}}],
        'aggregate': {
            'token': {'slope_mean': 0.12, 'mse_far_mean': 0.034},
            'frame': {'slope_mean': 0.40, 'mse_far_mean': 0.0115},
            'state': {'slope_mean': 0.20, 'mse_far_mean': 0.0035},
        },
        'verdict': {'action_ablation_ratio_mean': 100.0},
    }
    a = analyze(fake)
    assert a['verdict']['original_criterion_slope_lowest'] == 'token', a
    assert a['verdict']['original_criterion_passed'] is False, a
    assert a['verdict']['absolute_far_error_lowest'] == 'state', a
    assert a['verdict']['absolute_far_error_passed'] is True, a
    assert a['verdict']['action_dependency_confirmed'] is True, a
    # 反证：若 state 绝对误差不是最低，判定必须翻 (装置能红)
    fake2 = json.loads(json.dumps(fake))
    fake2['aggregate']['state']['mse_far_mean'] = 0.05
    a2 = analyze(fake2)
    assert a2['verdict']['absolute_far_error_passed'] is False, a2
    print(json.dumps({'selftest': 'PASS',
                      'floor_illusion_detected': a['verdict']['original_criterion_slope_lowest'] == 'token',
                      'counterfactual_flips': True}, ensure_ascii=False))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', default='world-model-nsp/evidence/nsp-full-result.json')
    ap.add_argument('--out', default=None)
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest:
        selftest(); return
    res = analyze(load(a.input))
    txt = json.dumps(res, indent=2, ensure_ascii=False)
    if a.out:
        open(a.out, 'w', encoding='utf-8').write(txt + '\n')
        print('WROTE', a.out)
    print(txt)

if __name__ == '__main__':
    main()
