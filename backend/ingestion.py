from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext, Document
from llama_index.core.node_parser import CodeSplitter
from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from tree_sitter_languages import get_parser
import psycopg2
from config import *


def ingest_codebase(repo_path: str):
    embed_model = HuggingFaceEmbedding(model_name=EMBED_MODEL)

    vector_store = PGVectorStore.from_params(
        database=DB_NAME,
        host=DB_HOST,
        password=DB_PASSWORD,
        port=DB_PORT,
        user=DB_USER,
        table_name="code_nodes",
        embed_dim=768,
    )

    # Manually instantiate the parser to bypass the broken language pack
    parser = get_parser("python")

    code_splitter = CodeSplitter(
        language="python",
        chunk_lines=30,
        chunk_lines_overlap=15,
        max_chars=1800,
        parser=parser,
    )

    documents = SimpleDirectoryReader(
        input_dir=repo_path,
        required_exts=[".py", ".js", ".ts", ".java", ".md"],
        exclude_hidden=True,
    ).load_data()

    # Convert all document content to strings with proper encoding
    for doc in documents:
        content = doc.get_content()
        if isinstance(content, bytes):
            try:
                doc.set_content(content.decode('utf-8'))
            except UnicodeDecodeError:
                doc.set_content(content.decode('utf-8', errors='ignore'))

    nodes = code_splitter.get_nodes_from_documents(documents)

    for node in nodes:
        node.metadata.update({
            "file_path": node.metadata.get("file_path", ""),
            "function_name": node.metadata.get("function_name", ""),
            "class_name": node.metadata.get("class_name", ""),
            "language": "python",
            "node_type": "function" if node.metadata.get("function_name") else "class" if node.metadata.get(
                "class_name") else "module",
        })

    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex(nodes=nodes, storage_context=storage_context, embed_model=embed_model, show_progress=True)

    print(f"✅ Indexed {len(nodes)} AST-based chunks from codebase")
    return index
