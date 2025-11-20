from load_pdf import load_pdf
from build_kg import KGBuilder
import os
from dotenv import load_dotenv

load_dotenv()

pdf_text = load_pdf("/Users/lakshmichellasamy/Desktop/RAG/knowledge-graph-RAG/sample_data/NEPQ Black Book of Questions (PLEASE DO NOT SHARE).pdf")

kg = KGBuilder(
    os.getenv("NEO4J_URI"),
    os.getenv("NEO4J_USERNAME"),
    os.getenv("NEO4J_PASSWORD")
)

kg.add_document(pdf_text)

print("PDF added to Neo4j Knowledge Graph!")

