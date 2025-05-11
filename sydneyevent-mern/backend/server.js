import express from 'express';
import mongoose from 'mongoose';
import cors from 'cors';
import dotenv from 'dotenv';

// Load environment variables from .env
dotenv.config();
console.log('MONGO_URI in server.js:', process.env.MONGO_URI);

const app = express();

// Middleware
const allowedOrigins = [
    'http://localhost:5173', // Frontend local URL (Vite default port)
    'https://sydney-event-data-frontend.onrender.com', // Frontend production URL
];
app.use(cors({
    origin: (origin, callback) => {
        if (!origin || allowedOrigins.includes(origin)) {
            callback(null, true);
        } else {
            callback(new Error('Not allowed by CORS'));
        }
    },
}));
app.use(express.json());

// Connect to MongoDB
mongoose.connect(process.env.MONGO_URI)
    .then(() => {
        console.log('Connected to MongoDB');
        console.log('Database Name:', mongoose.connection.db.databaseName);
    })
    .catch(err => {
        console.error('MongoDB connection error:', err);
        process.exit(1); // Exit if MongoDB connection fails
    });

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
        const events = await Event.find().sort({ date: 1 });
        console.log(`Returning ${events.length} events`); // Debug log
        res.json(events);
    } catch (err) {
        console.error('Error fetching events:', err);
        res.status(500).json({ message: 'Error fetching events', error: err.message });
    }
});

// Global Error Handling Middleware
app.use((err, req, res, next) => {
    console.error('Global error:', err.stack);
    res.status(500).json({ message: 'Something went wrong!', error: err.message });
});

// Start the Server
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));