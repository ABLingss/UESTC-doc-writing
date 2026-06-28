"""
UESTC 综合设计报告 — 各章节骨架函数。

支持两种报告类型:
- 中期报告: 3章结构
- 后期报告: 4章+致谢结构

所有函数通过 kwargs 注入项目特定内容，不包含任何硬编码的个人/学校信息。
"""

from uestc_doc import (
    ProjectMeta,
    add_heading, add_body_para, add_bold_para,
    add_list_item, add_code_block, add_table,
)


# ═══════════════════════════════════════════════════════════════
# 中期报告: 1.1 方案设计
# ═══════════════════════════════════════════════════════════════

def write_design_solution(doc, meta: ProjectMeta, **kwargs):
    """1.1 针对工程问题的方案设计。

    kwargs:
        architecture_desc: str — 总体架构描述
        modules: [(title, level, [paragraphs]), ...] — 各模块设计方案
    """
    arch_desc = kwargs.get('architecture_desc', '')
    modules = kwargs.get('modules', [])

    if arch_desc:
        add_body_para(doc, arch_desc)
    else:
        add_body_para(doc,
            "（请描述系统总体架构与技术路线。建议包含：分层架构设计、"
            "技术选型理由、工具链选择、模块划分方案。）"
        )

    if modules:
        for title, level, paras in modules:
            add_heading(doc, title, level=level)
            for text in paras:
                add_body_para(doc, text)
    else:
        add_heading(doc, "核心模块设计", level=3)
        add_body_para(doc,
            "（请逐一描述各核心模块的设计方案：数据结构选型、接口定义、算法选择、设计模式应用。）"
        )


# ═══════════════════════════════════════════════════════════════
# 中期报告: 1.2 推理分析
# ═══════════════════════════════════════════════════════════════

def write_reasoning_analysis(doc, meta: ProjectMeta, **kwargs):
    """1.2 针对工程问题的推理分析。

    kwargs:
        functional_reqs: [(name, desc), ...]
        nonfunctional_reqs: [(name, desc), ...]
        complex_problems: [(title, [paragraphs]), ...]
    """
    functional_reqs = kwargs.get('functional_reqs', [])
    nonfunctional_reqs = kwargs.get('nonfunctional_reqs', [])
    complex_problems = kwargs.get('complex_problems', [])

    # 需求分析
    add_heading(doc, "需求分析概述", level=3)
    add_body_para(doc, "（请概述项目整体需求，从功能性和非功能性两个维度进行分析。）")

    add_heading(doc, "功能性需求", level=3)
    if functional_reqs:
        for name, desc in functional_reqs:
            add_bold_para(doc, name)
            add_body_para(doc, desc)
    else:
        add_body_para(doc, "（请列出核心功能性需求。）")

    add_heading(doc, "非功能性需求", level=3)
    if nonfunctional_reqs:
        for name, desc in nonfunctional_reqs:
            add_bold_para(doc, name)
            add_body_para(doc, desc)
    else:
        add_body_para(doc, "（请列出非功能性需求：正确性、性能、可扩展性、可维护性等。）")

    # 复杂工程问题归纳
    add_heading(doc, "复杂工程问题归纳", level=3)
    if complex_problems:
        for i, (title, lines) in enumerate(complex_problems, 1):
            label = f"复杂工程问题{i}：{title}"
            add_bold_para(doc, label)
            for line in lines:
                add_body_para(doc, line)
    else:
        add_body_para(doc,
            "（请归纳本课题涉及的核心复杂工程问题。每个问题需包含："
            "问题定义、技术难点分析、工程挑战、本项目的解决策略。）"
        )


# ═══════════════════════════════════════════════════════════════
# 中期报告: 1.3 具体实现
# ═══════════════════════════════════════════════════════════════

def write_implementation_progress(doc, meta: ProjectMeta, **kwargs):
    """1.3 针对工程问题的具体实现。

    kwargs:
        modules: [(name, [paragraphs]), ...]
        code_examples: [(caption, code, language), ...]
    """
    modules = kwargs.get('modules', [])
    code_examples = kwargs.get('code_examples', [])

    if modules:
        for mod_name, content_list in modules:
            add_heading(doc, mod_name, level=3)
            for text in content_list:
                add_body_para(doc, text)
    else:
        add_body_para(doc,
            "（请描述已完成的实现工作：核心模块的实现方法、关键算法、"
            "数据结构、代码组织方式。中期阶段可侧重于已完成的部分。）"
        )

    if code_examples:
        for caption, code, lang in code_examples:
            if caption:
                add_body_para(doc, caption)
            add_code_block(doc, code, language=lang)


# ═══════════════════════════════════════════════════════════════
# 中期报告: 1.4 知识技能学习
# ═══════════════════════════════════════════════════════════════

def write_knowledge_skills(doc, meta: ProjectMeta, **kwargs):
    """1.4 知识技能学习情况。

    kwargs:
        areas: [(area_title, [(sub_title, desc), ...]), ...]
    """
    areas = kwargs.get('areas', [])

    if areas:
        for area_title, items in areas:
            add_bold_para(doc, area_title)
            if items:
                for sub_title, desc in items:
                    add_body_para(doc, f"（{sub_title}）{desc}")
    else:
        add_bold_para(doc, "一、理论知识")
        add_body_para(doc, "（请描述学到的核心理论知识。）")
        add_bold_para(doc, "二、工程技能")
        add_body_para(doc, "（请描述提升的工程实践能力。）")
        add_bold_para(doc, "三、工具链掌握")
        add_body_para(doc, "（请列出掌握的工具和技术栈。）")
        add_bold_para(doc, "四、科研素养")
        add_body_para(doc, "（请总结科研习惯的养成。）")


# ═══════════════════════════════════════════════════════════════
# 共用: 第二章 存在问题与解决方案
# ═══════════════════════════════════════════════════════════════

def write_problems_and_solutions(doc, meta: ProjectMeta, **kwargs):
    """第二章: 存在问题与解决方案 (中期和后期共用)。

    kwargs:
        problems: [(title, [paragraphs]), ...]
        solutions: [(title, [paragraphs]), ...]
    """
    problems = kwargs.get('problems', [])
    solutions = kwargs.get('solutions', [])

    add_heading(doc, "2.1 存在的主要问题", level=2)
    if problems:
        for title, lines in problems:
            add_bold_para(doc, title)
            for line in lines:
                add_body_para(doc, line)
    else:
        add_body_para(doc,
            "（请归纳项目推进过程中遇到的主要技术问题和管理挑战。"
            "建议包含：问题描述、产生原因、影响范围。）"
        )

    add_heading(doc, "2.2 解决方案", level=2)
    if solutions:
        for title, lines in solutions:
            add_bold_para(doc, title)
            for line in lines:
                add_body_para(doc, line)
    else:
        add_body_para(doc,
            "（针对上述问题，请逐一阐述解决方案。"
            "建议包含：解决思路、技术选型理由、实施效果。）"
        )


# ═══════════════════════════════════════════════════════════════
# 中期报告: 第三章 前期任务完成度与后续实施计划
# ═══════════════════════════════════════════════════════════════

def write_completion_and_plan(doc, meta: ProjectMeta, **kwargs):
    """第三章: 前期任务完成度与后续实施计划 (仅中期报告)。

    kwargs:
        completion_rows: [(module, subtask, completion, status), ...]
        plan_phases: [(phase_title, time_range, [items]), ...]
    """
    completion_rows = kwargs.get('completion_rows', [])
    plan_phases = kwargs.get('plan_phases', [])

    add_heading(doc, "3.1 前期任务完成度", level=2)
    if completion_rows:
        add_table(doc,
            ["模块", "子任务", "完成度", "验证状态"],
            completion_rows,
            caption="表3-1 前期任务完成度总览"
        )
    else:
        add_body_para(doc,
            "（请以表格形式列出各模块子任务的完成度百分比和验证状态。）"
        )

    add_heading(doc, "3.2 后续实施计划", level=2)
    if plan_phases:
        for phase_title, time_range, items in plan_phases:
            add_bold_para(doc, f"{phase_title}（{time_range}）")
            for item in items:
                add_body_para(doc, item)
    else:
        add_body_para(doc,
            "（请按时间阶段列出后续工作计划，每阶段包含核心目标和验收标准。）"
        )


# ═══════════════════════════════════════════════════════════════
# 后期报告: 1.1 需求分析与建模
# ═══════════════════════════════════════════════════════════════

def write_requirements_modeling(doc, meta: ProjectMeta, **kwargs):
    """1.1 需求分析与建模 (仅后期报告)。

    kwargs:
        overview: str
        functional_reqs: [(name, desc), ...]
        nonfunctional_reqs: [(name, desc), ...]
        models: [(name, desc), ...]  — 用例图/DFD/ER图等
    """
    overview = kwargs.get('overview', '')
    functional_reqs = kwargs.get('functional_reqs', [])
    nonfunctional_reqs = kwargs.get('nonfunctional_reqs', [])
    models = kwargs.get('models', [])

    if overview:
        add_body_para(doc, overview)
    else:
        add_body_para(doc,
            "（请概述项目背景与需求分析范围，说明需求获取的方法与过程。）"
        )

    add_heading(doc, "功能性需求", level=3)
    if functional_reqs:
        for name, desc in functional_reqs:
            add_bold_para(doc, name)
            add_body_para(doc, desc)
    else:
        add_body_para(doc, "（请列出所有功能性需求，建议按模块或用户故事组织。）")

    add_heading(doc, "非功能性需求", level=3)
    if nonfunctional_reqs:
        for name, desc in nonfunctional_reqs:
            add_bold_para(doc, name)
            add_body_para(doc, desc)
    else:
        add_body_para(doc, "（请列出性能、可靠性、安全性、可维护性等非功能性需求。）")

    if models:
        add_heading(doc, "需求建模", level=3)
        for name, desc in models:
            add_bold_para(doc, name)
            add_body_para(doc, desc)


# ═══════════════════════════════════════════════════════════════
# 后期报告: 1.2 复杂工程问题归纳
# ═══════════════════════════════════════════════════════════════

def write_complex_problems(doc, meta: ProjectMeta, **kwargs):
    """1.2 复杂工程问题归纳 (仅后期报告)。

    kwargs:
        problems: [(title, [paragraphs]), ...]
    """
    problems = kwargs.get('problems', [])

    if problems:
        for i, (title, lines) in enumerate(problems, 1):
            add_bold_para(doc, f"问题{i}：{title}")
            for line in lines:
                add_body_para(doc, line)
    else:
        add_body_para(doc,
            "（请归纳本课题涉及的核心复杂工程问题。每个问题需包含："
            "问题背景、技术难点、涉及的多学科知识、工程挑战、本项目的创新解决思路。）"
        )


# ═══════════════════════════════════════════════════════════════
# 后期报告: 1.3 实施方案与可行性研究
# ═══════════════════════════════════════════════════════════════

def write_feasibility_study(doc, meta: ProjectMeta, **kwargs):
    """1.3 实施方案与可行性研究 (仅后期报告)。

    kwargs:
        tech_route: str — 技术路线描述
        alternatives: [(approach, pros, cons), ...] — 方案对比
        feasibility: str — 可行性分析结论
    """
    tech_route = kwargs.get('tech_route', '')
    alternatives = kwargs.get('alternatives', [])
    feasibility = kwargs.get('feasibility', '')

    add_heading(doc, "技术路线", level=3)
    if tech_route:
        add_body_para(doc, tech_route)
    else:
        add_body_para(doc,
            "（请描述整体技术路线：技术选型、工具链、开发环境、架构方案。）"
        )

    if alternatives:
        add_heading(doc, "方案对比与选择", level=3)
        headers = ["方案", "优势", "劣势"]
        rows = [[a, p, c] for a, p, c in alternatives]
        add_table(doc, headers, rows, caption="表1-1 技术方案对比")

    add_heading(doc, "可行性分析", level=3)
    if feasibility:
        add_body_para(doc, feasibility)
    else:
        add_body_para(doc,
            "（请从技术可行性、时间可行性、资源可行性等维度进行分析。）"
        )


# ═══════════════════════════════════════════════════════════════
# 后期报告: 3.1 项目执行过程概述
# ═══════════════════════════════════════════════════════════════

def write_execution_overview(doc, meta: ProjectMeta, **kwargs):
    """3.1 项目执行过程概述 (仅后期报告)。

    kwargs:
        phases: [(phase_name, time_range, desc), ...]
        methodology: str — 开发方法论 (如敏捷/迭代/瀑布)
    """
    phases = kwargs.get('phases', [])
    methodology = kwargs.get('methodology', '')

    if methodology:
        add_body_para(doc, f"本项目采用{methodology}开发方法。")

    if phases:
        for name, time_range, desc in phases:
            add_bold_para(doc, f"{name}（{time_range}）")
            add_body_para(doc, desc)
    else:
        add_body_para(doc,
            "（请按时间顺序描述项目的执行过程，包括各阶段的起止时间、"
            "主要工作内容、关键里程碑。）"
        )


# ═══════════════════════════════════════════════════════════════
# 后期报告: 3.2 核心功能完成情况
# ═══════════════════════════════════════════════════════════════

def write_core_completion(doc, meta: ProjectMeta, **kwargs):
    """3.2 核心功能完成情况 (仅后期报告)。

    kwargs:
        features: [(name, planned, actual, status, notes), ...]
    """
    features = kwargs.get('features', [])

    if features:
        headers = ["功能模块", "计划内容", "实际完成", "状态", "备注"]
        add_table(doc, headers, features, caption="表3-1 核心功能完成情况")
    else:
        add_body_para(doc,
            "（请以表格形式列出各核心功能的计划内容、实际完成情况、"
            "完成状态和备注说明。）"
        )


# ═══════════════════════════════════════════════════════════════
# 后期报告: 3.3 仿真运行效果与仿真效果
# ═══════════════════════════════════════════════════════════════

def write_simulation_results(doc, meta: ProjectMeta, **kwargs):
    """3.3 仿真运行效果与仿真效果 (仅后期报告)。

    kwargs:
        test_env: str — 测试环境描述
        test_results: [(category, cases, passed, rate, notes), ...]
        analysis: str — 结果分析
    """
    test_env = kwargs.get('test_env', '')
    test_results = kwargs.get('test_results', [])
    analysis = kwargs.get('analysis', '')

    add_heading(doc, "测试环境", level=3)
    if test_env:
        add_body_para(doc, test_env)
    else:
        add_body_para(doc, "（请描述测试/仿真环境：硬件平台、软件版本、工具链。）")

    add_heading(doc, "测试结果", level=3)
    if test_results:
        headers = ["测试类别", "用例数", "通过数", "通过率", "备注"]
        add_table(doc, headers, test_results,
                  caption="表3-2 仿真/测试结果汇总")
    else:
        add_body_para(doc, "（请汇总仿真运行或测试的结果数据。）")

    if analysis:
        add_heading(doc, "结果分析", level=3)
        add_body_para(doc, analysis)


# ═══════════════════════════════════════════════════════════════
# 后期报告: 3.4 完成度评估
# ═══════════════════════════════════════════════════════════════

def write_completion_evaluation(doc, meta: ProjectMeta, **kwargs):
    """3.4 完成度评估 (仅后期报告)。

    kwargs:
        overall_rate: str — 总体完成度百分比
        dimensions: [(dim, self_score, evidence), ...]
        summary: str
    """
    overall_rate = kwargs.get('overall_rate', '')
    dimensions = kwargs.get('dimensions', [])
    summary = kwargs.get('summary', '')

    if overall_rate:
        add_body_para(doc, f"项目总体完成度：{overall_rate}")

    if dimensions:
        headers = ["评估维度", "自评得分", "支撑证据"]
        add_table(doc, headers, dimensions,
                  caption="表3-3 完成度自评")

    if summary:
        add_body_para(doc, summary)
    else:
        add_body_para(doc,
            "（请从功能完整性、性能达标度、代码质量、文档完整性等维度进行自评。）"
        )


# ═══════════════════════════════════════════════════════════════
# 后期报告: 第四章 分工协作与交流情况
# ═══════════════════════════════════════════════════════════════

def write_team_collaboration(doc, meta: ProjectMeta, **kwargs):
    """第四章: 分工协作与交流情况 (仅后期报告)。

    kwargs:
        members: [(name, role, tasks, contribution), ...]
        tools: [(tool, purpose), ...]
        meetings: [(date, topic, outcome), ...]
        summary: str
    """
    members = kwargs.get('members', [])
    tools = kwargs.get('tools', [])
    meetings = kwargs.get('meetings', [])
    summary = kwargs.get('summary', '')

    add_heading(doc, "4.1 团队分工", level=2)
    if members:
        headers = ["成员", "角色", "负责模块", "贡献度"]
        add_table(doc, headers, members, caption="表4-1 团队分工表")
    else:
        add_body_para(doc, "（请以表格形式列出各成员的分工和贡献。）")

    add_heading(doc, "4.2 协作工具与流程", level=2)
    if tools:
        for tool, purpose in tools:
            add_list_item(doc, f"{tool} — {purpose}")
    else:
        add_body_para(doc,
            "（请列出团队使用的协作工具：版本控制(Git)、文档协作、"
            "即时通讯、项目管理等。）"
        )

    add_heading(doc, "4.3 交流与沟通", level=2)
    if meetings:
        for date, topic, outcome in meetings:
            add_list_item(doc, f"{date}: {topic} — {outcome}")
    else:
        add_body_para(doc,
            "（请描述团队的沟通机制：例会制度、代码评审流程、技术讨论方式等。）"
        )

    if summary:
        add_heading(doc, "4.4 协作总结", level=2)
        add_body_para(doc, summary)
