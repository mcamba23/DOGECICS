/**
 * K6 Stress Test for DOGECICS
 * Tests system behavior under extreme load
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');

// Stress test configuration
export const options = {
  stages: [
    { duration: '1m', target: 50 },   // Ramp up to 50 users
    { duration: '2m', target: 100 },  // Ramp up to 100 users
    { duration: '3m', target: 100 },  // Stay at 100 users
    { duration: '2m', target: 150 },  // Push to 150 users
    { duration: '3m', target: 150 },  // Stay at 150 users
    { duration: '2m', target: 0 },    // Ramp down to 0
  ],
  thresholds: {
    http_req_duration: ['p(95)<1000'], // 95% of requests should be below 1s
    http_req_failed: ['rate<0.2'],     // Error rate should be less than 20% (stress allows more errors)
    errors: ['rate<0.2'],
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:22555';

export default function () {
  // Multiple rapid requests to stress the system
  const requests = [
    {
      method: 'POST',
      url: BASE_URL,
      body: JSON.stringify({
        method: 'getbalance',
        params: [],
        jsonrpc: '1.0',
      }),
      params: {
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Basic ' + encoding.b64encode('testuser:testpass'),
        },
        tags: { name: 'StressGetBalance' },
      },
    },
    {
      method: 'POST',
      url: BASE_URL,
      body: JSON.stringify({
        method: 'getunconfirmedbalance',
        params: [],
        jsonrpc: '1.0',
      }),
      params: {
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Basic ' + encoding.b64encode('testuser:testpass'),
        },
        tags: { name: 'StressGetUnconfirmed' },
      },
    },
    {
      method: 'POST',
      url: BASE_URL,
      body: JSON.stringify({
        method: 'listtransactions',
        params: [],
        jsonrpc: '1.0',
      }),
      params: {
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Basic ' + encoding.b64encode('testuser:testpass'),
        },
        tags: { name: 'StressListTransactions' },
      },
    },
  ];

  // Send batch requests
  const responses = http.batch(requests);

  // Check all responses
  responses.forEach((response, index) => {
    const checkResult = check(response, {
      'status is 200': (r) => r.status === 200,
      'has result': (r) => r.json('result') !== undefined,
    });
    errorRate.add(!checkResult);
  });

  sleep(0.5); // Shorter sleep for stress test
}

export function handleSummary(data) {
  return {
    'tests/reports/stress-test-summary.json': JSON.stringify(data),
    stdout: textSummary(data, { indent: ' ', enableColors: true }),
  };
}
