from typing import Dict

# Estado global en memoria (por proceso)
LOANS: Dict[str, dict] = {}
BOOK_STATUS: Dict[str, str] = {}  # book_id -> "available" | "loaned"