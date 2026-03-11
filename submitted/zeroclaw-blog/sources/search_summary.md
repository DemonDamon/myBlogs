# ZeroClaw 搜索摘要

## 搜索时间
2026-02-17

## GitHub 仓库
- **仓库地址**: https://github.com/zeroclaw-labs/zeroclaw
- **组织**: zeroclaw-labs
- **项目名**: zeroclaw

## 核心特性

### 性能指标
- 内存占用: 不到 5MB
- 启动时间: 10 毫秒以内
- 编译后二进制: 3.4MB
- 对比 OpenClaw: 需要 >1GB 内存，启动需 500+ 秒（两个数量级差距）

### 架构设计
- 用 Rust 编写的全自主 AI 助手框架
- 8 个核心 trait 构成（热插拔）:
  - AI: AI 模型
  - 消息通道
  - 记忆系统
  - 工具集
  - 可观测性
  - 运行时
  - 安全策略
  - 隧道服务

### 记忆系统
- 零外部依赖实现
- 纯用 SQLite 实现:
  - 向量数据库（BLOB 存储）
  - 全文检索（FTS5）
  - 混合搜索（自定义权重函数融合）

### 安全设计
- 网关默认只绑定本地地址
- 首次连接需要 6 位配对码
- 文件操作被限制在工作区内
- 14 个系统目录和 4 个敏感配置文件被硬编码屏蔽
- 空的白名单 = 拒绝一切（默认拒绝）

### 兼容性
- 支持 22 个 AI 供应商
- 8 个消息通道
- 50+ 集成服务
- 平台: Mac, 树莓派（$10 硬件）
- 架构: ARM, x86, RISC-V

## 找到的高价值页面

1. **腾讯新闻**: 当AI助手只需要5MB内存和10美元硬件
   - URL: https://news.qq.com/rain/a/20260215A0725400
   - 描述: 深度介绍 ZeroClaw 的设计哲学、性能指标、架构和安全设计

2. **博客园**: 用 ZeroClaw 结合 SNS 打造每日新闻邮件推送助手
   - URL: https://www.cnblogs.com/peacemaple/p/19620712
   - 描述: 实战案例，展示如何使用 ZeroClaw 构建应用

3. **博客园**: NuClaw - 更快、更安全、更小巧的 OpenClaw
   - URL: https://www.cnblogs.com/gyc567/p/19571485
   - 描述: 类似项目对比，用 Rust 重构 OpenClaw 理念

4. **网易**: 代码暴减99.9%!独立开发者仅用500行代码做出安全版OpenClaw
   - URL: https://www.163.com/dy/article/KLJ9UTMQ05566ZHB.html
   - 描述: NanoClaw 项目介绍，极简架构实现

5. **ODaily**: OpenClaw 极简部署:最快 1 分钟搞定,纯小白友好教程
   - URL: https://www.odaily.news/zh-CN/post/5209317
   - 描述: 部署方案横评，包含多种部署选项对比

6. **GitHub**: zeroclaw-labs/zeroclaw 仓库（需直接访问）
   - URL: https://github.com/zeroclaw-labs/zeroclaw
   - 描述: 官方仓库，源代码和文档

## 搜索策略

已搜索的关键词:
- ZeroClaw Rust AI framework architecture design
- ZeroClaw zeroclaw-labs GitHub repository
- ZeroClaw memory performance benchmark comparison
- ZeroClaw security design sandbox isolation
- ZeroClaw trait architecture hot pluggable design
- ZeroClaw SQLite vector database FTS5 hybrid search
- ZeroClaw deployment raspberry pi ARM x86 RISC-V

## 待补充
- 官方 README 文档
- 架构图和系统设计文档
- 使用教程和示例代码
- 性能基准测试数据
- 与竞品对比的详细分析
