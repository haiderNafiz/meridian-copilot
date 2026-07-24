import pytest
import json
from src.intelligence.tools.deterministic_enricher.normalizers.email import normalize_email, extract_domain
from src.intelligence.tools.deterministic_enricher.normalizers.urls import normalize_website, normalize_linkedin, normalize_github
from src.intelligence.tools.deterministic_enricher.normalizers.phone import normalize_phone
from src.intelligence.tools.deterministic_enricher.normalizers.company import normalize_company
from src.intelligence.tools.deterministic_enricher.normalizers.geography import normalize_country, infer_timezone
from src.intelligence.tools.deterministic_enricher.normalizers.technologies import normalize_technologies

def test_email_normalizer():
    # Valid
    val, src, conf, status, evidence = normalize_email(" USER@Google.COM ")
    assert val == "user@google.com"
    assert status == "valid"
    assert conf == 1.0
    
    # Invalid
    val, src, conf, status, evidence = normalize_email("not-valid-email")
    assert val == "not-valid-email"
    assert status == "invalid"
    assert conf == 0.5
    
    # Extract domain
    assert extract_domain("user@google.com") == "google.com"
    assert extract_domain(None) is None

def test_urls_normalizer():
    # Website
    val, src, conf, status, evidence = normalize_website("google.com/")
    assert val == "https://google.com"
    assert status == "valid"
    
    # LinkedIn
    val, src, conf, status, evidence = normalize_linkedin("https://www.linkedin.com/in/alex-smith/")
    assert val == "https://www.linkedin.com/in/alex-smith"
    assert status == "valid"
    
    # LinkedIn Username only
    val, src, conf, status, evidence = normalize_linkedin("alex-smith")
    assert val == "https://www.linkedin.com/in/alex-smith"
    
    # GitHub
    val, src, conf, status, evidence = normalize_github("https://github.com/defunkt/")
    assert val == "https://github.com/defunkt"
    
    # GitHub username only
    val, src, conf, status, evidence = normalize_github("defunkt")
    assert val == "https://github.com/defunkt"

def test_phone_normalizer():
    # Formatting stripped
    val, src, conf, status, evidence = normalize_phone("+1 (555) 019-2834")
    assert val == "+15550192834"
    assert status == "valid"
    
    # Too short / bad format
    val, src, conf, status, evidence = normalize_phone("123")
    assert val == "123"
    assert status == "invalid"
    assert conf == 0.6

def test_company_normalizer():
    # Legal suffix stripping
    val, src, conf, status, evidence = normalize_company("Google Inc.")
    assert val == "Google"
    assert "corporate legal suffix" in evidence[0].lower()
    
    val, src, conf, status, evidence = normalize_company("Tesla LLC")
    assert val == "Tesla"
    
    val, src, conf, status, evidence = normalize_company("My Company Ltd.")
    assert val == "My Company"

def test_geography_normalizer():
    # Country canonical mapping
    val, src, conf, status, evidence = normalize_country("USA")
    assert val == "United States"
    assert conf == 1.0
    
    # Timezone matching
    tz, src, conf, status, evidence = infer_timezone("United States", "Lives in San Francisco, California")
    assert tz == "America/Los_Angeles"
    assert conf == 0.8
    
    # Timezone country fallback
    tz, src, conf, status, evidence = infer_timezone("United Kingdom", None)
    assert tz == "Europe/London"
    assert conf == 1.0

def test_technologies_normalizer():
    val, src, conf, status, evidence = normalize_technologies(["js", "REACTJS", "Python", "gcp"])
    assert "JavaScript" in val
    assert "React" in val
    assert "Python" in val
    assert "GCP" in val

from src.intelligence.tools.deterministic_enricher.schema import EnrichmentInput
from src.intelligence.tools.deterministic_enricher.service import DeterministicEnrichmentService

def test_enricher_service_full_pipeline():
    service = DeterministicEnrichmentService()
    
    inp = EnrichmentInput(
        company_name="Google LLC",
        website="google.com",
        email="info@google.com",
        linkedin_url="https://www.linkedin.com/in/larrypage/",
        github_url="https://github.com/google",
        phone_number="+1-800-555-0199",
        country="US",
        location="Headquarters in Mountain View",
        technology_keywords=["js", "py", "k8s"]
    )
    
    output = service.process(inp)
    
    assert output.status.value == "success"
    assert output.metadata.provider == "deterministic"
    assert output.metadata.model == "rule-engine-v1"
    
    payload = output.payload
    assert payload.company_name.normalized_value == "Google"
    assert payload.website.normalized_value == "https://google.com"
    assert payload.email.normalized_value == "info@google.com"
    assert payload.linkedin_url.normalized_value == "https://www.linkedin.com/in/larrypage"
    assert payload.github_url.normalized_value == "https://github.com/google"
    assert payload.phone_number.normalized_value == "+18005550199"
    assert payload.country.normalized_value == "United States"
    assert "JavaScript" in payload.technology_keywords.normalized_value
    
    # Assert Derived values (Enrichments)
    assert payload.company_domain.normalized_value == "google.com"
    assert payload.timezone.normalized_value == "America/New_York"

def test_enricher_domain_from_email_only():
    service = DeterministicEnrichmentService()
    
    # Corporate email
    inp1 = EnrichmentInput(email="recruiter@stripe.com")
    out1 = service.process(inp1)
    assert out1.payload.company_domain.normalized_value == "stripe.com"
    assert out1.payload.company_domain.confidence == 0.9
    
    # Generic/free email
    inp2 = EnrichmentInput(email="john.doe@gmail.com")
    out2 = service.process(inp2)
    assert out2.payload.company_domain.normalized_value is None
    assert out2.payload.company_domain.validation_status == "invalid"

from src.intelligence.platform.test_utils import run_mcp_session

def test_mcp_enrich_entity_success():
    call_req = {
        "jsonrpc": "2.0",
        "id": 201,
        "method": "tools/call",
        "params": {
            "name": "enrich_entity",
            "arguments": {
                "company_name": "Google LLC",
                "email": "larry@google.com",
                "website": "www.google.com",
                "linkedin_url": "larrypage",
                "country": "USA",
                "location": "Lives in London",
                "technology_keywords": ["js", "py"]
            }
        }
    }
    
    responses, stderr_lines = run_mcp_session([call_req])
    
    assert len(responses) == 1
    resp = json.loads(responses[0])
    assert "result" in resp
    assert "content" in resp["result"]
    
    content_raw = resp["result"]["content"][0]["text"]
    content_data = json.loads(content_raw)
    
    # Assert JSON-RPC response fields
    assert content_data["status"] == "success"
    payload = content_data["payload"]
    assert payload["company_name"]["normalized_value"] == "Google"
    assert payload["company_domain"]["normalized_value"] == "google.com"
    assert payload["timezone"]["normalized_value"] == "Europe/London" # London matched in location
    
    # Assert telemetry logs in stderr
    json_logs = []
    for line in stderr_lines:
        try:
            parsed = json.loads(line)
            if "request_id" in parsed:
                json_logs.append(parsed)
        except json.JSONDecodeError:
            continue
            
    assert len(json_logs) == 1
    log = json_logs[0]
    assert log["tool_name"] == "enrich_entity"
    assert log["provider"] == "deterministic"
    assert log["model"] == "rule-engine-v1"
    assert log["status"] == "success"


