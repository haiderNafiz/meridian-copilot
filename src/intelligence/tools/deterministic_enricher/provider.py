from typing import Optional
from .schema import EnrichmentInput, EnrichmentPayload, FieldResult
from .normalizers.email import normalize_email, extract_domain
from .normalizers.urls import normalize_website, normalize_linkedin, normalize_github
from .normalizers.phone import normalize_phone
from .normalizers.company import normalize_company
from .normalizers.geography import normalize_country, infer_timezone
from .normalizers.technologies import normalize_technologies
from .constants.email_domains import FREE_EMAIL_DOMAINS

class DeterministicEnrichmentProvider:
    def infer(self, request: EnrichmentInput) -> EnrichmentPayload:
        # Stage 1 & 2: Normalization and Validation Stages
        email_val, email_src, email_conf, email_status, email_evidence = normalize_email(request.email)
        email_res = FieldResult(
            normalized_value=email_val,
            source=email_src,
            confidence=email_conf,
            validation_status=email_status,
            evidence=email_evidence
        ) if request.email is not None else None
        
        web_val, web_src, web_conf, web_status, web_evidence = normalize_website(request.website)
        web_res = FieldResult(
            normalized_value=web_val,
            source=web_src,
            confidence=web_conf,
            validation_status=web_status,
            evidence=web_evidence
        ) if request.website is not None else None
        
        li_val, li_src, li_conf, li_status, li_evidence = normalize_linkedin(request.linkedin_url)
        li_res = FieldResult(
            normalized_value=li_val,
            source=li_src,
            confidence=li_conf,
            validation_status=li_status,
            evidence=li_evidence
        ) if request.linkedin_url is not None else None
        
        gh_val, gh_src, gh_conf, gh_status, gh_evidence = normalize_github(request.github_url)
        gh_res = FieldResult(
            normalized_value=gh_val,
            source=gh_src,
            confidence=gh_conf,
            validation_status=gh_status,
            evidence=gh_evidence
        ) if request.github_url is not None else None
        
        phone_val, phone_src, phone_conf, phone_status, phone_evidence = normalize_phone(request.phone_number)
        phone_res = FieldResult(
            normalized_value=phone_val,
            source=phone_src,
            confidence=phone_conf,
            validation_status=phone_status,
            evidence=phone_evidence
        ) if request.phone_number is not None else None
        
        country_val, country_src, country_conf, country_status, country_evidence = normalize_country(request.country)
        country_res = FieldResult(
            normalized_value=country_val,
            source=country_src,
            confidence=country_conf,
            validation_status=country_status,
            evidence=country_evidence
        ) if request.country is not None else None
        
        comp_val, comp_src, comp_conf, comp_status, comp_evidence = normalize_company(request.company_name)
        comp_res = FieldResult(
            normalized_value=comp_val,
            source=comp_src,
            confidence=comp_conf,
            validation_status=comp_status,
            evidence=comp_evidence
        ) if request.company_name is not None else None
        
        tech_val, tech_src, tech_conf, tech_status, tech_evidence = normalize_technologies(request.technology_keywords)
        tech_res = FieldResult(
            normalized_value=tech_val,
            source=tech_src,
            confidence=tech_conf,
            validation_status=tech_status,
            evidence=tech_evidence
        ) if request.technology_keywords is not None else None
        
        # Stage 3: Enrichment Stage (Derived Values)
        # Derive company domain
        domain_val = None
        domain_evidence = []
        domain_status = "unverified"
        domain_confidence = 1.0
        
        if web_val:
            from urllib.parse import urlparse
            parsed_url = urlparse(web_val)
            domain_candidate = parsed_url.netloc
            if domain_candidate.startswith("www."):
                domain_candidate = domain_candidate[4:]
            if domain_candidate:
                domain_val = domain_candidate
                domain_evidence.append(f"Extracted domain '{domain_val}' from normalized website URL")
                domain_status = "valid"
                domain_confidence = 1.0
                
        if not domain_val and email_val:
            email_domain = extract_domain(email_val)
            if email_domain:
                if email_domain in FREE_EMAIL_DOMAINS:
                    domain_evidence.append(f"Ignored generic/free email domain '{email_domain}'")
                    domain_status = "invalid"
                    domain_confidence = 0.5
                else:
                    domain_val = email_domain
                    domain_evidence.append(f"Extracted domain '{domain_val}' from corporate email address")
                    domain_status = "valid"
                    domain_confidence = 0.9
                    
        domain_res = FieldResult(
            normalized_value=domain_val,
            source="enricher_domain",
            confidence=domain_confidence,
            validation_status=domain_status,
            evidence=domain_evidence
        ) if (web_val or email_val) else None
        
        # Derive timezone
        tz_val = None
        tz_src = "enricher_timezone"
        tz_conf = 1.0
        tz_status = "unverified"
        tz_evidence = []
        
        c_val = country_val if country_val else request.country
        if c_val or request.location:
            tz_val, tz_src, tz_conf, tz_status, tz_evidence = infer_timezone(country_val, request.location)
            
        tz_res = FieldResult(
            normalized_value=tz_val,
            source=tz_src,
            confidence=tz_conf,
            validation_status=tz_status,
            evidence=tz_evidence
        ) if (c_val or request.location) else None
        
        # Stage 4: Payload Assembly Stage
        return EnrichmentPayload(
            company_name=comp_res,
            website=web_res,
            email=email_res,
            linkedin_url=li_res,
            github_url=gh_res,
            phone_number=phone_res,
            country=country_res,
            technology_keywords=tech_res,
            timezone=tz_res,
            company_domain=domain_res
        )
