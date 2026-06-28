"""
Demo: 使用 UESTC 模板生成一份完整的中期/后期报告。

运行: python examples/demo_report.py
输出: output/demo_midterm.docx 和 output/demo_final.docx
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from uestc_doc import ProjectMeta
from uestc_doc.templates.uestc_thesis import build_report, ReportType


def make_meta():
    """创建示例项目元数据 — 请替换为你的实际信息。"""
    return ProjectMeta(
        course_name="综合设计项目",
        college="XX学院",
        semester="2025-2026 学年 2 学期",
        project_name="XXX项目",
        advisor="指导教师姓名",
        students=[
            {"name": "组长姓名", "id": "2024XXXXXX"},
            {"name": "成员2", "id": "2024XXXXXX"},
            {"name": "成员3", "id": "2024XXXXXX"},
        ],
        abstract_text=(
            "本报告聚焦于示例语言系统的设计与实现。"
            "系统以项目源码为输入，经过输入解析、结构分析构建AST，"
            "通过Visitor设计模式生成中间表示兼容的IR，经自研PipelineManager框架"
            "调度的多级优化Pass深度优化后，最终输出目标平台汇编代码。"
        ),
        keywords_text="示例语言；系统设计；中间表示 IR；PipelineManager；代码优化",
    )


def demo_midterm():
    """生成中期报告示例。"""
    meta = make_meta()
    doc = build_report(meta, report_type=ReportType.MIDTERM,
        # ── 1.1 方案设计 ──
        design={
            'architecture_desc': (
                "本系统采用经典的三阶段流水线架构：前端（Tokenizer+Parser）→ "
                "中端（自研PipelineManager + 中间表示兼容IR）→ 后端（目标平台/目标平台）。"
            ),
            'modules': [
                ('前端设计', 3, [
                    "输入解析采用Tokenizer生成DFA，识别所有示例 Token类型。",
                    "结构分析采用GNU Parser LALR(1)，在归约时直接构建AST。",
                ]),
                ('中端设计', 3, [
                    "IR采用与中间表示兼容的指令体系，共33种指令类型。",
                    "PipelineManager基于CRTP+类型擦除模式，支持非侵入式扩展。",
                ]),
            ],
        },
        # ── 1.2 推理分析 ──
        reasoning={
            'complex_problems': [
                ('静态单赋值形式的构建与销毁', [
                    "核心结构形式是现代系统优化的数学基础。构建核心结构需要在迭代支配边界上放置汇合节点。",
                    "变量重命名阶段需在支配树上DFS遍历，维护每个变量的版本栈。",
                ]),
                ('寄存器分配与溢出处理', [
                    "寄存器分配是将逻辑上无限的虚拟寄存器映射到硬件有限的物理寄存器的NP完全问题。",
                    "本后端采用贪心+活跃区间分析算法，支持传送亲和性优化和迭代式溢出回退。",
                ]),
            ],
        },
        # ── 1.3 具体实现 ──
        impl={
            'modules': [
                ('前端实现', [
                    "Tokenizer输入解析器：由src/yacc/example.l规则文件生成，每次调用yylex()返回Token。",
                    "IRGenerator（983行）：采用Visitor模式+栈驱动上下文管理，为每个AST节点生成IR。",
                ]),
                ('中端Analysis Pass', [
                    "支配树分析（Semi-NCA算法）：O(1)支配判定，基于DFS进出时间戳。",
                    "RangeAnalysis（1708行）：同时追踪IntRange/FloatRange/KnownBits三通道格信息。",
                ]),
            ],
            'code_examples': [
                ('核心算法核心算法：', '// Phi插入: IDF计算\nfor (auto &alloca : allocas) {\n    computeIDF(alloca, phi_blocks);\n}', 'cpp'),
            ],
        },
        # ── 1.4 知识技能学习 ──
        skills={
            'areas': [
                ('一、编译理论与算法', [
                    ('核心结构与数据流分析', '掌握了支配树/IDF/变量重命名等核心算法。'),
                    ('抽象解释', '理解了格理论/Widening/Narrowing的收敛加速技术。'),
                ]),
                ('二、软件工程能力', [
                    ('大型C++项目架构', '实践了分层模块化架构，约24000行代码的组织与管理。'),
                ]),
            ],
        },
        # ── 第二章 问题与方案 ──
        problems={
            'problems': [
                ('问题一：核心模块构建的复杂性', [
                    '核心算法涉及6个阶段的复杂变换，变量重命名的正确性极难保证。',
                ]),
                ('问题二：别名分析精度', [
                    'GEP的灵活偏移和PHI多来源聚合使基址追踪困难，分析被迫退回MayAlias。',
                ]),
            ],
            'solutions': [
                ('方案一：Pruned 核心结构 + 严格栈管理', [
                    '引入活跃变量信息修剪冗余Phi，减少30-40%无用节点。',
                    'Rename阶段记录栈深度，确保路径栈操作严格匹配。',
                ]),
            ],
        },
        # ── 第三章 完成度与计划 ──
        plan={
            'completion_rows': [
                ["前端", "词法+结构分析", "100%", "测试通过"],
                ["中端", "PipelineManager框架", "100%", "CRTP+类型擦除完成"],
                ["中端", "30个Transform Pass", "100%", "语义保持验证通过"],
                ["后端", "指令选择+寄存器分配", "85%", "核心算法完成"],
                ["测试", "全链路集成测试", "进行中", "目标100% AC"],
            ],
            'plan_phases': [
                ('第一阶段：后端完善', '第13-14周', [
                    "完成后端边界指令覆盖与全链路贯通测试。",
                ]),
                ('第二阶段：性能调优', '第15-16周', [
                    "Pass执行序列调优，Benchmark性能对标。",
                ]),
            ],
        },
    )
    os.makedirs('output', exist_ok=True)
    doc.save('output/demo_midterm.docx')
    print("[OK] Generated: output/demo_midterm.docx")


def demo_final():
    """生成后期报告示例。"""
    meta = make_meta()
    doc = build_report(meta, report_type=ReportType.FINAL,
        acknowledgments=(
            "感谢指导教师在本项目中的悉心指导。\n"
            "感谢团队成员的通力协作与相互支持。\n"
            "感谢课程平台提供的学习与实践机会。"
        ),
        # ── 1.1 需求分析与建模 ──
        requirements={
            'functional_reqs': [
                ('FR1: 输入解析与结构分析', '支持完整示例词法和语法定义，构建完整AST。'),
                ('FR2: 中间代码生成', '遍历AST生成中间表示兼容IR，覆盖所有核心IR指令。'),
                ('FR3: 中端优化', '提供可扩展的优化管线，实现7个Analysis+30个Transform Pass。'),
            ],
            'nonfunctional_reqs': [
                ('NFR1: 正确性', '通过示例竞赛测试集，AC率≥95%。'),
                ('NFR2: 性能', '优化后IR指令数减少≥40%，目标代码超越GCC -O2。'),
            ],
        },
        # ── 1.2 复杂工程问题 ──
        problems_induction={
            'problems': [
                ('核心模块构建与销毁', [
                    '需要在IDF上精确放置汇合节点，同时利用Pruned 核心结构减少冗余。',
                    '变量重命名必须精确处理控制流汇合，任何栈操作不匹配都会导致错误核心结构。',
                ]),
                ('全局值编号与部分冗余消除', [
                    'GVN-PRE融合了CSE和PRE两项经典优化，1311行实现为本项目最大Transform Pass。',
                ]),
            ],
        },
        # ── 3.2 核心功能完成 ──
        core_completion={
            'features': [
                ["前端解析", "解析+AST+代码生成", "全部完成", "✅ 完成", "LLI验证通过"],
                ["中端优化", "核心分析模块", "全部完成", "✅ 完成", "逐Pass语义保持"],
                ["目标平台后端", "ISel+RA+Frame+Peephole", "核心完成", "⚠ 调优中", "QEMU执行正确"],
                ["目标平台后端", "AArch64 ISel+RA", "基础完成", "⚠ 完善中", "Cortex-A53验证"],
            ],
        },
        # ── 3.3 仿真效果 ──
        simulation={
            'test_results': [
                ["功能测试", "138", "138", "100%", ""],
                ["性能测试", "12", "12", "100%", "vs GCC -O2: 112.5%"],
                ["隐藏测试", "10", "10", "100%", ""],
            ],
        },
        # ── 第四章 分工协作 ──
        team={
            'members': [
                ["组长", "系统架构", "PipelineManager/RangeAnalysis/GVN-PRE", "35%"],
                ["成员2", "前端+测试", "Tokenizer/Parser/AST/IRGen/测试体系", "35%"],
                ["成员3", "后端", "目标平台 ISel/RegAlloc/目标平台", "30%"],
            ],
            'tools': [
                ("Git + GitHub", "版本控制与代码评审"),
                ("VS Code + CMake", "开发环境与构建系统"),
                ("飞书/钉钉", "日常沟通与文档协作"),
            ],
        },
    )
    os.makedirs('output', exist_ok=True)
    doc.save('output/demo_final.docx')
    print("[OK] Generated: output/demo_final.docx")


if __name__ == '__main__':
    print("=" * 60)
    print("UESTC-doc-writing Demo")
    print("=" * 60)
    demo_midterm()
    demo_final()
    print("\n在 Microsoft Word 中打开 output/ 目录下的文件，右键目录 → 更新域。")
