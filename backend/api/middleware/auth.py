"""
API key validation middleware.
Key loaded from environment — constant-time comparison to prevent timing attacks.

Build target: Month 2.
Security note: Use hmac.compare_digest(), never ==, for key comparison.
"""

# TODO Month 2
