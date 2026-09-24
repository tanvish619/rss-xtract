import hashlib
import json


def calculate_config_hash(
    url: str,
    configuration: dict,
) -> str:

    payload = {
        "url": url,
        "configuration": configuration,
    }

    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )

    return hashlib.sha256(
        canonical.encode("utf-8")
    ).hexdigest()
