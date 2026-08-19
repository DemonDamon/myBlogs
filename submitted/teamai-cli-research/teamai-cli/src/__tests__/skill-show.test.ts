import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import path from 'node:path';
import os from 'node:os';
import fse from 'fs-extra';

vi.mock('../utils/logger.js', () => ({
  log: {
    info: vi.fn(),
    success: vi.fn(),
    warn: vi.fn(),
    error: vi.fn(),
    debug: vi.fn(),
    dim: vi.fn(),
  },
}));

import type { LocalConfig, TeamaiConfig } from '../types.js';

interface Fixture {
  tmpDir: string;
  homeDir: string;
  repoPath: string;
  localConfig: LocalConfig;
  teamConfig: TeamaiConfig;
}

async function makeFixture(): Promise<Fixture> {
  const tmpDir = await fse.mkdtemp(path.join(os.tmpdir(), 'teamai-skill-show-'));
  const homeDir = path.join(tmpDir, 'home');
  const repoPath = path.join(tmpDir, 'team-repo');
  await fse.ensureDir(path.join(repoPath, 'skills'));
  await fse.ensureDir(homeDir);
  vi.stubEnv('HOME', homeDir);

  const teamConfig: TeamaiConfig = {
    team: 'test',
    description: '',
    repo: 'https://example.com/test.git',
    provider: 'tgit',
    reviewers: [],
    sharing: {
      skills: {},
      rules: { enforced: [] },
      docs: { localDir: '' },
      env: { injectShellProfile: true },
    },
    toolPaths: {
      claude: { skills: '.claude/skills', rules: '.claude/rules' },
      cursor: { skills: '.cursor/skills', rules: '.cursor/rules' },
    },
  };

  const localConfig: LocalConfig = {
    repo: { localPath: repoPath, remote: 'https://example.com/test.git' },
    username: 'tester',
    updatePolicy: 'auto',
    scope: 'user',
    additionalRoles: [],
  };

  return { tmpDir, homeDir, repoPath, localConfig, teamConfig };
}

async function makeSkill(dir: string, name: string, description: string, contributors?: string[]): Promise<void> {
  const skillDir = path.join(dir, name);
  await fse.ensureDir(skillDir);
  const fm = `---\nname: ${name}\ndescription: ${description}\n---\n\n# ${name}\n\nbody\n`;
  await fse.writeFile(path.join(skillDir, 'SKILL.md'), fm, 'utf-8');
  if (contributors?.length) {
    await fse.writeFile(path.join(skillDir, 'CONTRIBUTORS'), contributors.join('\n') + '\n');
  }
}

function captureLogs() {
  const lines: string[] = [];
  const orig = console.log;
  console.log = (...args: unknown[]) => {
    lines.push(args.map((a) => String(a)).join(' '));
  };
  return {
    lines,
    restore: () => {
      console.log = orig;
    },
  };
}

async function runSkillShow(name: string, fx: Fixture): Promise<string[]> {
  vi.doMock('../config.js', () => ({
    autoDetectInit: async () => ({ localConfig: fx.localConfig, teamConfig: fx.teamConfig }),
  }));
  const { skillShow } = await import('../skill-cmd.js');
  const cap = captureLogs();
  process.exitCode = 0;
  try {
    await skillShow(name, {});
  } finally {
    cap.restore();
  }
  vi.doUnmock('../config.js');
  return cap.lines;
}

describe('skillShow locator', () => {
  let fx: Fixture;

  beforeEach(async () => {
    fx = await makeFixture();
    vi.resetModules();
  });

  afterEach(async () => {
    vi.unstubAllEnvs();
    await fse.remove(fx.tmpDir);
    process.exitCode = 0;
  });

  it('finds skill in flat layout of team repo', async () => {
    await makeSkill(path.join(fx.repoPath, 'skills'), 'flat-skill', 'flat description', ['alice', 'bob']);
    const lines = await runSkillShow('flat-skill', fx);
    const text = lines.join('\n');
    expect(text).toContain('flat-skill');
    expect(text).toContain('[team]');
    expect(text).toContain('flat description');
    expect(text).toContain('alice, bob');
    expect(text).not.toContain('Missing in');
    expect(text).not.toContain('# flat-skill'); // body NOT rendered
  });

  it('finds skill in namespaced layout of team repo', async () => {
    await makeSkill(path.join(fx.repoPath, 'skills', 'hai_dev'), 'ns-skill', 'ns desc');
    const lines = await runSkillShow('ns-skill', fx);
    const text = lines.join('\n');
    expect(text).toContain('Source       : [team:hai_dev]');
    expect(text).toContain('Namespace    : hai_dev');
  });

  it('falls back to installed agent when not in team repo', async () => {
    const claudeSkillsDir = path.join(fx.homeDir, '.claude', 'skills');
    await fse.ensureDir(claudeSkillsDir);
    await makeSkill(claudeSkillsDir, 'agent-only', 'agent-side desc');

    const lines = await runSkillShow('agent-only', fx);
    const text = lines.join('\n');
    expect(text).toContain('[local-only]');
    expect(text).toContain('agent-side desc');
    expect(text).toContain('claude');
  });

  it('exits with non-zero code when skill not found', async () => {
    process.exitCode = 0;
    const lines = await runSkillShow('does-not-exist', fx);
    expect(process.exitCode).toBe(1);
    // No card printed
    expect(lines.find((l) => l.includes('skill: does-not-exist'))).toBeUndefined();
    process.exitCode = 0;
  });
});

describe('skillShow output formatting', () => {
  let fx: Fixture;

  beforeEach(async () => {
    fx = await makeFixture();
    vi.resetModules();
  });

  afterEach(async () => {
    vi.unstubAllEnvs();
    await fse.remove(fx.tmpDir);
    process.exitCode = 0;
  });

  it('truncates long descriptions to 160 characters with ellipsis', async () => {
    const longDesc = 'a'.repeat(300);
    await makeSkill(path.join(fx.repoPath, 'skills'), 'long', longDesc);

    const lines = await runSkillShow('long', fx);
    const descLine = lines.find((l) => l.includes('Description'))!;
    expect(descLine).toBeDefined();
    // 'Description  : ' prefix + truncated text
    const truncatedPart = descLine.split('Description  : ')[1];
    expect(truncatedPart.length).toBeLessThanOrEqual(160);
    expect(truncatedPart.endsWith('...')).toBe(true);
  });

  it('lists installed agents and never shows "Missing in" line', async () => {
    await makeSkill(path.join(fx.repoPath, 'skills'), 'multi-agent', 'desc');

    const claudeDir = path.join(fx.homeDir, '.claude', 'skills');
    await fse.ensureDir(claudeDir);
    await makeSkill(claudeDir, 'multi-agent', 'desc-claude');

    const cursorDir = path.join(fx.homeDir, '.cursor', 'skills');
    await fse.ensureDir(cursorDir);
    await makeSkill(cursorDir, 'multi-agent', 'desc-cursor');

    const lines = await runSkillShow('multi-agent', fx);
    const text = lines.join('\n');
    expect(text).toContain('Installed in : claude');
    expect(text).toContain('cursor');
    expect(text).not.toContain('Missing in');
    expect(text).not.toContain('codex'); // not installed → not listed anywhere
  });

  it('shows tags from tags.yaml when present', async () => {
    await makeSkill(path.join(fx.repoPath, 'skills'), 'tagged', 'desc');
    await fse.writeFile(
      path.join(fx.repoPath, 'tags.yaml'),
      'skills:\n  tagged: [hai, infra]\nrules: {}\n',
    );

    const lines = await runSkillShow('tagged', fx);
    const text = lines.join('\n');
    expect(text).toContain('Tags         : hai, infra');
  });
});
