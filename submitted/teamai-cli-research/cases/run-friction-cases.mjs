import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';

const SANDBOX = '/tmp/teamai-sandbox';
const CLI = '/Users/damonli/myWork/myBlog/unsubmitted/teamai-cli-research/teamai-cli/dist/index.js';

function setup() {
  fs.rmSync(SANDBOX, { recursive: true, force: true });
  fs.mkdirSync(path.join(SANDBOX, '.teamai', 'dashboard'), { recursive: true });
  fs.mkdirSync(path.join(SANDBOX, '.teamai', 'sessions'), { recursive: true });
}

function ts(offsetSec) {
  return new Date(Date.now() - offsetSec * 1000).toISOString();
}

function buildEvents({ sessionId, toolCallCount, interventions, promptSummary }) {
  const events = [];
  events.push({ type: 'session_start', timestamp: ts(3600), sessionId, tool: 'claude', cwd: '/tmp' });
  events.push({ type: 'prompt_submit', timestamp: ts(3590), sessionId, tool: 'claude', promptSummary });
  const toolNames = ['Bash', 'Read', 'Edit', 'Write', 'Grep', 'Glob', 'Skill', 'TodoWrite'];
  for (let i = 0; i < toolCallCount; i++) {
    events.push({
      type: 'tool_use',
      timestamp: ts(3580 - i * 5),
      sessionId,
      tool: 'claude',
      toolName: toolNames[i % toolNames.length],
    });
  }
  events.push({
    type: 'stop',
    timestamp: ts(60),
    sessionId,
    tool: 'claude',
    interventions,
    prompts: 3,
  });
  return events;
}

function runCase(name, hookData) {
  console.log(`\n===== ${name} =====`);
  try {
    const out = execFileSync('node', [CLI, 'contribute-check', '--stdin', '--tool', 'claude'], {
      input: JSON.stringify(hookData),
      env: { ...process.env, HOME: SANDBOX, NO_COLOR: '1' },
      encoding: 'utf-8',
      timeout: 30000,
    });
    console.log(out.trim() === '' ? '(no output — hint NOT triggered)' : out);
  } catch (e) {
    console.log('exit code:', e.status);
    console.log('stdout:', e.stdout?.toString().trim());
    console.log('stderr:', e.stderr?.toString().trim().split('\n').slice(-3).join('\n'));
  }
}

setup();

// Case A: 高摩擦 — 用户打断 2 次、拒绝工具 1 次、AI 重试失败工具 8 次（对应推文场景）
const eventsA = buildEvents({
  sessionId: 'friction-heavy-session',
  toolCallCount: 20,
  interventions: { interrupt: 2, toolReject: 1, toolError: 8 },
  promptSummary: 'Fix duplicate project-level Hook injection',
});
fs.writeFileSync(
  path.join(SANDBOX, '.teamai/dashboard/events.jsonl'),
  eventsA.map((e) => JSON.stringify(e)).join('\n') + '\n',
);
runCase('Case A: 高摩擦 session (interrupt=2, reject=1, toolError=8, toolCalls=20)', {
  session_id: 'friction-heavy-session',
  cwd: '/tmp',
});

// Case B: 顺滑 session — 30 次工具调用但零摩擦
setup();
const eventsB = buildEvents({
  sessionId: 'smooth-session',
  toolCallCount: 30,
  interventions: { interrupt: 0, toolReject: 0, toolError: 0 },
  promptSummary: 'Add unit tests for utils',
});
fs.writeFileSync(
  path.join(SANDBOX, '.teamai/dashboard/events.jsonl'),
  eventsB.map((e) => JSON.stringify(e)).join('\n') + '\n',
);
runCase('Case B: 顺滑 session (零摩擦, toolCalls=30)', {
  session_id: 'smooth-session',
  cwd: '/tmp',
});

// Case C: 有摩擦但工作量不足（toolCalls < 15 硬门槛）
setup();
const eventsC = buildEvents({
  sessionId: 'small-friction-session',
  toolCallCount: 5,
  interventions: { interrupt: 3, toolReject: 2, toolError: 0 },
  promptSummary: 'Quick one-line fix',
});
fs.writeFileSync(
  path.join(SANDBOX, '.teamai/dashboard/events.jsonl'),
  eventsC.map((e) => JSON.stringify(e)).join('\n') + '\n',
);
runCase('Case C: 摩擦够但工作量不足 (interrupt=3, reject=2, toolCalls=5)', {
  session_id: 'small-friction-session',
  cwd: '/tmp',
});

// Case D: 边界值 — 恰好 1 次打断 + 3 次工具重试（分数 20+10=30, toolCalls=20）
setup();
const eventsD = buildEvents({
  sessionId: 'borderline-session',
  toolCallCount: 20,
  interventions: { interrupt: 1, toolReject: 0, toolError: 3 },
  promptSummary: 'Investigate flaky test',
});
fs.writeFileSync(
  path.join(SANDBOX, '.teamai/dashboard/events.jsonl'),
  eventsD.map((e) => JSON.stringify(e)).join('\n') + '\n',
);
runCase('Case D: 边界值 (interrupt=1, toolError=3, toolCalls=20)', {
  session_id: 'borderline-session',
  cwd: '/tmp',
});
