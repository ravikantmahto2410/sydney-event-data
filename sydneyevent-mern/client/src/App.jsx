import { useState, useEffect } from 'react';
import axios from 'axios';
import { format, parse } from 'date-fns'; // Import parse from date-fns

function App() {
    const [events, setEvents] = useState([]);
    const [searchTerm, setSearchTerm] = useState('');
    const [venueFilter, setVenueFilter] = useState('');
    const [sortOrder, setSortOrder] = useState('asc');

    useEffect(() => {
        const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000'
        axios.get(`${API_URL}/api/events`)
            .then(response => {
                setEvents(response.data);
            })
            .catch(error => {
                console.error('Error fetching events:', error);
            });
    }, []);

    const filteredEvents = events
        .filter(event =>
            event.title?.toLowerCase().includes(searchTerm.toLowerCase()) &&
            event.venue?.toLowerCase().includes(venueFilter.toLowerCase())
        )
        .sort((a, b) => {
            const dateA = new Date(a.date);
            const dateB = new Date(b.date);
            return sortOrder === 'asc' ? dateA - dateB : dateB - dateA;
        });

    // Helper function to format date safely
    const formatDate = (dateString) => {
        try {
            // Parse the date string in "YYYY-MM-DD HH:mm:ss" format
            const parsedDate = parse(dateString, 'yyyy-MM-dd HH:mm:ss', new Date());
            // Check if the parsed date is valid
            if (isNaN(parsedDate.getTime())) {
                return 'Invalid Date';
            }
            // Format the date for display
            return format(parsedDate, 'PPP p'); // e.g., "May 15th, 2025 6:00 PM"
        } catch (error) {
            console.error('Error formatting date:', dateString, error);
            return 'Invalid Date';
        }
    };

    return (
        <div className="min-h-screen bg-gray-100 p-4">
            <h1 className="text-3xl font-bold text-center mb-6">Sydney Events</h1>

            {/* Filters */}
            <div className="flex flex-col sm:flex-row gap-4 mb-6">
                <input
                    type="text"
                    placeholder="Search by title..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="border p-2 rounded-lg"
                />
                <input
                    type="text"
                    placeholder="Filter by venue..."
                    value={venueFilter}
                    onChange={(e) => setVenueFilter(e.target.value)}
                    className="border p-2 rounded-lg"
                />
                <button
                    onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
                    className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600"
                >
                    Sort by Date ({sortOrder === 'asc' ? 'Ascending' : 'Descending'})
                </button>
                <button
                    onClick={() => {
                        setSearchTerm('');
                        setVenueFilter('');
                    }}
                    className="bg-gray-500 text-white px-4 py-2 rounded-lg hover:bg-gray-600"
                >
                    Clear Filters
                </button>
            </div>

            {/* Event Cards */}
            <div className="max-w-7xl mx-auto grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 px-4">
                {filteredEvents.length > 0 ? (
                    filteredEvents.map(event => (
                        <div key={event._id} className="bg-white p-4 rounded-lg shadow-lg fade-in-up">
                            <h2 className="text-xl font-semibold">{event.title || 'No Title'}</h2>
                            <p className="text-gray-600">Date: {formatDate(event.date)}</p>
                            <p className="text-gray-600">Venue: {event.venue || 'No Venue'}</p>
                            <p className="text-gray-600">{event.description || 'No Description'}</p>
                            <a
                                href={event.ticket_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-blue-500 hover:underline"
                            >
                                Get Tickets
                            </a>
                        </div>
                    ))
                ) : (
                    <p className="text-center text-gray-600">No events found.</p>
                )}
            </div>
        </div>
    );
}

export default App;