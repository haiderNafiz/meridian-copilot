from typing import List
from .base import ChunkStrategy

class SlidingWindowChunker(ChunkStrategy):
    def __init__(self, window_size: int = 200, overlap: int = 50):
        self.window_size = window_size
        self.overlap = overlap

    def chunk(self, text: str) -> List[str]:
        if not text:
            return []
        chunks = []
        start = 0
        text_len = len(text)
        
        while start < text_len:
            end = min(start + self.window_size, text_len)
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append(chunk_text)
            start += (self.window_size - self.overlap)
            if start >= text_len or end == text_len:
                break
        return chunks
