#!/usr/bin/env python3
import http.server
import json
import logging
import os
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger("portfolio")

PORT = 8091
VERSION = "1.5"
DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(DIR), 'data')

MARKET_SUFFIX = {"US": "", "JP": ".T", "HK": ".HK", "UK": ".L", "EU": ".DE", "CA": ".TO", "AU": ".AX", "CN": ".SS"}
MARKET_CURRENCY = {"US": "USD", "JP": "JPY", "HK": "HKD", "UK": "GBP", "EU": "EUR", "CA": "CAD", "AU": "AUD", "CN": "CNY"}


def _fetch_quote(symbol):
    url = f'https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=1d'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        meta = data.get('chart', {}).get('result', [{}])[0].get('meta', {})
        return {
            'price': meta.get('regularMarketPrice'),
            'previousClose': meta.get('chartPreviousClose') or meta.get('previousClose'),
        }
    except Exception as e:
        logger.warning("quote fetch failed for %s: %s", symbol, e)
        return {}


def _fetch_rates():
    url = 'https://open.er-api.com/v6/latest/USD'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        if data.get('result') == 'success':
            return data.get('rates', {})
        logger.warning("fx rates response not success: %s", data.get('result'))
    except Exception as e:
        logger.warning("fx rates fetch failed: %s", e)
    return {}


def build_portfolio():
    portfolio_file = os.path.join(DATA_DIR, 'my-portfolio.json')
    if not os.path.exists(portfolio_file):
        return {"positions": [], "totalValue": 0, "totalCost": 0, "totalPL": 0, "todayPL": 0}

    with open(portfolio_file) as f:
        data = json.load(f)

    positions = data.get('positions', [])
    if not positions:
        return {"positions": [], "totalValue": 0, "totalCost": 0, "totalPL": 0, "todayPL": 0}

    symbols = []
    for p in positions:
        suffix = MARKET_SUFFIX.get(p.get('market', 'US'), '')
        symbols.append(p.get('ticker', '') + suffix)

    with ThreadPoolExecutor(max_workers=8) as pool:
        rates_future = pool.submit(_fetch_rates)
        quotes = list(pool.map(_fetch_quote, symbols))
        rates = rates_future.result()

    total_value = 0
    total_cost = 0
    today_pl = 0

    for p, quote in zip(positions, quotes):
        currency = MARKET_CURRENCY.get(p.get('market', 'US'), 'USD')
        fx = rates.get(currency, 1) if currency != 'USD' else 1
        p['currency'] = currency
        p['fxRate'] = fx

        price = quote.get('price')
        prev_close = quote.get('previousClose')
        if price:
            qty = p.get('qty', 0)
            cost_basis = p.get('costBasis', 0)
            p['price'] = price
            p['previousClose'] = prev_close
            p['marketValue'] = round(price * qty / fx, 2)
            p['costTotal'] = round(cost_basis * qty / fx, 2)
            p['gainLoss'] = round((price - cost_basis) * qty / fx, 2)
            p['gainLossPct'] = round(((price - cost_basis) / cost_basis) * 100, 1) if cost_basis else 0
            if prev_close:
                p['dayChange'] = round(price - prev_close, 2)
                p['dayChangePct'] = round(((price - prev_close) / prev_close) * 100, 2)
                p['dayPL'] = round((price - prev_close) * qty / fx, 2)
                today_pl += p['dayPL']
            total_value += p['marketValue']
            total_cost += p['costTotal']

    cash_balances = data.get('cashBalances', {})
    cash_usd = 0
    for cur, amt in cash_balances.items():
        if cur == 'USD':
            cash_usd += amt
        else:
            fx = rates.get(cur, 1)
            cash_usd += amt / fx if fx else 0
    total_value += cash_usd
    # Cash is part of both cost basis and market value so the two stay
    # consistent; totalPL below then reflects stock gains only (cash cancels).
    total_cost += cash_usd

    return {
        "positions": positions,
        "cashBalances": cash_balances,
        "totalValue": round(total_value, 2),
        "totalCost": round(total_cost, 2),
        "totalPL": round(total_value - total_cost, 2),
        "todayPL": round(today_pl, 2),
    }


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIR, **kwargs)

    def do_GET(self):
        if self.path == '/api/health':
            self.send_json({'status': 'ok', 'version': VERSION, 'port': PORT})
        elif self.path == '/api/positions':
            self.handle_positions()
        elif self.path.startswith('/api/portfolio'):
            self.handle_portfolio()
        elif self.path.startswith('/api/quote/'):
            self.handle_quote()
        elif self.path.startswith('/api/rates'):
            self.handle_rates()
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == '/api/portfolio/sync':
            self.handle_sync()
        else:
            self.send_json({'error': 'not found'}, 404)

    def handle_positions(self):
        try:
            portfolio_file = os.path.join(DATA_DIR, 'my-portfolio.json')
            if os.path.exists(portfolio_file):
                with open(portfolio_file) as f:
                    data = json.load(f)
                self.send_json(data)
            else:
                self.send_json({"positions": [], "cashBalance": 0})
        except Exception as e:
            self.send_json({'error': str(e)}, 500)

    def handle_sync(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length)) if length else {}
            positions = body.get('positions', [])
            cash = body.get('cashBalances', {})
            portfolio_file = os.path.join(DATA_DIR, 'my-portfolio.json')
            data = {"positions": positions, "cashBalance": 0}
            if cash:
                data["cashBalances"] = cash
            with open(portfolio_file, 'w') as f:
                json.dump(data, f, indent=2)
                f.write('\n')
            self.send_json({'success': True, 'positions': len(positions)})
        except Exception as e:
            self.send_json({'error': str(e)}, 500)

    def handle_portfolio(self):
        try:
            self.send_json(build_portfolio())
        except Exception as e:
            self.send_json({'error': str(e)}, 500)

    def handle_quote(self):
        symbol = self.path.split('/api/quote/')[-1]
        result = _fetch_quote(symbol)
        if result:
            result['symbol'] = symbol
            self.send_json(result)
        else:
            self.send_json({'error': 'quote failed'}, 500)

    def handle_rates(self):
        url = 'https://open.er-api.com/v6/latest/USD'
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())
            self.send_json(data)
        except Exception as e:
            self.send_json({'error': str(e)}, 500)

    def send_json(self, obj, code=200):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(body))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        msg = str(args[0]) if args else ''
        if '/api/' in msg and '/api/health' not in msg:
            super().log_message(format, *args)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    print(f'Portfolio server running on http://localhost:{PORT}')
    # localhost-only (2026-07-05 network-posture decision): no auth on any
    # endpoint, so the module must not be reachable from the LAN.
    server = http.server.HTTPServer(('127.0.0.1', PORT), Handler)
    server.serve_forever()
