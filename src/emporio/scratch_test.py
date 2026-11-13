from emporio.agent.graph import build_graph

graph = build_graph()
questions = [
    "Quanto custa o Takamine GD20?",
    "Quais violões vocês têm até R$ 1000?",
    "Me arrependi da compra, posso devolver?",
    "Qual a capital da França?",
]
for q in questions:
    result = graph.invoke({"messages": [("user", q)]})
    print(f"\n>>> {q}")
    for m in result["messages"]:
        for call in getattr(m, "tool_calls", []):
            print(f"  [tool] {call['name']}({call['args']})")
    print(result["messages"][-1].content)
