// Helper script to import the EasyPay collection into Postman
// Run: node import_collection.js
// Requires: POSTMAN_API_KEY environment variable set

const fs = require('fs');
const https = require('https');

const apiKey = process.env.POSTMAN_API_KEY;
const collection = JSON.parse(fs.readFileSync('easypay_postman_collection.json', 'utf8'));

const data = JSON.stringify({ collection });

const options = {
  hostname: 'api.getpostman.com',
  path: '/collections',
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-Api-Key': apiKey,
    'Content-Length': Buffer.byteLength(data)
  }
};

const req = https.request(options, (res) => {
  let body = '';
  res.on('data', chunk => body += chunk);
  res.on('end', () => console.log(JSON.parse(body)));
});

req.on('error', console.error);
req.write(data);
req.end();
