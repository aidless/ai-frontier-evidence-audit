#!/usr/bin/env python3
"""E2 多投影 full 结果分析：把原始 JSON 折成可引用的判决，带 --selftest 反证。

诚实边界：这是合成方法学诊断（synthetic diagnostic），不是 CF-WAM 数值复现。
两臂参数量相等（68748），但 multi 输入维度更大——信息互补带来的优势不免费。
"""
import argparse, json, sys

def analyze(d):
    agg = d['aggregate']
    s, m = agg['single'], agg['multi']
    # Q1: in-dist 误差比
    q1_ratio = round(m['in_dist_mse'] / max(s['in_dist_mse'], 1e-9), 4)
    # Q2: 跨本体退化比之差（越小越鲁棒）
    q2_gap = round(s['degradation_ratio'] - m['degradation_ratio'], 3)
    # 跨 seed 一致性：每个 seed multi_deg < single_deg？
    consistent = all(r['multi']['degradation_ratio'] < r['single']['degradation_ratio']
                     for r in d['per_seed'])
    verdict = {
        'q1_multi_better_indist': bool(d['verdict']['q1_multi_better_indist']),
        'q1_error_ratio_multi_over_single': q1_ratio,
        'q2_multi_more_robust': bool(d['verdict']['q2_multi_more_robust']),
        'q2_degradation_gap': q2_gap,
        'q2_consistent_across_seeds': consistent,
        'params_equal': s['n_params'] == m['n_params'],
        'h2_supported': bool(d['verdict']['q1_multi_better_indist'] and
                             d['verdict']['q2_multi_more_robust'] and consistent),
    }
    return verdict

def selftest():
    # 注入假数据：若 multi 更差/不一致，判定必须能红
    bad = {'aggregate': {'single': {'in_dist_mse': 0.01, 'cross_emb_mse': 0.05,
                                    'degradation_ratio': 5.0, 'n_params': 100},
                         'multi': {'in_dist_mse': 0.02, 'cross_emb_mse': 0.20,
                                   'degradation_ratio': 10.0, 'n_params': 100}},
           'per_seed': [{'single': {'degradation_ratio': 5.0},
                         'multi': {'degradation_ratio': 10.0}}],
           'verdict': {'q1_multi_better_indist': False, 'q2_multi_more_robust': False}}
    v = analyze(bad)
    assert not v['h2_supported'], 'gate must fail on bad data'
    assert not v['q2_consistent_across_seeds'], 'consistency check must catch inconsistency'
    print(json.dumps({'selftest': 'PASS', 'bad_h2_supported': v['h2_supported']}))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', default='world-model-nsp/evidence/nsp-multiview-full-result.json')
    ap.add_argument('--out', default=None)
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest:
        selftest(); return
    d = json.load(open(a.input, encoding='utf-8'))
    v = analyze(d)
    txt = json.dumps(v, indent=2, ensure_ascii=False)
    if a.out:
        open(a.out, 'w', encoding='utf-8').write(txt + '\n')
        print('WROTE', a.out)
    print(txt)

if __name__ == '__main__':
    main()
