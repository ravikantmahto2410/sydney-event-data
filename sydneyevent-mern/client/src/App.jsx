import { useState, useEffect } from 'react';
import axios from 'axios';
import { format, parse } from 'date-fns';

function App() {
    const [events, setEvents] = useState([]);
    const [searchTerm, setSearchTerm] = useState('');
    const [venueFilter, setVenueFilter] = useState('');
    const [sortOrder, setSortOrder] = useState('asc');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchEvents = async () => {
        setLoading(true);
        setError(null);
        const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';
        console.log('Fetching events from:', `${API_URL}/api/events`);
        try {
            const response = await axios.get(`${API_URL}/api/events`, {
                timeout: 10000, // Timeout after 10 seconds
            });
            console.log('Fetched events:', response.data);
            setEvents(response.data || []); // Ensure events is always an array
            setLoading(false);
        } catch (error) {
            console.error('Error fetching events:', error);
            setError(`Failed to fetch events: ${error.message}`);
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchEvents();
    }, []);

    const filteredEvents = events
        .filter(event => {
            const title = event.title || '';
            const venue = event.venue || '';
            const matchesTitle = title.toLowerCase().includes(searchTerm.toLowerCase());
            const matchesVenue = venue.toLowerCase().includes(venueFilter.toLowerCase());
            console.log(`Event: ${title}, Matches Title: ${matchesTitle}, Matches Venue: ${matchesVenue}`);
            return matchesTitle && matchesVenue;
        })
        .sort((a, b) => {
            const dateA = new Date(a.date);
            const dateB = new Date(b.date);
            return sortOrder === 'asc' ? dateA - dateB : dateB - dateA;
        });

    console.log('Events state:', events);
    console.log('Filtered events:', filteredEvents);

    const formatDate = (dateString) => {
        try {
            const parsedDate = parse(dateString, 'yyyy-MM-dd HH:mm:ss', new Date());
            if (isNaN(parsedDate.getTime())) {
                return 'Invalid Date';
            }
            return format(parsedDate, 'PPP p');
        } catch (error) {
            console.error('Error formatting date:', dateString, error);
            return 'Invalid Date';
        }
    };

    return (
        <div className="min-h-screen bg-gray-100 p-4">
            <h1 className="text-3xl font-bold text-center mb-6">Sydney Events</h1>

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

            {error ? (
                <div className="text-center">
                    <p className="text-red-600">{error}</p>
                    <button
                        onClick={fetchEvents}
                        className="mt-2 bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600"
                    >
                        Retry
                    </button>
                </div>
            ) : loading ? (
                <div className="flex justify-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-t-4 border-blue-500"></div>
                </div>
            ) : filteredEvents.length > 0 ? (
                <div className="max-w-7xl mx-auto grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 px-4">
                    {filteredEvents.map(event => (
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
                    ))}
                </div>
            ) : (
                <p className="text-center text-gray-600">No events found.</p>
            )}
        </div>
    );
}

export default App;