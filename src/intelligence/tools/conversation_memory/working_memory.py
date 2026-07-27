import re
from typing import List, Dict, Any, Optional
from .schema import ConversationTurn, WorkingMemory

def parse_turn_metadata(text: str) -> Dict[str, Any]:
    # Extract candidate email
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    email = email_match.group(0) if email_match else None
    
    # Extract phone
    phone_match = re.search(r'\+?\d[\d -]{7,}\d', text)
    phone = phone_match.group(0) if phone_match else None
    
    entities = {}
    if email:
        entities["email"] = email
    if phone:
        entities["phone"] = phone
        
    return entities

def extract_questions_and_actions(text: str) -> tuple[List[str], List[str]]:
    questions = []
    actions = []
    
    # Split sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)
    for sent in sentences:
        sent_strip = sent.strip()
        if not sent_strip:
            continue
        if sent_strip.endswith('?'):
            questions.append(sent_strip)
        elif any(kw in sent_strip.lower() for kw in ["todo", "will ", "action:", "must"]):
            actions.append(sent_strip)
            
    return questions, actions

class WorkingMemoryManager:
    @staticmethod
    def update_working_memory(wm: WorkingMemory, turn: ConversationTurn) -> None:
        wm.turns.append(turn)
        
        # Merge entities
        if turn.entities:
            wm.active_entities.update(turn.entities)
            
        # Add unresolved questions
        if turn.unresolved_questions:
            wm.unresolved_questions.extend(turn.unresolved_questions)
            
        # Add pending actions
        if turn.pending_actions:
            wm.pending_actions.extend(turn.pending_actions)
            
        # If user answers a question, resolve it (heuristic: if assistant asked a question, user turn removes matching questions)
        if turn.role == "user" and wm.unresolved_questions:
            historical_qs = [q for q in wm.unresolved_questions if q not in turn.unresolved_questions]
            resolved = []
            for q in historical_qs:
                # Only resolve if keywords match and are not trivial
                if any(kw in turn.content.lower() for kw in q.lower().split() if len(kw) > 3):
                    continue
                resolved.append(q)
            wm.unresolved_questions = resolved + turn.unresolved_questions
