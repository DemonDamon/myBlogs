import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';

const SANDBOX = '/tmp/teamai-sandbox-recall';
const TEAM_REPO = path.join(SANDBOX, 'team-repo');
const CLI = '/Users/damonli/myWork/myBlog/unsubmitted/teamai-cli-research/teamai-cli/dist/index.js';

fs.rmSync(SANDBOX, { recursive: true, force: true });
fs.mkdirSync(path.join(TEAM_REPO, 'learnings'), { recursive: true });
fs.mkdirSync(path.join(TEAM_REPO, 'docs'), { recursive: true });

const learnings = [
  {
    file: 'port-conflict-debug.md',
    content: `---
title: "MR review 抓到的端口冲突 bug 排查记录"
author: member-a
date: 2026-08-01
tags: [troubleshooting, networking]
---

## 背景
服务本地起两个实例时偶发 EADDRINUSE，MR review 才发现是默认端口写死导致。

## 解决方案
用环境变量覆盖默认端口，并在启动脚本里做端口探测。

## 经验总结
- 默认端口一律走配置注入
- 启动前先探测端口占用
`,
  },
  {
    file: 'deploy-config-best-practice.md',
    content: `---
title: "部署配置最佳实践"
author: member-b
date: 2026-08-05
tags: [deploy, config]
---

## 背景
多环境部署时配置漂移，staging 与 production 行为不一致。

## 解决方案
配置分层：基础配置 + 环境覆盖 + 密钥走 secret 管理。

## 经验总结
- 配置变更必须走 MR
- 密钥不允许明文进仓库
`,
  },
  {
    file: 'react-effect-cleanup.md',
    content: `---
title: "React useEffect 清理函数踩坑"
author: member-c
date: 2026-08-10
tags: [frontend, react]
---

## 背景
组件卸载后 setState 报 warning，定位是 WebSocket 订阅没有清理。

## 解决方案
在 useEffect 返回的清理函数里关闭订阅。

## 经验总结
- 所有订阅类副作用必须成对清理
`,
  },
  {
    file: 'db-migration-lock.md',
    content: `---
title: "数据库迁移锁导致发版阻塞"
author: member-d
date: 2026-08-12
tags: [database, migration]
---

## 背景
大表加字段时迁移锁表，发版流水线阻塞 40 分钟。

## 解决方案
改用 online schema change 工具分批变更。

## 经验总结
- 大表 DDL 必须走在线变更
- 迁移脚本要先在预发验证锁行为
`,
  },
];
for (const l of learnings) {
  fs.writeFileSync(path.join(TEAM_REPO, 'learnings', l.file), l.content);
}
fs.writeFileSync(
  path.join(TEAM_REPO, 'docs', 'api-conventions.md'),
  `---
title: "API 设计规范"
author: lead
date: 2026-07-20
tags: [api, design]
---

## 统一响应结构
所有 REST 接口返回 { code, message, data }。

## 分页
游标分页统一使用 cursor + limit 参数。
`,
);

fs.writeFileSync(
  path.join(TEAM_REPO, 'teamai.yaml'),
  `team: demo-team
description: sandbox team for recall testing
repo: ${TEAM_REPO}
provider: github
`,
);

execFileSync('git', ['init', '-q'], { cwd: TEAM_REPO });
execFileSync('git', ['add', '.'], { cwd: TEAM_REPO });
execFileSync('git', ['-c', 'user.email=t@t', '-c', 'user.name=t', 'commit', '-q', '-m', 'init team repo'], { cwd: TEAM_REPO });

fs.mkdirSync(path.join(SANDBOX, '.teamai'), { recursive: true });
fs.writeFileSync(
  path.join(SANDBOX, '.teamai', 'config.yaml'),
  `repo:
  localPath: ${TEAM_REPO}
  remote: ${TEAM_REPO}
  kind: git
username: damon
scope: user
`,
);

function recall(query, extraArgs = []) {
  console.log(`\n===== $ teamai recall ${extraArgs.join(' ')} "${query}" =====`);
  try {
    const out = execFileSync('node', [CLI, 'recall', ...extraArgs, ...query.split(/\s+/).filter(Boolean)], {
      cwd: '/tmp',
      env: { ...process.env, HOME: SANDBOX, NO_COLOR: '1' },
      encoding: 'utf-8',
      timeout: 60000,
    });
    console.log(out.trim());
  } catch (e) {
    console.log('exit:', e.status, '| stderr:', (e.stderr?.toString() || '').trim().split('\n').slice(-2).join(' | '));
  }
}

recall('port conflict');
recall('端口 冲突');
recall('useEffect 订阅 清理');
recall('数据库 迁移 锁');
recall('kubernetes istio service mesh');
recall('端口 探测', ['--check']);
recall('kubernetes istio', ['--check']);
recall('api 分页 cursor');
recall('锁 表 发版');
