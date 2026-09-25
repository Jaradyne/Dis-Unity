#!/usr/bin/env python3
"""One explicitly pinned, zero-price OpenRouter route. No fallbacks or model tools."""
from decimal import Decimal, InvalidOperation
import json
import os
import re
import socket
import urllib.error
import urllib.parse
import urllib.request

import cycle
import scout

MODEL = "nvidia/nemotron-3-super-120b-a12b:free"
CATALOG = f"https://openrouter.ai/api/v1/models/{MODEL}/endpoints"
ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"


class ProviderFailure(Exception):
    def __init__(self, category, reason, *, brake=False, cooldown_hours=12):
        super().__init__(reason)
        self.category, self.brake, self.cooldown_hours = category, brake, cooldown_hours


def check_spend(value):
    """A positive receipt closes Week One; missing cost is still unverified."""
    try:
        amount = Decimal(str(value))
        if amount.is_finite() and amount > 0:
            raise ProviderFailure("spend_detected", f"Positive provider cost reported (USD {amount}); stop Week One", brake=True)
    except InvalidOperation:
        pass


def request_json(url, *, payload=None, key=None):
    scout.checked_url(url, ["openrouter.ai"])
    headers = {"Accept": "application/json", "User-Agent": "Dis-Unity-Week-One/1"}
    if key:
        headers.update(Authorization=f"Bearer {key}", **{"X-OpenRouter-Metadata": "enabled"})
    data = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(url, headers=headers, data=data)
    try:
        with urllib.request.build_opener(scout.NoRedirect()).open(request, timeout=120 if data else 25) as response:
            body = response.read(512001)
        if len(body) > 512000:
            raise ProviderFailure("invalid_response", "Response exceeded size bound", brake=True)
        return json.loads(body)
    except urllib.error.HTTPError as exc:
        # Do not persist raw provider error bodies, which can echo request/credential data.
        if exc.code == 429:
            raise ProviderFailure("daily_quota_exhausted", "HTTP 429; defer at least 24 hours", cooldown_hours=24) from None
        if exc.code in (401, 402, 403):
            raise ProviderFailure("auth_or_configuration_error", f"HTTP {exc.code}; explicit operator review required", brake=True) from None
        if exc.code in (404, 400, 422):
            raise ProviderFailure("model_unavailable", f"HTTP {exc.code}; bounded route unavailable") from None
        raise ProviderFailure("transient_capacity", f"HTTP {exc.code}; retry only in a later unit") from None
    except (socket.timeout, TimeoutError, urllib.error.URLError):
        raise ProviderFailure("transport_timeout", "Transport did not return a verifiable result; no immediate repeat") from None
    except (ValueError, cycle.CycleError):
        raise ProviderFailure("invalid_response", "Invalid JSON or unapproved redirect", brake=True) from None


def zero(value):
    try:
        return value is not None and Decimal(str(value)) == 0
    except InvalidOperation:
        return False


def verify_catalog(data):
    if data.get("data", {}).get("id") != MODEL:
        raise ProviderFailure("policy_blocked", "Catalog model identity differs", brake=True)
    endpoints = data.get("data", {}).get("endpoints", [])
    allowed = []
    for endpoint in endpoints:
        prices = endpoint.get("pricing", {})
        if (endpoint.get("model_id") == MODEL and endpoint.get("provider_name", "").casefold() == "nvidia"
                and endpoint.get("tag") == "nvidia" and endpoint.get("status") == 0
                and zero(prices.get("prompt")) and zero(prices.get("completion"))
                and all(zero(v) for v in prices.values())):
            allowed.append({"provider_name": "Nvidia", "tag": "nvidia", "pricing": prices,
                            "status": 0, "supported_parameters": endpoint.get("supported_parameters", [])})
    if not allowed:
        raise ProviderFailure("model_unavailable", "Pinned Nvidia zero-price endpoint is unavailable")
    return {"model": MODEL, "verified_at": cycle.now(), "catalog_url": CATALOG, "endpoints": allowed}


def payload(prompt):
    return {"model": MODEL, "messages": [{"role": "user", "content": prompt}],
            "stream": False, "max_tokens": 6000, "temperature": 0.2,
            "reasoning": {"effort": "low", "exclude": True},
            "response_format": {"type": "json_object"},
            "usage": {"include": True},
            "plugins": [{"id": name, "enabled": False} for name in ['web', 'file-parser', 'response-healing']],
            "provider": {"only": ["nvidia"], "order": ["nvidia"], "ignore": ["groq"],
                         "allow_fallbacks": False, "require_parameters": True,
                         "max_price": {"prompt": 0, "completion": 0, "request": 0, "image": 0}}}


def validate_payload(value):
    expected = payload(value.get("messages", [{}])[0].get("content", ""))
    if value != expected or not expected["messages"][0]["content"]:
        raise ProviderFailure("policy_blocked", "Request differs from the reviewed fixed adapter", brake=True)


def model_matches(value):
    return bool(re.fullmatch(r"nvidia/nemotron-3-super-120b-a12b(?:-\d{8})?(?::free)?", str(value)))


def verify_routing_metadata(response):
    metadata = response.get("openrouter_metadata") or {}
    selected = [e for e in metadata.get("endpoints", {}).get("available", []) if e.get("selected")]
    attempts = metadata.get("attempts", [])
    if (metadata.get('requested') not in (None, MODEL) or metadata.get('is_byok') is True
            or any(e.get('provider') is not None and str(e['provider']).casefold() != 'nvidia'
                   for e in selected + attempts)
            or any(e.get('model') is not None and not model_matches(e['model']) for e in selected + attempts)):
        raise ProviderFailure('policy_blocked', 'Contradictory routing metadata', brake=True)
    return selected


def verify_receipt(response, audit):
    data = audit.get("data", {})
    check_spend(data.get("total_cost"))
    served_model = str(data.get("model", ""))
    verify_routing_metadata(response)
    fields = ('id', 'provider_name', 'is_byok', 'total_cost', 'model')
    checks = {
        "id_match": data.get("id") == response.get("id"),
        "provider_nvidia": str(data.get("provider_name", "")).casefold() == "nvidia",
        "non_byok": data.get("is_byok") is False,
        "zero_cost": zero(data.get("total_cost")),
        "model_family": model_matches(served_model),
    }
    # Known contradictions brake. Missing receipt fields remain a GET recovery task.
    for field, check in zip(fields, checks.values()):
        if data.get(field) is not None and not check:
            safe = {k: data.get(k) for k in fields}
            raise ProviderFailure("policy_blocked", "Generation receipt mismatch: " + json.dumps(safe, sort_keys=True), brake=True)
    if not all(checks.values()):
        raise ProviderFailure("audit_pending", "Saved generation has an incomplete receipt; recover by ID")
    return {k: data.get(k) for k in ("id", "model", "provider_name", "total_cost", "is_byok",
                                    "tokens_prompt", "tokens_completion", "generation_time", "created_at")}


def complete(response, *, transport=request_json, recovery_hours=12):
    """Audit/recover an already saved generation without making another inference POST."""
    if isinstance(response.get('usage'), dict):
        check_spend(response['usage'].get('cost'))
        if response['usage'].get('is_byok') is True:
            raise ProviderFailure('policy_blocked', 'Saved usage reports BYOK', brake=True)
    verify_routing_metadata(response)
    if response.get('model') and not model_matches(response['model']):
        raise ProviderFailure('policy_blocked', 'Saved response model differs', brake=True)
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        raise ProviderFailure("auth_or_configuration_error", "Audit key is absent", brake=True, cooldown_hours=24)
    generation_id = response.get("id")
    if not isinstance(generation_id, str) or not generation_id.startswith("gen-") or len(generation_id) > 180:
        raise ProviderFailure("invalid_response", "Missing generation identity", brake=True)
    try:
        audit = transport("https://openrouter.ai/api/v1/generation?id=" + urllib.parse.quote(generation_id, safe=""), key=key)
    except ProviderFailure as exc:
        if not exc.brake:
            delay = exc.cooldown_hours if exc.category == 'daily_quota_exhausted' else recovery_hours
            raise ProviderFailure("audit_pending", "Saved generation awaits its audit; recover this receipt without another POST", cooldown_hours=delay) from None
        raise
    try:
        receipt = verify_receipt(response, audit)
    except ProviderFailure as exc:
        if exc.category == 'audit_pending':
            exc.cooldown_hours = recovery_hours
        raise
    if response.get("choices"):
        result = parse_result(response)
    else:
        try:
            content = transport("https://openrouter.ai/api/v1/generation/content?id="
                                + urllib.parse.quote(generation_id, safe=""), key=key)
            completion = content["data"]["output"]["completion"]
            result = json.loads(completion)
            if not isinstance(result, dict):
                raise ValueError("Object required")
        except ProviderFailure as exc:
            if not exc.brake:
                delay = exc.cooldown_hours if exc.category == 'daily_quota_exhausted' else recovery_hours
                raise ProviderFailure("audit_pending", "Generation exists but stored completion is not ready; recover by ID without another POST",
                                      cooldown_hours=delay) from None
            raise
        except (KeyError, TypeError, ValueError):
            raise ProviderFailure("invalid_response", "Stored generation content is not one complete JSON object") from None
    return {"result": result, "receipt": receipt}


def public_response(response):
    """Keep the visible answer and zero-cost receipt fields; exclude hidden reasoning."""
    return {"id": response.get("id"), "model": response.get("model"),
            "openrouter_metadata": response.get("openrouter_metadata", {}),
            "usage": response.get("usage", {}),
            "choices": [{"finish_reason": c.get("finish_reason"),
                         "message": {"content": c.get("message", {}).get("content")}}
                        for c in response.get("choices", [])[:1]]}


def parse_result(response):
    try:
        choice = response["choices"][0]
        if choice.get("finish_reason") != "stop":
            raise ValueError("Incomplete response")
        result = json.loads(choice["message"]["content"])
        if not isinstance(result, dict):
            raise ValueError("Object required")
        return result
    except (KeyError, TypeError, ValueError, IndexError):
        raise ProviderFailure("invalid_response", "Provider output is not one complete JSON object") from None


def verify_inline_receipt(response):
    """Establish zero-cost/non-BYOK/provider identity from the original completion response."""
    usage = response.get("usage", {})
    if isinstance(usage, dict):
        check_spend(usage.get("cost"))
    selected = verify_routing_metadata(response)
    if (isinstance(usage, dict) and (usage.get('is_byok') is True or
            (usage.get('cost') is not None and not zero(usage['cost'])))):
        raise ProviderFailure("policy_blocked", "Inline usage contradicts the zero-cost non-BYOK route", brake=True)
    if response.get("model") and not model_matches(response['model']):
        raise ProviderFailure("policy_blocked", "Response model differs from the pinned free model", brake=True)
    if not isinstance(response.get('id'), str) or not response['id'].startswith('gen-'):
        raise ProviderFailure('invalid_response', 'Missing generation identity', brake=True)
    if (not isinstance(usage, dict) or not zero(usage.get('cost')) or usage.get('is_byok') is not False
            or not response.get('model') or len(selected) != 1
            or str(selected[0].get('provider', '')).casefold() != 'nvidia'):
        raise ProviderFailure('audit_pending', 'Inline receipt is incomplete; audit the saved generation')
    return {"source": "inline_usage", "id": response.get("id"), "model": response.get("model"),
            "provider_name": selected[0].get("provider"), "total_cost": usage.get("cost"),
            "is_byok": usage.get("is_byok"), "tokens_prompt": usage.get("prompt_tokens"),
            "tokens_completion": usage.get("completion_tokens"), "verified_at": cycle.now()}


def verify_inference_key(data):
    """Confirm the supplied credential is an inference key without retaining account metadata."""
    row = data.get("data")
    if not isinstance(row, dict):
        raise ProviderFailure("auth_or_configuration_error", "Current-key preflight returned no usable key metadata", brake=True)
    if row.get("is_management_key") is True:
        raise ProviderFailure("auth_or_configuration_error", "Management key cannot be used for inference", brake=True)
    return {"authenticated": True, "is_management_key": False, "verified_at": cycle.now()}


def call(value, transport=request_json, checkpoint=lambda value: None, *, recovery_hours=12):
    validate_payload(value)
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        raise ProviderFailure("auth_or_configuration_error", "OPENROUTER_API_KEY is absent; no call made", brake=True, cooldown_hours=24)
    catalog = verify_catalog(transport(CATALOG))
    key_preflight = verify_inference_key(transport("https://openrouter.ai/api/v1/key", key=key))
    response = transport(ENDPOINT, payload=value, key=key)
    response = public_response(response)
    checkpoint(response)  # Persist the visible generation ID/body BEFORE verification/review.
    usage = response.get("usage", {})
    if isinstance(usage, dict):
        check_spend(usage.get("cost"))
    try:
        receipt = verify_inline_receipt(response)
        if not response.get('choices'):
            raise ProviderFailure('audit_pending', 'Retrieve saved completion by ID')
        result = parse_result(response)
    except ProviderFailure as exc:
        if exc.category != 'audit_pending':
            raise
        recovered = complete(response, transport=transport, recovery_hours=recovery_hours)
        receipt, result = recovered["receipt"], recovered["result"]
    return {"result": result, "receipt": receipt,
            "catalog": catalog, "key_preflight": key_preflight}
