"""
Knowledge Graph vs Traditional RAG Demo
"""

import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

from traditional_rag import TraditionalRAG
from knowledge_graph import KnowledgeGraphRAG
from comparison import compare_systems, run_comparison_suite, plot_comparison_metrics, visualize_graph

from load_pdf import load_pdf
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

console = Console()


DEMO_QUESTIONS = [
    "How does the AuthenticationService relate to the UserManager?",
    "What services depend on the PermissionManager?",
    "Explain the file upload workflow and all the services involved.",
    "How are share links related to notifications?",
    "What is the relationship between QuotaManager and StorageManager?",
    "Which services interact with the FileManager?",
    "How does the search functionality work with permissions?"
]


def setup_environment():
    """Load and validate environment variables."""
    load_dotenv()

    required_vars = [
        "OPENAI_API_KEY",
        "NEO4J_URI",
        "NEO4J_USERNAME",
        "NEO4J_PASSWORD"
    ]

    missing = [v for v in required_vars if not os.getenv(v)]

    if missing:
        console.print("[bold red]Missing environment variables:[/bold red]")
        for v in missing:
            console.print(f" - {v}")
        return False

    return True


async def initialize_systems():
    """Initialize Traditional RAG + Knowledge Graph RAG."""
    console.print("\n[bold cyan]Initializing Systems...[/bold cyan]\n")

    # Load config
    openai_api_key = os.getenv("OPENAI_API_KEY")
    neo4j_uri = os.getenv("NEO4J_URI")
    neo4j_username = os.getenv("NEO4J_USERNAME")
    neo4j_password = os.getenv("NEO4J_PASSWORD")
    model_name = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
    embedding_model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

    # Initialize Traditional RAG
    console.print("[yellow]1. Initializing Traditional RAG...[/yellow]")
    rag_system = TraditionalRAG(
        openai_api_key=openai_api_key,
        model_name=model_name,
        embedding_model=embedding_model
    )

    # Load PDF
    PDF_PATH = Path("sample_data/NEPQ Black Book of Questions (PLEASE DO NOT SHARE).pdf")

    if not PDF_PATH.exists():
        console.print(f"[bold red]ERROR: PDF not found at {PDF_PATH}[/bold red]")
        return None, None

    console.print(f"[yellow]Loading PDF: {PDF_PATH}[/yellow]")

    try:
        full_text = load_pdf(str(PDF_PATH))
    except Exception as e:
        console.print(f"[bold red]PDF Load Error:[/bold red] {e}")
        return None, None

    # -------------------------------
    # CHUNKING USING LANGCHAIN SPLITTER
    # -------------------------------
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )

    chunks = splitter.create_documents([full_text])

    # Add metadata (FAISS requires metadata)
    documents = []
    for i, doc in enumerate(chunks):
        documents.append(
            Document(
                page_content=doc.page_content,
                metadata={"source": str(PDF_PATH), "chunk_id": i}
            )
        )

    console.print(f"[green]PDF loaded and {len(documents)} chunks created[/green]")

    # Build FAISS Index
    rag_system.build_index(documents)
    console.print("[green][OK] Traditional RAG initialized[/green]\n")

    # -------------------------------
    # KNOWLEDGE GRAPH RAG
    # -------------------------------
    console.print("[yellow]2. Initializing Knowledge Graph RAG...[/yellow]")

    kg_system = KnowledgeGraphRAG(
        neo4j_uri=neo4j_uri,
        neo4j_user=neo4j_username,
        neo4j_password=neo4j_password,
        openai_api_key=openai_api_key,
        model_name=model_name
    )

    await kg_system.graphiti.build_indices_and_constraints()

    # Check graph existing
    stats = kg_system.get_graph_statistics()

    if stats["total_nodes"] > 0:
        console.print(f"[yellow]Existing graph found: {stats['total_nodes']} nodes[/yellow]")
        rebuild = Confirm.ask("Rebuild the knowledge graph?", default=False)

        if rebuild:
            kg_system.clear_graph()
            stats = kg_system.get_graph_statistics()

    # Build graph if empty
    if stats["total_nodes"] == 0:
        console.print("[yellow]Building knowledge graph...[/yellow]")

        text_blocks = [doc.page_content for doc in documents]
        await kg_system.add_documents_to_graph(text_blocks, source="NEPQ_black_book")

        stats = kg_system.get_graph_statistics()

        console.print("[green][OK] Knowledge Graph Initialized[/green]")
        console.print(f"  Nodes: {stats['total_nodes']}")
        console.print(f"  Relationships: {stats['total_relationships']}")
        console.print(f"  Entities: {stats['num_entities']}")
        console.print(f"  Episodes: {stats['num_episodes']}\n")
    else:
        console.print("[green][OK] Using Existing Knowledge Graph[/green]")

    return rag_system, kg_system


async def run_single_comparison(rag_system, kg_system):
    console.print("\n[bold cyan]Single Question Comparison[/bold cyan]\n")

    console.print("[yellow]Suggested questions:[/yellow]")
    for i, q in enumerate(DEMO_QUESTIONS, 1):
        console.print(f"{i}. {q}")

    user_input = Prompt.ask("\nEnter question number or type your own")

    if user_input.isdigit() and 1 <= int(user_input) <= len(DEMO_QUESTIONS):
        question = DEMO_QUESTIONS[int(user_input) - 1]
    else:
        question = user_input

    await compare_systems(rag_system, kg_system, question, verbose=True)


async def run_full_comparison_suite(rag_system, kg_system):
    console.print("\n[bold cyan]Running Complete Comparison Suite[/bold cyan]")

    confirm = Confirm.ask("Start?", default=True)
    if not confirm:
        return

    results = await run_comparison_suite(rag_system, kg_system, DEMO_QUESTIONS)

    plot_comparison_metrics(results, "comparison_metrics.png")
    console.print("[green]Saved: comparison_metrics.png[/green]")


def visualize_knowledge_graph(kg_system):
    console.print("\n[bold cyan]Visualizing Graph[/bold cyan]\n")

    visualize_graph(
        neo4j_uri=os.getenv("NEO4J_URI"),
        neo4j_user=os.getenv("NEO4J_USERNAME"),
        neo4j_password=os.getenv("NEO4J_PASSWORD"),
        output_file="knowledge_graph.html",
        max_nodes=100
    )

    console.print("[green]Saved: knowledge_graph.html[/green]")


async def interactive_mode(rag_system, kg_system):
    console.print("\n[bold cyan]Interactive Mode[/bold cyan]")

    while True:
        question = Prompt.ask("\nYour question (or 'exit')")

        if question.lower() in ("exit", "quit", "q"):
            break

        await compare_systems(rag_system, kg_system, question, verbose=True)


async def main():
    console.print(Panel.fit(
        "[bold green]Knowledge Graph vs Traditional RAG Demo[/bold green]",
        border_style="green"
    ))

    if not setup_environment():
        return

    rag_system, kg_system = await initialize_systems()
    if not rag_system or not kg_system:
        return

    while True:
        console.print("\n" + "=" * 80)
        console.print("[bold cyan]MENU[/bold cyan]")
        console.print("=" * 80)
        console.print("1. Run single question comparison")
        console.print("2. Run full comparison suite")
        console.print("3. Visualize knowledge graph")
        console.print("4. Interactive question mode")
        console.print("5. View graph stats")
        console.print("6. Exit\n")

        choice = Prompt.ask("Choose option", choices=["1", "2", "3", "4", "5", "6"])

        if choice == "1":
            await run_single_comparison(rag_system, kg_system)
        elif choice == "2":
            await run_full_comparison_suite(rag_system, kg_system)
        elif choice == "3":
            visualize_knowledge_graph(kg_system)
        elif choice == "4":
            await interactive_mode(rag_system, kg_system)
        elif choice == "5":
            stats = kg_system.get_graph_statistics()
            console.print("\n[bold cyan]Graph Statistics[/bold cyan]")
            for k, v in stats.items():
                console.print(f"  {k}: {v}")
        elif choice == "6":
            console.print("\n[bold green]Goodbye![/bold green]\n")
            kg_system.close()
            break


if __name__ == "__main__":
    asyncio.run(main())
