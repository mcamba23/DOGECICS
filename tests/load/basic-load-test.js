/**
 * K6 Basic Load Test for DOGECICS
 * Tests basic load handling for the system
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');

// Test configuration
export const options = {
  stages: [
    { duration: '30s', target: 10 },  // Ramp up to 10 users
    { duration: '1m', target: 10 },   // Stay at 10 users
    { duration: '30s', target: 20 },  // Ramp up to 20 users
    { duration: '1m', target: 20 },   // Stay at 20 users
    { duration: '30s', target: 0 },   // Ramp down to 0 users
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% of requests should be below 500ms
    http_req_failed: ['rate<0.1'],    // Error rate should be less than 10%
    errors: ['rate<0.1'],             // Custom error rate should be less than 10%
  },
};

// Base URL - modify as needed
const BASE_URL = __ENV.BASE_URL || 'http://localhost:22555';

export default function () {
  // Simulate wallet balance check
  let balanceResponse = http.post(
    BASE_URL,
    JSON.stringify({
      method: 'getbalance',
      params: [],
      jsonrpc: '1.0',
      id: 'k6-test',
    }),
    {
      headers: {
        'Content-Type': 'application/json',
        Authorization: 'Basic ' + encoding.b64encode('testuser:testpass'),
      },
      tags: { name: 'GetBalance' },
    }
  );

  // Check response
  const balanceCheck = check(balanceResponse, {
    'balance status is 200': (r) => r.status === 200,
    'balance response has result': (r) => r.json('result') !== undefined,
  });
  errorRate.add(!balanceCheck);

  sleep(1);

  // Simulate transaction list request
  let transactionsResponse = http.post(
    BASE_URL,
    JSON.stringify({
      method: 'listtransactions',
      params: [],
      jsonrpc: '1.0',
      id: 'k6-test',
    }),
    {
      headers: {
        'Content-Type': 'application/json',
        Authorization: 'Basic ' + encoding.b64encode('testuser:testpass'),
      },
      tags: { name: 'ListTransactions' },
    }
  );

  // Check response
  const txCheck = check(transactionsResponse, {
    'transactions status is 200': (r) => r.status === 200,
    'transactions response has result': (r) => r.json('result') !== undefined,
  });
  errorRate.add(!txCheck);

  sleep(1);
}

export function handleSummary(data) {
  return {
    'tests/reports/load-test-basic-summary.json': JSON.stringify(data),
    stdout: textSummary(data, { indent: ' ', enableColors: true }),
  };
}
