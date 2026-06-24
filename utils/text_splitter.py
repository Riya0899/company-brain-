from langchain_text_splitters import RecursiveCharacterTextSplitter

def spit_text_into_chunks(text):
    splitter=RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200  # overlap preserves context
        )
    chunks=splitter.split_text(text)
    return chunks