#!/usr/bin/env python3
"""
Lightweight dashboard server for LLM chat usage tracking.
Runs locally, fetches usage from claude.ai using your browser session.
"""

import http.server
import socketserver
import json
import urllib.request
import urllib.error
from pathlib import Path
from urllib.parse import urlparse, parse_qs


class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler for dashboard API endpoints."""

    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        # Serve dashboard
        if path == '/' or path == '/index.html':
            self.serve_dashboard()
        # API endpoint for Claude usage
        elif path == '/api/claude-usage':
            self.fetch_claude_usage()
        # Serve static files
        else:
            super().do_GET()

    def serve_dashboard(self):
        """Serve the dashboard HTML."""
        dashboard_path = Path(__file__).parent / 'index.html'

        try:
            with open(dashboard_path, 'r') as f:
                content = f.read()

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(content.encode())
        except Exception as e:
            self.send_error(500, f'Error loading dashboard: {e}')

    def fetch_claude_usage(self):
        """Fetch Claude chat usage from claude.ai."""
        # Get cookies from request
        cookie_header = self.headers.get('Cookie', '')

        if not cookie_header or 'sessionKey' not in cookie_header:
            self.send_json_response({
                'error': 'Not logged in to claude.ai. Please log in first.'
            }, 401)
            return

        try:
            # Fetch from Claude API
            headers = {
                'Cookie': cookie_header,
                'User-Agent': self.headers.get('User-Agent', 'Mozilla/5.0')
            }

            # Try to get organizations first
            org_req = urllib.request.Request(
                'https://claude.ai/api/organizations',
                headers=headers
            )

            with urllib.request.urlopen(org_req, timeout=10) as response:
                orgs = json.loads(response.read().decode('utf-8'))

                if not orgs or len(orgs) == 0:
                    self.send_json_response({'error': 'No organizations found'}, 404)
                    return

                org_id = orgs[0].get('uuid')

                if not org_id:
                    self.send_json_response({'error': 'Invalid organization data'}, 500)
                    return

            # Now fetch usage for this org
            usage_url = f'https://claude.ai/api/organizations/{org_id}/subscription'
            usage_req = urllib.request.Request(usage_url, headers=headers)

            with urllib.request.urlopen(usage_req, timeout=10) as response:
                subscription = json.loads(response.read().decode('utf-8'))

                # Parse usage data
                usage_data = self.parse_claude_subscription(subscription)
                self.send_json_response(usage_data)

        except urllib.error.HTTPError as e:
            if e.code == 401:
                self.send_json_response({
                    'error': 'Session expired. Please log in to claude.ai again.'
                }, 401)
            else:
                self.send_json_response({
                    'error': f'HTTP error {e.code}'
                }, e.code)
        except Exception as e:
            print(f'Error fetching Claude usage: {e}')
            self.send_json_response({
                'error': f'Failed to fetch usage: {str(e)}'
            }, 500)

    def parse_claude_subscription(self, subscription):
        """Parse Claude subscription data to extract usage."""
        # The API response structure may vary, this attempts to extract
        # the relevant usage information

        usage = {}

        # Try to find usage info
        if 'usage' in subscription:
            usage_info = subscription['usage']
        elif 'credit' in subscription:
            usage_info = subscription['credit']
        else:
            usage_info = subscription

        # Extract plan type
        plan = subscription.get('plan', {})
        usage['planType'] = plan.get('name', 'unknown').lower()

        # For now, return raw data for inspection
        # TODO: Parse actual message limits from API response
        usage['raw'] = subscription

        # Default placeholder values (will be replaced when we know the API structure)
        usage['used'] = 0
        usage['limit'] = 45  # Default free tier
        usage['remaining'] = 45
        usage['percentage'] = 0
        usage['resetTime'] = 'Unknown'

        return usage

    def send_json_response(self, data, status=200):
        """Send JSON response."""
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def log_message(self, format, *args):
        """Custom log format."""
        print(f"[{self.log_date_time_string()}] {format % args}")


def main():
    """Start the dashboard server."""
    PORT = 8000

    # Change to dashboard directory
    dashboard_dir = Path(__file__).parent
    import os
    os.chdir(dashboard_dir)

    print("\n" + "=" * 60)
    print("  🤖 LLM Chat Usage Dashboard")
    print("=" * 60)
    print(f"\n✅ Dashboard running at: http://localhost:{PORT}")
    print(f"\n📋 Instructions:")
    print(f"   1. Make sure you're logged into claude.ai in your browser")
    print(f"   2. Open http://localhost:{PORT} in your browser")
    print(f"   3. Click 'Refresh Usage' to fetch your Claude chat usage")
    print(f"\n💡 Tip: Bookmark the dashboard for quick access!")
    print(f"\n⚠️  Note: This tracks CHAT usage (conversations),")
    print(f"          NOT API usage (developer API calls)")
    print(f"\nPress Ctrl+C to stop the server\n")
    print("=" * 60 + "\n")

    try:
        with socketserver.TCPServer(("", PORT), DashboardHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 Dashboard stopped")
        return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
