/**
 * K6 Spike Test for DOGECICS
 * Tests system behavior under sudden traffic spikes
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');

// Spike test configuration
export const options = {
  stages: [
    { duration: '30s', target: 10 },   // Normal load
    { duration: '10s', target: 200 },  // Sudden spike!
    { duration: '1m', target: 200 },   // Maintain spike
    { duration: '10s', target: 10 },   // Quick drop
    { duration: '30s', target: 10 },   // Normal load
    { duration: '10s', target: 300 },  // Even bigger spike!
    { duration: '1m', target: 300 },   // Maintain bigger spike
    { duration: '20s', target: 0 },    // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<2000'], // 95% of requests should be below 2s (spike allows higher)
    http_req_failed: ['rate<0.3'],     // Error rate should be less than 30% during spike
    errors: ['rate<0.3'],
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:22555';

export default function () {
  // Simulate various operations during spike
  const operation = Math.floor(Math.random() * 3);

  let response;
  switch (operation) {
    case 0:
      response = http.post(
        BASE_URL,
        JSON.stringify({
          method: 'getbalance',
          params: [],
          jsonrpc: '1.0',
        }),
        {
          headers: {
            'Content-Type': 'application/json',
            Authorization: 'Basic ' + encoding.b64encode('testuser:testpass'),
          },
          tags: { name: 'SpikeGetBalance' },
        }
      );
      break;
    case 1:
      response = http.post(
        BASE_URL,
        JSON.stringify({
          method: 'listtransactions',
          params: [],
          jsonrpc: '1.0',
        }),
        {
          headers: {
            'Content-Type': 'application/json',
            Authorization: 'Basic ' + encoding.b64encode('testuser:testpass'),
          },
          tags: { name: 'SpikeListTransactions' },
        }
      );
      break;
    case 2:
      response = http.post(
        BASE_URL,
        JSON.stringify({
          method: 'getunconfirmedbalance',
          params: [],
          jsonrpc: '1.0',
        }),
        {
          headers: {
            'Content-Type': 'application/json',
            Authorization: 'Basic ' + encoding.b64encode('testuser:testpass'),
          },
          tags: { name: 'SpikeGetUnconfirmed' },
        }
      );
      break;
  }

  const checkResult = check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 5s': (r) => r.timings.duration < 5000,
  });
  errorRate.add(!checkResult);

  sleep(0.3); // Very short sleep for spike simulation
}

export function handleSummary(data) {
  return {
    'tests/reports/spike-test-summary.json': JSON.stringify(data),
    stdout: textSummary(data, { indent: ' ', enableColors: true }),
  };
}
