/**
 * K6 Soak Test for DOGECICS
 * Tests system stability under sustained load over extended period
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');

// Soak test configuration - runs for extended period
export const options = {
  stages: [
    { duration: '2m', target: 30 },   // Ramp up to 30 users
    { duration: '20m', target: 30 },  // Stay at 30 users for 20 minutes
    { duration: '2m', target: 0 },    // Ramp down to 0
  ],
  thresholds: {
    http_req_duration: ['p(95)<800'],  // 95% of requests should be below 800ms
    http_req_failed: ['rate<0.05'],    // Error rate should be less than 5%
    errors: ['rate<0.05'],
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:22555';

export default function () {
  // Simulate realistic user behavior over long period
  
  // Check balance
  let balanceResponse = http.post(
    BASE_URL,
    JSON.stringify({
      method: 'getbalance',
      params: [],
      jsonrpc: '1.0',
      id: `soak-${__VU}-${__ITER}`,
    }),
    {
      headers: {
        'Content-Type': 'application/json',
        Authorization: 'Basic ' + encoding.b64encode('testuser:testpass'),
      },
      tags: { name: 'SoakGetBalance' },
    }
  );

  const balanceCheck = check(balanceResponse, {
    'balance status is 200': (r) => r.status === 200,
    'balance has result': (r) => r.json('result') !== undefined,
  });
  errorRate.add(!balanceCheck);

  sleep(2); // Realistic pause

  // Check pending balance
  let pendingResponse = http.post(
    BASE_URL,
    JSON.stringify({
      method: 'getunconfirmedbalance',
      params: [],
      jsonrpc: '1.0',
      id: `soak-${__VU}-${__ITER}`,
    }),
    {
      headers: {
        'Content-Type': 'application/json',
        Authorization: 'Basic ' + encoding.b64encode('testuser:testpass'),
      },
      tags: { name: 'SoakGetPending' },
    }
  );

  const pendingCheck = check(pendingResponse, {
    'pending status is 200': (r) => r.status === 200,
    'pending has result': (r) => r.json('result') !== undefined,
  });
  errorRate.add(!pendingCheck);

  sleep(3); // Realistic pause

  // List transactions
  let transactionsResponse = http.post(
    BASE_URL,
    JSON.stringify({
      method: 'listtransactions',
      params: [],
      jsonrpc: '1.0',
      id: `soak-${__VU}-${__ITER}`,
    }),
    {
      headers: {
        'Content-Type': 'application/json',
        Authorization: 'Basic ' + encoding.b64encode('testuser:testpass'),
      },
      tags: { name: 'SoakListTransactions' },
    }
  );

  const txCheck = check(transactionsResponse, {
    'transactions status is 200': (r) => r.status === 200,
    'transactions has result': (r) => r.json('result') !== undefined,
    'response time acceptable': (r) => r.timings.duration < 1000,
  });
  errorRate.add(!txCheck);

  sleep(5); // Longer realistic pause between cycles
}

export function handleSummary(data) {
  return {
    'tests/reports/soak-test-summary.json': JSON.stringify(data),
    stdout: textSummary(data, { indent: ' ', enableColors: true }),
  };
}
