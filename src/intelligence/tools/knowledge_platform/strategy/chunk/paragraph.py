import re
from typing import List
from .base import ChunkStrategy

class ParagraphChunker(ChunkStrategy):
    def chunk(self, text: str) -> List[str]:
        if not text:
            return []
        paragraphs = re.split(r'\n\s*\n', text)
        return [p.strip() for p in paragraphs if p.strip()]
