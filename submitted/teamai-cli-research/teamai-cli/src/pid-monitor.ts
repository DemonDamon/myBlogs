import fs from 'node:fs';
import { execSync } from 'node:child_process';

// ─── Process tree helpers ──────────────────────────────
//
//  Used by dashboard-collector (at hook time) to find the AI tool PID,
//  and by dashboard server (at check time) to verify PID liveness.
//
//  Cross-platform: tries Linux /proc first (zero-cost), falls back to ps(1).

/** Shell executable names to skip when walking the process tree. */
const SHELL_COMMS = new Set([
    'sh', 'bash', 'zsh', 'fish', 'dash', 'csh', 'tcsh', 'ksh',
]);

/**
 * Get the parent PID of a given process.
 * Returns undefined if PID doesn't exist or can't be read.
 */
export function getParentPid(pid: number): number | undefined {
    // Linux: read /proc/{pid}/stat (fast, no process spawn)
    try {
        const stat = fs.readFileSync(`/proc/${pid}/stat`, 'utf-8');
        // Field 4 is ppid. Field 2 (comm) can contain spaces/parens, so split carefully.
        // Format: pid (comm) state ppid ...
        const closeParen = stat.lastIndexOf(') ');
        if (closeParen === -1) return undefined;
        const fields = stat.slice(closeParen + 2).split(' ');
        // fields[0]=state, fields[1]=ppid
        const ppid = parseInt(fields[1], 10);
        return ppid > 0 ? ppid : undefined;
    } catch {
        // not Linux, or PID gone
    }

    // macOS/BSD fallback: ps -o ppid= -p <pid>
    try {
        const out = execSync(`ps -o ppid= -p ${pid}`, {
            encoding: 'utf-8',
            timeout: 2000,
            stdio: ['pipe', 'pipe', 'pipe'],
        });
        const ppid = parseInt(out.trim(), 10);
        return ppid > 0 ? ppid : undefined;
    } catch {
        return undefined;
    }
}

/**
 * Get the executable name (comm) of a process.
 * Returns undefined if PID doesn't exist.
 */
export function getProcessComm(pid: number): string | undefined {
    // Linux: /proc/{pid}/comm (just the basename, no args)
    try {
        return fs.readFileSync(`/proc/${pid}/comm`, 'utf-8').trim();
    } catch {
        // fall through
    }

    // macOS/BSD fallback
    try {
        const out = execSync(`ps -o comm= -p ${pid}`, {
            encoding: 'utf-8',
            timeout: 2000,
            stdio: ['pipe', 'pipe', 'pipe'],
        });
        // ps on macOS may return full path
        return out.trim().split('/').pop();
    } catch {
        return undefined;
    }
}

/**
 * Walk up the process tree from the hook's parent PID to find the
 * AI tool's main process. Skips shell wrapper processes (sh, bash, etc.)
 * and returns the first non-shell ancestor.
 *
 * Falls back to the hook's parent PID if no non-shell ancestor is found
 * within 5 levels.
 */
export function resolveMonitorPid(hookPpid: number): number {
    let current = hookPpid;
    let best = hookPpid;

    for (let depth = 0; depth < 5; depth++) {
        const comm = getProcessComm(current);
        if (comm && !SHELL_COMMS.has(comm)) {
            // Found a non-shell process — this is likely the AI tool
            return current;
        }

        const parent = getParentPid(current);
        if (!parent || parent <= 1) break;

        best = parent;
        current = parent;
    }

    return best;
}

/**
 * Check if a process with the given PID is still alive.
 * Uses kill(pid, 0) which sends no signal — just checks existence.
 *
 * Returns true if the process exists (even if we lack permission to signal it).
 */
export function isProcessAlive(pid: number): boolean {
    try {
        process.kill(pid, 0);
        return true;
    } catch (err: unknown) {
        const code = (err as NodeJS.ErrnoException).code;
        if (code === 'ESRCH') return false;  // No such process
        if (code === 'EPERM') return true;   // Exists, but no permission
        return false;
    }
}
