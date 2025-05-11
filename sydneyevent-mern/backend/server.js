import express from 'express';
import mongoose from 'mongoose';
import cors from 'cors';
import dotenv from 'dotenv';

// Load environment variables from .env
dotenv.config();
console.log('MONGO_URI in server.js:', process.env.MONGO_URI)

const app = express();

// Middleware
app.use(cors());
app.use(express.json());

// Connect to MongoDB
mongoose.connect(process.env.MONGO_URI)
    .then(() => {
        console.log('Connected to MongoDB')
        console.log('Database Name:', mongoose.connection.db.databaseName);
    })
    .catch(err => console.error('MongoDB connection error:', err));

// Define Event Schema
const eventSchema = new mongoose.Schema({
    title: String,
    date: String,
    venue: String,
    description: String,
    ticket_url: String,
});

const Event = mongoose.model('Event', eventSchema, 'events');

// Health Check Route
app.get('/', (req, res) => {
    res.json({ message: 'Sydney Events API is running' });
});

// API Route to Get Events
app.get('/api/events', async (req, res) => {
    try {
        const events = await Event.find().sort({ date: 1 }); // Sort by date
        res.json(events);
    } catch (err) {
        res.status(500).json({ message: err.message });
    }
});

// Global Error Handling Middleware
app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).json({ message: 'Something went wrong!' });
});

// Start the Server
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));