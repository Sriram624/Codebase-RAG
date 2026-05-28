from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Annotated
from operator import add
from llama_index.llms.ollama import Ollama
from config import OLLAMA_MODEL

# Point base_url to the host machine where Ollama runs
llm = Ollama(
    model=OLLAMA_MODEL,
    base_url="http://host.docker.internal:11434",
    temperature=0.1,
    request_timeout=180.0
)

class AgentState(TypedDict):
    question: str
    intent: str
    context: List[str]
    compressed_context: str
    answer: str
    steps: Annotated[List[str], add]
    chat_history: List[str]

def classify_intent(state: AgentState):
    print(f"DEBUG: Entering classify_intent with question: {state['question']}")
    try:
        prompt = (
            "Classify query: ARCHITECTURE, DEBUGGING, REFACTOR, EXPLAIN, DEPENDENCY, SIMILAR. "
            f"Return one word.\nQuery: {state['question']}"
        )
        intent = llm.complete(prompt).text.strip().upper()
        print(f"DEBUG: classfiy_intent output: {intent}")
        return {"intent": intent, "steps": [f"Intent: {intent}"]}
    except Exception as e:
        print(f"ERROR in classify_intent: {e}")
        raise e


def retrieve(state: AgentState, index):
    k = 12 if state.get("intent") in ["ARCHITECTURE", "DEPENDENCY"] else 10
    retriever = index.as_retriever(similarity_top_k=k)
    nodes = retriever.retrieve(state["question"])
    context = [n.text for n in nodes]
    return {"context": context, "steps": ["Retrieved code chunks"]}

def compress_context(state: AgentState):
    text = "\n\n".join(state["context"])
    if len(text) > 7000:
        compressed_text = llm.complete(
            f"Summarize key logic and relationships:\n{text[:14000]}"
        ).text
    else:
        compressed_text = text
    return {"compressed_context": compressed_text}

def generate(state: AgentState):
    history_list = state.get("chat_history", [])
    history = "\n".join([str(h) for h in history_list[-5:]])
    context = state.get("compressed_context", "\n\n".join(state.get("context", [])))
    question = state["question"]

    prompt = f"""You are a Principal Software Engineer. Provide high-quality, actionable responses.

Conversation History:
{history}

Context:
{context}

Question: {question}

Respond with:
- Clear explanation
- File + function citations
- Trade-offs when relevant
- Practical next steps
Use markdown and code blocks."""

    answer = llm.complete(prompt).text
    return {"answer": answer, "steps": ["Generated answer"]}

def build_graph(index):
    workflow = StateGraph(AgentState)
    workflow.add_node("classify", classify_intent)
    workflow.add_node("retrieve", lambda s: retrieve(s, index))
    workflow.add_node("compress", compress_context)
    workflow.add_node("generate", generate)
    workflow.set_entry_point("classify")
    workflow.add_edge("classify", "retrieve")
    workflow.add_edge("retrieve", "compress")
    workflow.add_edge("compress", "generate")
    workflow.add_edge("generate", END)
    return workflow.compile()
