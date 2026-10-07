"""Normalized symbol keys: no source-language parsing or case policy."""

def method_key(symbol, member, project):
    return (symbol, member, project) if symbol and member else None

def method_label(key):
    return f"{key[2] or '<unknown>'}::{key[0]}.{key[1]}"

def class_id(key):
    return f"{key[2] or '<unknown>'}::{key[0]}"

def entry_method_key(entry):
    return entry.get('method_key')

def resolved_method_key(call):
    return call.get('target_key')
