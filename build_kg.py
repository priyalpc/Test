from neo4j import GraphDatabase
import re
from langchain_text_splitters import RecursiveCharacterTextSplitter

class KGBuilder:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=100
        )

    def close(self):
        self.driver.close()

    def add_document(self, text: str):
        """
        Build a simple Knowledge Graph:
        - split text into chunks
        - extract simple 'entities' (capitalized words)
        - create Chunk nodes
        - create Entity nodes
        - connect Entity -> Chunk with :MENTIONS
        """

        chunks = self.splitter.split_text(text)

        with self.driver.session() as session:
            for i, chunk in enumerate(chunks):
                # Create chunk node
                session.run(
                    """
                    CREATE (c:Chunk {
                        chunk_id: $chunk_id,
                        text: $text
                    })
                    """,
                    chunk_id=i,
                    text=chunk
                )

                # Extract basic entities using capitalized words
                raw_entities = set(re.findall(r"\b[A-Z][a-zA-Z]+\b", chunk))

                for ent in raw_entities:
                    # Merge entity nodes
                    session.run(
                        """
                        MERGE (e:Entity {name: $name})
                        """,
                        name=ent
                    )

                    # Create relationship
                    session.run(
                        """
                        MATCH (e:Entity {name: $name})
                        MATCH (c:Chunk {chunk_id: $chunk_id})
                        MERGE (e)-[:MENTIONS]->(c)
                        """,
                        name=ent,
                        chunk_id=i
                    )

