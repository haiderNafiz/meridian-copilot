from typing import List
from ..schema import ChunkingConfig

def chunk_text(text: str, config: ChunkingConfig) -> List[str]:
    """
    Chunks input text using the provided ChunkingConfig parameters.
    """
    if not text:
        return []
        
    size = config.chunk_size
    overlap = config.overlap
    
    # Validation boundary guards
    if size <= 0:
        size = 500
    if overlap >= size or overlap < 0:
        overlap = 0
        
    chunks = []
    
    if config.strategy == "character":
        start = 0
        text_len = len(text)
        
        while start < text_len:
            end = start + size
            chunk = text[start:end]
            chunks.append(chunk)
            
            # Move index with overlap spacing
            start += (size - overlap)
            # Break condition if we cannot progress
            if size - overlap <= 0:
                break
    else:
        # Default fallback to simple fixed-size splitting
        chunks = [text[i:i+size] for i in range(0, len(text), size)]
        
    return chunks
