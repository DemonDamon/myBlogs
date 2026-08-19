import { describe, it, expect } from 'vitest';
import { compileClaudemd } from '../pull.js';

describe('compileClaudemd', () => {
    it('should wrap single file content in claudemd markers', () => {
        const contents = ['Always run tests before committing.\nUse conventional commits.'];

        const result = compileClaudemd(contents);
        expect(result).not.toBeNull();
        expect(result).toContain('<!-- [teamai:claudemd:start] -->');
        expect(result).toContain('<!-- [teamai:claudemd:end] -->');
        expect(result).toContain('Always run tests before committing.');
        expect(result).toContain('Use conventional commits.');
    });

    it('should merge multiple files with double newline separator', () => {
        const contents = [
            '## Project Overview\nHAI Platform.',
            '## Common Commands\nnpm run build',
        ];

        const result = compileClaudemd(contents);
        expect(result).not.toBeNull();
        expect(result).toContain('## Project Overview');
        expect(result).toContain('## Common Commands');
        // Files separated by double newline
        expect(result).toContain('HAI Platform.\n\n## Common Commands');
    });

    it('should return null when all contents are empty', () => {
        expect(compileClaudemd([])).toBeNull();
    });

    it('should return null when all contents are whitespace-only', () => {
        expect(compileClaudemd(['  ', '\n\n', '   \n  '])).toBeNull();
    });

    it('should filter out empty entries from mixed contents', () => {
        const contents = ['', 'Valid content', '  ', 'Another valid'];

        const result = compileClaudemd(contents);
        expect(result).not.toBeNull();
        expect(result).toContain('Valid content');
        expect(result).toContain('Another valid');
    });

    it('should trim leading/trailing whitespace from each file', () => {
        const contents = ['\n\n  Hello world  \n\n'];

        const result = compileClaudemd(contents);
        expect(result).not.toBeNull();
        expect(result).toContain('Hello world');
        // Content should be trimmed — no leading spaces
        expect(result).not.toContain('  Hello world');
    });

    it('should include DO NOT EDIT comment', () => {
        const result = compileClaudemd(['Test content']);
        expect(result).toContain('<!-- DO NOT EDIT: This section is auto-managed by teamai -->');
    });

    it('should preserve content as-is without frontmatter parsing', () => {
        const contents = [
            [
                '---',
                'key: value',
                '---',
                'Body text.',
            ].join('\n'),
        ];

        const result = compileClaudemd(contents);
        expect(result).not.toBeNull();
        // Frontmatter delimiters should be preserved (not parsed)
        expect(result).toContain('---');
        expect(result).toContain('key: value');
        expect(result).toContain('Body text.');
    });

    it('should preserve markdown formatting', () => {
        const contents = [
            [
                '## Custom Section',
                '',
                'Some instructions with **bold** and `code`.',
                '',
                '- Item 1',
                '- Item 2',
                '',
                '```bash',
                'npm run build',
                '```',
            ].join('\n'),
        ];

        const result = compileClaudemd(contents);
        expect(result).not.toBeNull();
        expect(result).toContain('## Custom Section');
        expect(result).toContain('**bold**');
        expect(result).toContain('`code`');
        expect(result).toContain('- Item 1');
        expect(result).toContain('```bash');
    });

    it('should produce correct block structure', () => {
        const result = compileClaudemd(['Content here']);
        expect(result).not.toBeNull();

        const lines = result!.split('\n');
        expect(lines[0]).toBe('<!-- [teamai:claudemd:start] -->');
        expect(lines[1]).toBe('<!-- DO NOT EDIT: This section is auto-managed by teamai -->');
        expect(lines[2]).toBe('');
        expect(lines[3]).toBe('Content here');
        expect(lines[4]).toBe('');
        expect(lines[5]).toBe('<!-- [teamai:claudemd:end] -->');
    });
});
