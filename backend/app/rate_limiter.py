from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass, field
from threading import Lock
from typing import Optional

from fastapi import HTTPException, Request, status


@dataclass
class RateLimitEntry:
    attempts: int = 0
    window_start: float = field(default_factory=time.time)
    blocked_until: Optional[float] = None


class RateLimiter:
    def __init__(
        self,
        max_attempts: int = 5,
        window_seconds: int = 60,
        block_seconds: int = 60,
        max_block_seconds: int = 3600,
    ):
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        self.block_seconds = block_seconds
        self.max_block_seconds = max_block_seconds
        self._entries: dict[str, RateLimitEntry] = defaultdict(RateLimitEntry)
        self._lock = Lock()
        self._violation_counts: dict[str, int] = defaultdict(int)
    
    def _get_block_duration(self, key: str) -> int:
        violations = self._violation_counts[key]
        duration = self.block_seconds * (2 ** violations)
        return min(duration, self.max_block_seconds)
    
    def _cleanup_old_entries(self) -> None:
        now = time.time()
        expired_keys = []
        
        for key, entry in self._entries.items():
            block_expired = entry.blocked_until is None or entry.blocked_until < now
            window_expired = (now - entry.window_start) > self.window_seconds * 2
            
            if block_expired and window_expired:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self._entries[key]
            if key in self._violation_counts:
                del self._violation_counts[key]
    
    def check(self, key: str) -> None:
        now = time.time()
        
        with self._lock:
            if len(self._entries) > 100:
                self._cleanup_old_entries()
            
            entry = self._entries[key]
            
            if entry.blocked_until and entry.blocked_until > now:
                retry_after = int(entry.blocked_until - now)
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Too many attempts. Please try again in {retry_after} seconds.",
                    headers={"Retry-After": str(retry_after)},
                )
            
            if (now - entry.window_start) > self.window_seconds:
                entry.attempts = 0
                entry.window_start = now
                entry.blocked_until = None
            
            entry.attempts += 1
            
            if entry.attempts > self.max_attempts:
                self._violation_counts[key] += 1
                block_duration = self._get_block_duration(key)
                entry.blocked_until = now + block_duration
                
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Too many attempts. Please try again in {block_duration} seconds.",
                    headers={"Retry-After": str(block_duration)},
                )
    
    def reset(self, key: str) -> None:
        with self._lock:
            if key in self._entries:
                del self._entries[key]
            if key in self._violation_counts:
                del self._violation_counts[key]


def get_login_rate_limiter() -> RateLimiter:
    from .config import get_settings
    settings = get_settings()
    return RateLimiter(
        max_attempts=settings.rate_limit_max_attempts,
        window_seconds=settings.rate_limit_window_seconds,
        block_seconds=settings.rate_limit_block_seconds,
        max_block_seconds=3600,
    )

_login_rate_limiter: Optional[RateLimiter] = None
_global_ip_rate_limiter: Optional[RateLimiter] = None


def _get_global_ip_rate_limiter() -> RateLimiter:
    return RateLimiter(
        max_attempts=20,
        window_seconds=60,
        block_seconds=300,
        max_block_seconds=3600,
    )


def login_rate_limiter_check(key: str, client_ip: str) -> None:
    from .config import get_settings
    settings = get_settings()
    global _login_rate_limiter, _global_ip_rate_limiter
    
    if not settings.rate_limit_enabled:
        _login_rate_limiter = None
        _global_ip_rate_limiter = None
        return
    
    if _global_ip_rate_limiter is None:
        _global_ip_rate_limiter = _get_global_ip_rate_limiter()
    _global_ip_rate_limiter.check(client_ip)
    
    if _login_rate_limiter is None:
        _login_rate_limiter = get_login_rate_limiter()
    _login_rate_limiter.check(key)


def login_rate_limiter_reset(key: str, client_ip: str) -> None:
    from .config import get_settings
    settings = get_settings()
    if not settings.rate_limit_enabled:
        return
    
    global _login_rate_limiter
    if _login_rate_limiter is not None:
        _login_rate_limiter.reset(key)


def _is_trusted_proxy(ip: str, trusted_proxies: list[str]) -> bool:
    if not trusted_proxies:
        return False
    
    for proxy in trusted_proxies:
        if proxy == ip:
            return True
        if proxy == "*":
            return True
        if proxy.endswith(".*") and ip.startswith(proxy[:-1]):
            return True
    
    return False


def get_client_ip(request: Request) -> str:
    from .config import get_settings
    settings = get_settings()
    
    direct_ip = request.client.host if request.client else "unknown"
    
    if not _is_trusted_proxy(direct_ip, settings.trusted_proxies):
        return direct_ip
    
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()
    
    return direct_ip
