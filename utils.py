def normalize_collection_name(role: str) -> str:
    """
    Normalizes a role string into a valid Chroma collection name.
    
    ChromaDB requires names to be 3-512 characters and only contain 
    alphanumeric characters, underscores, dashes, or dots.
    """
    safe_name = role.lower().strip()
    
    if len(safe_name) < 3:
        safe_name = f"{safe_name}_col"
    
    valid_chars = set('abcdefghijklmnopqrstuvwxyz0123456789_-')
    normalized_name = "".join(c for c in safe_name if c in valid_chars)
    
    if not normalized_name:
        return "default_col"
    
    if not normalized_name[0].isalnum():
        normalized_name = f"a{normalized_name}"
    
    if not normalized_name[-1].isalnum():
        normalized_name = f"{normalized_name}a"

    return normalized_name[:512]