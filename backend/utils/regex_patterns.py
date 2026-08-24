"""
Pre-compiled regex patterns for log parsing.
Compile once at import, reuse everywhere.
Build target: Month 1.
"""

import re

# Apache Combined Log Format
APACHE_CLF = re.compile(
    r"(?P<ip>\S+) \S+ \S+ \[(?P<time>[^\]]+)\] "
    r'"(?P<method>\S+) (?P<path>\S+) \S+" '
    r"(?P<status>\d{3}) (?P<size>\S+)"
    r'(?: "(?P<referer>[^"]*)" "(?P<ua>[^"]*)")?'
)

# SSH failed/accepted auth
AUTH_SSH = re.compile(
    r"(?P<month>\w+)\s+(?P<day>\d+) (?P<time>\S+) \S+ sshd\[\d+\]: "
    r"(?P<result>Failed|Accepted) (?P<method>\w+) for (?P<user>\S+) "
    r"from (?P<ip>\S+) port (?P<port>\d+)"
)

# sudo usage
AUTH_SUDO = re.compile(
    r"(?P<month>\w+)\s+(?P<day>\d+) (?P<time>\S+) \S+ sudo\[\d+\]: "
    r"(?P<user>\S+) : TTY=\S+ ; PWD=\S+ ; USER=(?P<as_user>\S+) ; COMMAND=(?P<cmd>.+)"
)
