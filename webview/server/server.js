const express = require('express');
const cors = require('cors');

const app = express();
const port = process.env.PORT || 3000;

// Enable CORS for all routes
app.use(cors());

const fs = require('fs');

const data = fs.readFileSync('207296_model.json');
const testData = JSON.parse(data);

// Route to get test data
app.get('/api/testdata', (req, res) => {
  res.json(testData);
});

app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});
