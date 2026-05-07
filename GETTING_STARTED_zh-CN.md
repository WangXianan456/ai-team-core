# 开始使用（30分钟）

## 1. 复制任务模板

把 `templates/task_card.md` 复制为 `tasks/TASK-002-你的任务名.md`，并填完整目标/范围/验收标准。

## 2. 按流程执行

1. PM：补全任务卡
2. Dev：实现改动并记录自测
3. QA：按验收标准验证
4. Ops：填写发布检查清单
5. Orchestrator（你）：最终审批

流程参考：`workflows/delivery_flow.md`

也可以用命令行推进状态：

```bash
python scripts/orchestrate.py list
python scripts/orchestrate.py next TASK-001
python scripts/orchestrate.py advance TASK-001
```

状态推进日志会自动写入：`logs/orchestration_events.jsonl`

周报统计命令：

```bash
python scripts/report.py weekly
```

记录 token 和费用统计：

```bash
python scripts/log_usage.py --task TASK-001 --role dev --model gpt-5.5 --input 1200 --output 800
python scripts/cost_report.py weekly
python scripts/autopilot.py daily --output reports/daily-YYYY-MM-DD.md
python scripts/dependency_audit.py plan --repo F:\path\to\business-repo
python scripts/sync_external.py
```

## 3. 记录决策

如涉及架构或重大取舍，复制 `templates/adr.md` 到 `decisions/ADR-xxx.md`。

## 4. 周度复盘

复制 `templates/weekly_review.md`，每周更新一次：

- 交付速度
- 质量问题
- AI成本
- 下周优化项

大项目请先建 EPIC（`templates/epic_card.md`），再拆 TASK 并写 `Depends On`。
