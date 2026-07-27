import pytest
import json
from src.intelligence.tools.conversation_memory.schema import (
    ConversationTurn,
    WorkingMemory,
    ConversationContext,
    ConversationResult,
    ConversationFailure
)
from src.intelligence.tools.conversation_memory.working_memory import (
    parse_turn_metadata,
    extract_questions_and_actions,
    WorkingMemoryManager
)
from src.intelligence.tools.conversation_memory.state_manager import ConversationStateManager
from src.intelligence.tools.conversation_memory.service import get_conversation_memory_service

def test_metadata_and_heuristics_parsing():
    # 1. Entity parsing
    text = "Send info to larry@example.com or call +442079460958."
    entities = parse_turn_metadata(text)
    assert entities.get("email") == "larry@example.com"
    assert entities.get("phone") == "+442079460958"
    
    # 2. Questions & Actions parsing
    text = "Will we schedule the meeting tomorrow? I must review the profile. Action: call Larry."
    qs, acs = extract_questions_and_actions(text)
    assert len(qs) == 1
    assert qs[0] == "Will we schedule the meeting tomorrow?"
    assert len(acs) == 2
    assert "I must review the profile." in acs
    assert "Action: call Larry." in acs

def test_sliding_window_pruning():
    mgr = ConversationStateManager()
    session_id = "test_sess_prune"
    
    # Add 12 turns
    for i in range(12):
        mgr.add_message_turn(session_id, "user", f"Turn {i}")
        
    _, wm = mgr.get_or_create_session(session_id)
    assert len(wm.turns) == 10
    assert wm.turns[0].content == "Turn 2"
    assert wm.turns[-1].content == "Turn 11"

def test_multi_session_isolation():
    mgr = ConversationStateManager()
    
    mgr.add_message_turn("sess_1", "user", "Hello from Session 1")
    mgr.add_message_turn("sess_2", "user", "Hello from Session 2")
    
    _, wm1 = mgr.get_or_create_session("sess_1")
    _, wm2 = mgr.get_or_create_session("sess_2")
    
    assert len(wm1.turns) == 1
    assert wm1.turns[0].content == "Hello from Session 1"
    
    assert len(wm2.turns) == 1
    assert wm2.turns[0].content == "Hello from Session 2"

def test_conversation_memory_service_success():
    service = get_conversation_memory_service()
    session_id = "service_test_session"
    
    # Post a message turn
    res = service.post_turn(
        session_id=session_id,
        role="user",
        content="Is Larry a Python developer? Let's check. Action: review resume.",
        active_goal="Assess Larry"
    )
    
    assert isinstance(res, ConversationResult)
    assert res.status == "success"
    assert res.context is not None
    assert res.context.active_goal == "Assess Larry"
    assert "Is Larry a Python developer?" in res.context.unresolved_questions
    assert "Action: review resume." in res.context.pending_actions

def test_mcp_conversation_memory_tools():
    from src.intelligence.platform.test_utils import run_mcp_session
    
    req_post = {
        "jsonrpc": "2.0",
        "id": 901,
        "method": "tools/call",
        "params": {
            "name": "post_conversation_turn",
            "arguments": {
                "session_id": "session_mcp_conv_88",
                "role": "user",
                "content": "Can we look at Larry's CV? Action: pull resume.",
                "active_goal": "assess_candidate"
            }
        }
    }
    
    req_get = {
        "jsonrpc": "2.0",
        "id": 902,
        "method": "tools/call",
        "params": {
            "name": "get_conversation_context",
            "arguments": {
                "session_id": "session_mcp_conv_88"
            }
        }
    }
    
    responses, _ = run_mcp_session([req_post, req_get])
    assert len(responses) == 2
    
    # Verify post response
    res1 = json.loads(responses[0])
    content1 = json.loads(res1["result"]["content"][0]["text"])
    assert content1["status"] == "success"
    assert content1["session_id"] == "session_mcp_conv_88"
    
    # Verify get response
    res2 = json.loads(responses[1])
    content2 = json.loads(res2["result"]["content"][0]["text"])
    assert content2["status"] == "success"
    assert content2["context"]["active_goal"] == "assess_candidate"
    assert "Can we look at Larry's CV?" in content2["context"]["unresolved_questions"]
    assert "Action: pull resume." in content2["context"]["pending_actions"]
