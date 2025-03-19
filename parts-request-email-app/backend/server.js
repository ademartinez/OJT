const express = require('express');
const fs = require('fs');
const path = require('path');
const cors = require('cors'); // Import the cors package
const app = express();

app.use(cors()); // Use the cors middleware
app.use(express.json());

// Path to the text file
const filePath = path.join(__dirname, 'engineers.txt');

// Endpoint to get the list of engineers
app.get('/api/engineers', (req, res) => {
  fs.readFile(filePath, 'utf8', (err, data) => {
    if (err) {
      console.error(err);
      return res.status(500).json({ message: 'Failed to read engineers list.' });
    }
    const engineers = data.split('\n').filter((line) => line.trim() !== '');
    res.json(engineers);
  });
});

// Endpoint to update the list of engineers
app.post('/api/engineers', (req, res) => {
  const { engineers } = req.body;
  if (!Array.isArray(engineers)) {
    return res.status(400).json({ message: 'Invalid data format.' });
  }
  fs.writeFile(filePath, engineers.join('\n'), (err) => {
    if (err) {
      console.error(err);
      return res.status(500).json({ message: 'Failed to update engineers list.' });
    }
    res.json({ message: 'Engineers list updated successfully.' });
  });
});

// Start the server
const PORT = 5000;
app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});