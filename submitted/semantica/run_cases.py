"""Semantica 实测脚本：上下文图谱 + 决策因果链 + 先例检索 + PROV-O 导出"""
import json
import time

from semantica.context import ContextGraph, AgentContext
from semantica.vector_store import VectorStore

print("=" * 60)
print("Case 1: 上下文图谱 —— 节点/边/多跳遍历/时间快照")
print("=" * 60)

graph = ContextGraph(advanced_analytics=True)

graph.add_node("acme_corp", "Organization", name="Acme Corp", industry="SaaS")
graph.add_node("alice_chen", "Person", name="Alice Chen", role="CTO")
graph.add_node("bob_wang", "Person", name="Bob Wang", role="Legal Counsel")
graph.add_node("contract_001", "Contract", value=2_400_000, currency="USD")
graph.add_node("contract_002", "Contract", value=800_000, currency="USD")

graph.add_edge("alice_chen", "acme_corp", edge_type="works_for", since="2019-03-01")
graph.add_edge("bob_wang", "acme_corp", edge_type="works_for", since="2021-06-01")
graph.add_edge("acme_corp", "contract_001", edge_type="party_to", signed="2024-01-15")
graph.add_edge("bob_wang", "contract_001", edge_type="reviewed", date="2024-01-10")
graph.add_edge("acme_corp", "contract_002", edge_type="party_to", signed="2026-05-20")

print(f"[图规模] nodes={len(graph.nodes)}, edges={len(graph.edges)}")

t0 = time.perf_counter()
neighbors = graph.get_neighbors("acme_corp", hops=2)
elapsed = (time.perf_counter() - t0) * 1000
print(f"[两跳遍历] acme_corp 2 跳邻居 ({elapsed:.3f} ms):")
if isinstance(neighbors, dict):
    for k, v in neighbors.items():
        print(f"  - {k}: {v}")
else:
    print(" ", neighbors)

snapshot = graph.state_at("2024-06-01")
if isinstance(snapshot, dict):
    n_nodes = len(snapshot.get("nodes", snapshot.get("node_count", [])))
    print(f"[时间快照] 2024-06-01 视角: nodes={n_nodes}")
else:
    print(f"[时间快照] 2024-06-01 视角: {snapshot}")

print()
print("=" * 60)
print("Case 2: 决策智能 —— 医疗联用处方因果链 (推文同款 case)")
print("=" * 60)

d1 = graph.record_decision(
    category="drug_interaction_check",
    scenario="Patient P-4821: warfarin + amiodarone co-prescribed",
    reasoning="Amiodarone potentiates warfarin's anticoagulant effect",
    outcome="flag_for_review",
    confidence=0.91,
    metadata={"patient_id": "P-4821"},
)
d2 = graph.record_decision(
    category="dosage_adjustment",
    scenario="INR monitoring plan for P-4821",
    reasoning="Reduce warfarin dose per interaction severity; recheck INR in 5 days",
    outcome="dose_reduced_30pct",
    confidence=0.87,
    metadata={"patient_id": "P-4821"},
)
d3 = graph.record_decision(
    category="followup_schedule",
    scenario="Follow-up visit for P-4821 after dose change",
    reasoning="Recheck INR on day 5; escalate if INR > 4.0",
    outcome="scheduled_day5",
    confidence=0.95,
    metadata={"patient_id": "P-4821"},
)
print(f"[决策ID] d1={d1[:16]}... d2={d2[:16]}... d3={d3[:16]}...")

graph.add_causal_relationship(d1, d2, relationship_type="CAUSED")
graph.add_causal_relationship(d2, d3, relationship_type="INFLUENCED")
print("[因果链] d1 --CAUSED--> d2 --INFLUENCED--> d3 已建立")

chain = graph.trace_decision_chain(d3)
print("[trace_decision_chain(d3)] 结果:")
print(json.dumps(chain, indent=2, default=str, ensure_ascii=False)[:1500])

print()
print("=" * 60)
print("Case 3: 先例检索 + 影响面分析")
print("=" * 60)

try:
    similar = graph.find_similar_decisions("warfarin interaction review", max_results=3)
    print("[find_similar_decisions] 返回类型:", type(similar).__name__)
    print(json.dumps(similar, indent=2, default=str, ensure_ascii=False)[:800])
except Exception as e:
    print("find_similar_decisions 异常:", type(e).__name__, str(e)[:200])

try:
    impact = graph.analyze_decision_impact(d2)
    print("[analyze_decision_impact(d2)] 返回类型:", type(impact).__name__)
    print(json.dumps(impact, indent=2, default=str, ensure_ascii=False)[:800])
except Exception as e:
    print("analyze_decision_impact 异常:", type(e).__name__, str(e)[:200])

try:
    insights = graph.get_decision_insights()
    print("[get_decision_insights] 返回类型:", type(insights).__name__)
    print(json.dumps(insights, indent=2, default=str, ensure_ascii=False)[:800])
except Exception as e:
    print("get_decision_insights 异常:", type(e).__name__, str(e)[:200])

print()
print("=" * 60)
print("Case 4: AgentContext —— Agent 记忆工作流 (语义检索)")
print("=" * 60)

try:
    vs = VectorStore(backend="faiss")
    ctx = AgentContext(vector_store=vs, knowledge_graph=graph)
    ctx.store("Alice approved the Acme renewal in Q1 2024", conversation_id="conv_001")
    ctx.store("Bob reviewed contract 001 for legal risks", conversation_id="conv_001")
    ctx.store("The 2.4M USD contract was signed on 2024-01-15", conversation_id="conv_001")
    retrieved = ctx.retrieve("who approved the Acme contract?")
    print("[retrieve] 返回类型:", type(retrieved).__name__)
    print(json.dumps(retrieved, indent=2, default=str, ensure_ascii=False)[:1000])
except Exception as e:
    print("AgentContext 异常:", type(e).__name__, str(e)[:300])

print()
print("=" * 60)
print("Case 5: 图导出 (RDF/turtle) —— 可交监管的机器可读格式")
print("=" * 60)

try:
    from semantica.export import RDFExporter, JSONExporter

    snapshot = {
        "entities": [
            {"id": n.node_id, "text": n.content or n.node_id, "type": n.node_type}
            for n in graph.nodes.values()
        ],
        "relationships": [
            {
                "source": e.source_id,
                "target": e.target_id,
                "type": e.edge_type,
            }
            for e in graph.edges
        ],
    }
    rdf_exporter = RDFExporter()
    rdf_exporter.export(snapshot, "semantica_demo.ttl", format="turtle")
    with open("semantica_demo.ttl") as f:
        content = f.read()
    print(f"[RDF 导出] semantica_demo.ttl 共 {len(content)} 字符, 前 600 字符:")
    print(content[:600])
except Exception as e:
    import traceback
    print("export 异常:", type(e).__name__, str(e)[:300])
    traceback.print_exc()

print()
print("=" * 60)
print("Case 6: PROV-O 溯源导出 —— 决策的完整监管证据链")
print("=" * 60)

try:
    from semantica.provenance import ProvenanceManager

    pm = ProvenanceManager()
    pm.track_entity(
        entity_id=d1,
        source="ehr_p4821.xml",
        metadata={"entity_type": "decision", "category": "drug_interaction_check",
                  "confidence": 0.91, "agent": "dr_ai_assistant"},
    )
    pm.track_entity(
        entity_id=d2,
        source="clinical_guideline_warfarin.pdf",
        metadata={"entity_type": "decision", "category": "dosage_adjustment",
                  "confidence": 0.87, "agent": "dr_ai_assistant"},
    )
    pm.track_relationship("caused_by_review", "physician_review_note.txt",
                          metadata={"source_id": d1, "target_id": d2, "relation": "CAUSED"})
    prov_out = pm.export_prov(format="turtle")
    print(f"[PROV-O turtle] 共 {len(prov_out)} 字符, 前 800 字符:")
    print(prov_out[:800])
    stats = pm.get_statistics()
    print("[统计]", json.dumps(stats, indent=2, default=str, ensure_ascii=False)[:400])
except Exception as e:
    import traceback
    print("PROV-O 异常:", type(e).__name__, str(e)[:300])
    traceback.print_exc()

print()
print("ALL CASES DONE")
