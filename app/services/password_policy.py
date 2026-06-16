from __future__ import annotations

import re
from collections.abc import Callable
from typing import Any


class PasswordPolicyValidationError(ValueError):
    """Se lanza cuando una contraseña no cumple una o más políticas."""


Validator = Callable[[str, dict[str, Any]], str | None]


def _normalize_policy_name(name: str) -> str:
    return name.strip().lower().replace("-", "_")


def _validate_min_uppercase(password: str, params: dict[str, Any]) -> str | None:
    required = int(params.get("min", 1))
    current = sum(1 for char in password if char.isupper())
    if current < required:
        return f"La contraseña debe tener al menos {required} letra(s) mayúscula(s)"
    return None


def _validate_min_length(password: str, params: dict[str, Any]) -> str | None:
    required = int(params.get("min", 9))
    if len(password) < required:
        return f"La contraseña debe tener al menos {required} caracteres"
    return None


def _validate_min_special(password: str, params: dict[str, Any]) -> str | None:
    required = int(params.get("min", 1))
    matches = re.findall(r"[^A-Za-z0-9]", password)
    if len(matches) < required:
        return f"La contraseña debe tener al menos {required} caracter(es) especial(es)"
    return None


POLICY_REGISTRY: dict[str, Validator] = {
    # Alias semánticos para facilitar crecimiento sin romper clientes actuales.
    "min_uppercase": _validate_min_uppercase,
    "uppercase": _validate_min_uppercase,
    "min_length": _validate_min_length,
    "length": _validate_min_length,
    "min_special": _validate_min_special,
    "special_char": _validate_min_special,
}


def _to_policy_object(raw_policy: str | dict[str, Any]) -> dict[str, Any]:
    if isinstance(raw_policy, str):
        return {"name": raw_policy, "enabled": True, "params": {}}

    name = raw_policy.get("name", "")
    # Si es un Enum, usar su valor
    if hasattr(name, "value"):
        name = name.value

    return {
        "name": str(name).strip(),
        "enabled": bool(raw_policy.get("enabled", True)),
        "params": dict(raw_policy.get("params", {})),
    }


def validate_password_with_policies(
    password: str,
    raw_policies: list[str | dict[str, Any]] | None,
) -> None:
    if not raw_policies:
        return

    errors: list[str] = []

    for raw_policy in raw_policies:
        policy = _to_policy_object(raw_policy)
        if not policy["enabled"]:
            continue

        policy_name = _normalize_policy_name(policy["name"])
        validator = POLICY_REGISTRY.get(policy_name)
        if validator is None:
            # Política desconocida: se ignora para mantener compatibilidad hacia adelante.
            continue

        error = validator(password, policy["params"])
        if error:
            errors.append(error)

    if errors:
        raise PasswordPolicyValidationError("; ".join(errors))

