# 🚀 快速运行指南

## 直接运行（无需安装）

```bash
# 进入项目目录
cd /Users/damon/myWork/myBlog/Agent-First/agent_first_agenticx

# 直接运行 demo
python demo.py
```

就这么简单！

## 运行要求

1. **Python 3.9+**
2. **AgenticX 已安装**（或者 AgenticX 源码在 `/Users/damon/myWork/AgenticX`）
3. **基础依赖**：
   ```bash
   pip install pydantic python-dateutil
   ```

## Demo 内容

运行 `demo.py` 将演示：

### 1️⃣ Probe 接口 - 智能化查询
- 元数据探索阶段
- 解决方案制定阶段（近似查询）
- 完整验证阶段（精确查询）

### 2️⃣ Agentic Memory Store - 语义缓存
- 5次相似查询
- 缓存命中演示
- 80-90% 冗余优化

### 3️⃣ Git 式分支管理 - 并行探索
- 创建多个测试分支
- 并行测试不同策略
- 合并或回滚

### 4️⃣ Agent 协作 - Field + Sleeper
- 架构说明
- 协作模式展示

## 文件说明

```
agent_first_agenticx/
├── demo.py              ← 🎯 主程序入口（直接运行）
├── RUN.md               ← 本文件（运行指南）
├── DESIGN.md            ← 详细设计文档
├── README.md            ← 使用手册
│
├── probes/              ← Probe 系统
├── agents/              ← Agent 系统
├── memory/              ← Memory 扩展
└── storage/             ← Storage 扩展
```

## 常见问题

### Q: 找不到 AgenticX？
**A:** 修改 `demo.py` 第 15 行的路径：
```python
agenticx_path = Path("/你的/AgenticX/路径")
```

### Q: 想看完整示例？
**A:** 查看 `examples/end_to_end_example.py`

### Q: 想了解设计？
**A:** 阅读 `DESIGN.md`

### Q: 想深入使用？
**A:** 阅读 `README.md`

## 下一步

1. **运行 demo** - 了解基本功能
2. **阅读 DESIGN.md** - 理解架构设计
3. **查看 examples/** - 学习具体用法
4. **修改代码** - 适配你的需求

---

**核心思想：基于 AgenticX，不重复造轮子！** 🎉

