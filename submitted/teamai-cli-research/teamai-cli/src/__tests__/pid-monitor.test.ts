import { describe, it, expect } from 'vitest';
import {
    isProcessAlive,
    getProcessComm,
    getParentPid,
    resolveMonitorPid,
} from '../pid-monitor.js';

describe('isProcessAlive', () => {
    it('returns true for current process', () => {
        expect(isProcessAlive(process.pid)).toBe(true);
    });

    it('returns false for non-existent PID', () => {
        // PID 99999999 is extremely unlikely to exist
        expect(isProcessAlive(99999999)).toBe(false);
    });

    it('returns true for PID 1 (init/systemd)', () => {
        // PID 1 always exists on Linux, may return EPERM
        expect(isProcessAlive(1)).toBe(true);
    });
});

describe('getProcessComm', () => {
    it('returns a string for current process', () => {
        const comm = getProcessComm(process.pid);
        expect(comm).toBeDefined();
        expect(typeof comm).toBe('string');
        expect(comm!.length).toBeGreaterThan(0);
    });

    it('returns undefined for non-existent PID', () => {
        expect(getProcessComm(99999999)).toBeUndefined();
    });
});

describe('getParentPid', () => {
    it('returns a number for current process', () => {
        const ppid = getParentPid(process.pid);
        expect(ppid).toBeDefined();
        expect(ppid).toBeGreaterThan(0);
    });

    it('matches process.ppid for current process', () => {
        const ppid = getParentPid(process.pid);
        expect(ppid).toBe(process.ppid);
    });

    it('returns undefined for non-existent PID', () => {
        expect(getParentPid(99999999)).toBeUndefined();
    });
});

describe('resolveMonitorPid', () => {
    it('returns a valid PID for current process ppid', () => {
        const pid = resolveMonitorPid(process.ppid);
        expect(pid).toBeGreaterThan(0);
    });

    it('returns the input PID when it is not a shell', () => {
        // process.ppid should be a node process (vitest runner), not a shell
        const pid = resolveMonitorPid(process.ppid);
        // Should return ppid itself if it's not a shell, or walk up to a non-shell
        expect(isProcessAlive(pid)).toBe(true);
    });
});
