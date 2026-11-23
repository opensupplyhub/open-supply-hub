#!/usr/bin/env python3
"""
OSDEV-2138: send a burst of requests to one URL to test the WAF
API rate-based rules (ApiRateLimitPerIp / ApiRateLimitAnonPerIp).

Only uses the Python standard library, so it runs anywhere with Python 3.8+.

Environments: dev.os-hub.net, test.os-hub.net, preprod.os-hub.net,
staging.opensupplyhub.org, rba.opensupplyhub.org, opensupplyhub.org (production).

Examples
--------
  # 700 anonymous requests to staging, 10 at a time (anon rule, limit 500/5 min)
  python scripts/waf_rate_limit_test/waf_rate_limit_test.py --url https://staging.opensupplyhub.org/api/countries/ --count 700

  # Same, but as an API token user (only the 2,000/5 min rule applies)
  OSH_API_TOKEN=xxxx python scripts/waf_rate_limit_test/waf_rate_limit_test.py \
      --url https://staging.opensupplyhub.org/api/countries/ --count 2500 --token-env OSH_API_TOKEN

  # Limit the request rate to 20 per second
  python scripts/waf_rate_limit_test/waf_rate_limit_test.py --url https://test.os-hub.net/api/countries/ --count 600 --rps 20

How to read the results
-----------------------
  * "WAF 429"    - blocked by the WAF rule (body is exactly
                   {"detail": "Request was throttled."}).
  * "Django 429" - throttled by Django ("... Expected available in N seconds.").
  * Other codes (200, 401, 403, ...) still count toward the WAF limit,
    because WAF counts requests before they reach Django.

  In Count mode the WAF never blocks, so no "WAF 429" will appear; check the
  CloudWatch metrics ApiRateLimitPerIp / ApiRateLimitAnonPerIp (us-east-1)
  and the web ACL's sampled requests instead.

  WAF reacts with a delay (usually under a minute), so a few hundred requests
  above the limit may get through before blocking starts.
"""

import argparse
import json
import os
import sys
import threading
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

WAF_BODY = {"detail": "Request was throttled."}
# Environments real users and partners depend on; require --yes for these.
PRODUCTION_HOSTS = {"opensupplyhub.org", "www.opensupplyhub.org", "rba.opensupplyhub.org"}


def parse_args():
    p = argparse.ArgumentParser(
        description="Send N requests to a URL and report how the WAF responds."
    )
    p.add_argument("--url", required=True, help="Full URL to request")
    p.add_argument("--count", type=int, required=True, help="Total number of requests")
    p.add_argument("--concurrency", type=int, default=10, help="Parallel requests (default 10)")
    p.add_argument("--rps", type=float, default=0, help="Max requests per second (0 = no limit)")
    p.add_argument("--method", default="GET", help="HTTP method (default GET)")
    p.add_argument("--timeout", type=float, default=15, help="Per-request timeout in seconds")
    p.add_argument(
        "--token-env",
        help="Name of an env var holding an API token; sends 'Authorization: Token <value>'",
    )
    p.add_argument(
        "--header",
        action="append",
        default=[],
        metavar="'Name: value'",
        help="Extra header, can be repeated (e.g. --header 'Referer: https://...')",
    )
    p.add_argument(
        "--report-every", type=float, default=5, help="Seconds between progress lines"
    )
    p.add_argument(
        "--yes", action="store_true", help="Don't ask for confirmation (needed for production)"
    )
    return p.parse_args()


class Stats:
    def __init__(self):
        self.lock = threading.Lock()
        self.codes = Counter()
        self.sent = 0
        self.first_waf_block = None  # (request number, seconds since start)
        self.start = time.monotonic()

    def record(self, label):
        with self.lock:
            self.sent += 1
            self.codes[label] += 1
            if label == "WAF 429" and self.first_waf_block is None:
                self.first_waf_block = (self.sent, time.monotonic() - self.start)

    def snapshot(self):
        with self.lock:
            return self.sent, dict(self.codes), self.first_waf_block


def classify(status, body):
    if status != 429:
        return str(status)
    try:
        return "WAF 429" if json.loads(body) == WAF_BODY else "Django 429"
    except (ValueError, TypeError):
        return "429 (other)"


def send_one(url, method, headers, timeout):
    req = Request(url, method=method, headers=headers)
    try:
        with urlopen(req, timeout=timeout) as resp:
            resp.read()
            return classify(resp.status, b"")
    except HTTPError as e:
        try:
            body = e.read()
        except Exception:
            body = b""
        return classify(e.code, body)
    except (URLError, TimeoutError, OSError) as e:
        return f"error ({type(e).__name__})"


def build_headers(args):
    headers = {"User-Agent": "osh-waf-rate-limit-test/1.0 (OSDEV-2138)"}
    for h in args.header:
        name, sep, value = h.partition(":")
        if not sep:
            sys.exit(f"Bad --header value (expected 'Name: value'): {h}")
        headers[name.strip()] = value.strip()
    if args.token_env:
        token = os.environ.get(args.token_env)
        if not token:
            sys.exit(f"Env var {args.token_env} is empty or not set")
        headers["Authorization"] = f"Token {token}"
    return headers


def confirm(args):
    host = urlparse(args.url).hostname or ""
    if not urlparse(args.url).scheme.startswith("http") or not host:
        sys.exit(f"Not a valid http(s) URL: {args.url}")
    print(f"Target: {args.method} {args.url}")
    print(f"Requests: {args.count}, concurrency: {args.concurrency}, "
          f"rps limit: {args.rps or 'none'}")
    if host in PRODUCTION_HOSTS and not args.yes:
        sys.exit(f"{host} is a production environment. Re-run with --yes if you really mean it.")
    if not args.yes:
        if input("Continue? [y/N] ").strip().lower() != "y":
            sys.exit("Cancelled.")


def print_progress(stats, final=False):
    sent, codes, first = stats.snapshot()
    elapsed = time.monotonic() - stats.start
    rate = sent / elapsed if elapsed else 0
    codes_txt = ", ".join(f"{k}: {v}" for k, v in sorted(codes.items()))
    prefix = "DONE " if final else ""
    print(f"{prefix}[{elapsed:6.1f}s] sent {sent} ({rate:.1f}/s) | {codes_txt}", flush=True)


def main():
    args = parse_args()
    if args.count < 1 or args.concurrency < 1:
        sys.exit("--count and --concurrency must be >= 1")
    headers = build_headers(args)
    confirm(args)

    stats = Stats()
    stop_reporting = threading.Event()

    def reporter():
        while not stop_reporting.wait(args.report_every):
            print_progress(stats)

    threading.Thread(target=reporter, daemon=True).start()

    interval = 1.0 / args.rps if args.rps > 0 else 0
    next_send = time.monotonic()
    try:
        with ThreadPoolExecutor(max_workers=args.concurrency) as pool:
            # Keep at most `concurrency` requests queued so --rps is respected.
            sem = threading.Semaphore(args.concurrency)

            def task():
                try:
                    stats.record(send_one(args.url, args.method, headers, args.timeout))
                finally:
                    sem.release()

            for _ in range(args.count):
                if interval:
                    now = time.monotonic()
                    if next_send > now:
                        time.sleep(next_send - now)
                    next_send = max(next_send + interval, time.monotonic())
                sem.acquire()
                pool.submit(task)
    except KeyboardInterrupt:
        print("\nInterrupted, waiting for in-flight requests...")
    finally:
        stop_reporting.set()

    print_progress(stats, final=True)
    _, codes, first = stats.snapshot()
    if first:
        print(f"First WAF block: request #{first[0]}, {first[1]:.1f}s after start.")
    elif codes.get("Django 429"):
        print("No WAF blocks; Django throttled some requests (see 'Django 429').")
    else:
        print("No WAF blocks. If the rules are in Count mode this is expected: "
              "check the CloudWatch metrics and sampled requests.")


if __name__ == "__main__":
    main()
