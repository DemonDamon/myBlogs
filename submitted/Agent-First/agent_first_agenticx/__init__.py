"""
Agent-First: 基于 AgenticX 的实现

将 Berkeley Agent-First 论文概念与 AgenticX 框架无缝集成。
"""

__version__ = "0.1.0"

# Probe 系统
from .probes import (
    ProbeQueryTool,
    create_probe_agent,
    ProbeRequest,
    ProbeResponse
)

# Agent 系统
from .agents import (
    create_field_agent,
    create_sleeper_agent,
    create_probe_collaboration
)

# Memory 扩展
from .memory import (
    AgenticMemoryStore,
    QueryCache,
    RedundancyDetector
)

# Storage 扩展
from .storage import (
    BranchManager,
    CopyOnWriteEngine
)

__all__ = [
    # Probe
    "ProbeQueryTool",
    "create_probe_agent",
    "ProbeRequest",
    "ProbeResponse",
    
    # Agents
    "create_field_agent",
    "create_sleeper_agent",
    "create_probe_collaboration",
    
    # Memory
    "AgenticMemoryStore",
    "QueryCache",
    "RedundancyDetector",
    
    # Storage
    "BranchManager",
    "CopyOnWriteEngine",
]

