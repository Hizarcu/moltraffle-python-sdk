class MoltraffleError(Exception):
    """Base exception for moltraffle SDK errors."""
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class MoltraffleValidationError(MoltraffleError):
    """Raised when the API returns validation errors (400)."""
    def __init__(self, message: str, details: list[str] | None = None):
        super().__init__(message, status_code=400)
        self.details = details or []

    def __str__(self) -> str:
        if self.details:
            return f"{super().__str__()}: {'; '.join(self.details)}"
        return super().__str__()


class MoltraffleNotFoundError(MoltraffleError):
    """Raised when a raffle address is not found (404)."""
    def __init__(self, address: str):
        super().__init__(f"Raffle not found: {address}", status_code=404)
        self.address = address
