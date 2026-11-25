"""Tiny wrapper: compiles a LangGraph StateGraph when installed, else runs an equivalent loop."""
END = "__end__"

def compile_flow(nodes: dict, entry: str, nxt: dict, state_cls):
    try:
        from langgraph.graph import StateGraph
    except ImportError:
        class Flow:
            def invoke(self, s):
                cur = entry
                while cur != END:
                    s = {**s, **nodes[cur](s)}
                    t = nxt[cur]; cur = t(s) if callable(t) else t
                return s
        return Flow()
    g = StateGraph(state_cls)
    for n, f in nodes.items(): g.add_node(n, f)
    g.set_entry_point(entry)
    for n, t in nxt.items():
        if callable(t): g.add_conditional_edges(n, t)
        else: g.add_edge(n, t)
    return g.compile()
