import { useState, useEffect } from 'react';
import axios from 'axios';
import { format } from 'date-fns';

function App() {
    const [events, setEvents] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [venueFilter, setVenueFilter] = useState('');
    const [sortOrder, setSortOrder] = useState('asc');

    useEffect(() => {
        // Fetch events from the backend API
        setLoading(true);
        axios.get('http://localhost:5000/api/events')
            .then(response => {
                setEvents(response.data);
                setLoading(false);
            })
            .catch(error => {
                console.error('Error fetching events:', error);
                setLoading(false);
            });
    }, []);

    // Filter events based on search term and venue
    const filteredEvents = events.filter(event =>
        event.title.toLowerCase().includes(searchTerm.toLowerCase()) &&
        (venueFilter ? event.venue?.toLowerCase().includes(venueFilter.toLowerCase()) : true)
    );

    // Sort events by date
    const sortedEvents = [...filteredEvents].sort((a, b) => {
        const dateA = new Date(a.date);
        const dateB = new Date(b.date);
        return sortOrder === 'asc' ? dateA - dateB : dateB - dateA;
    });

    return (
        <div className="min-h-screen bg-gray-100 py-8 flex flex-col">
            <div className="flex-grow">
                <h1 className="text-4xl font-bold text-center text-gray-800 mb-8">Sydney Events</h1>

                {/* Filters and Sort */}
                <div className="max-w-3xl mx-auto mb-6 flex flex-col sm:flex-row gap-4 justify-center">
                    <input
                        type="text"
                        placeholder="Search events by title..."
                        value={searchTerm}
                        onChange={e => setSearchTerm(e.target.value)}
                        className="w-full sm:w-80 p-3 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <input
                        type="text"
                        placeholder="Filter by venue..."
                        value={venueFilter}
                        onChange={e => setVenueFilter(e.target.value)}
                        className="w-full sm:w-80 p-3 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <button
                        onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
                        className="bg-gray-500 text-white px-4 py-2 rounded-lg hover:bg-gray-600 transition-colors"
                    >
                        Sort by Date ({sortOrder === 'asc' ? 'Ascending' : 'Descending'})
                    </button>
                    <button
                        onClick={() => {
                            setSearchTerm('');
                            setVenueFilter('');
                        }}
                        className="bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600 transition-colors"
                    >
                        Clear Filters
                    </button>
                </div>

                {/* Event List */}
                {loading ? (
                    <div className="flex justify-center">
                        <div className="animate-spin rounded-full h-12 w-12 border-t-4 border-blue-500"></div>
                    </div>
                ) : (
                    <div className="max-w-7xl mx-auto grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 px-4">
                        {sortedEvents.length > 0 ? (
                            sortedEvents.map(event => (
                                <div
                                    key={event._id}
                                    className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg hover:scale-105 transition-all duration-300 fade-in-up"
                                >
                                    <h3 className="text-xl font-semibold text-blue-600 mb-3 line-clamp-2">{event.title}</h3>
                                    <p className="text-gray-700 mb-2">
                                        <strong>Date:</strong> {format(new Date(event.date), 'PPPp')}
                                    </p>
                                    <p className="text-gray-700 mb-2">
                                        <strong>Venue:</strong> {event.venue || 'Not specified'}
                                    </p>
                                    <p className="text-gray-700 mb-4 line-clamp-3">
                                        <strong>Description:</strong> {event.description || 'No description available'}
                                    </p>
                                    <a
                                        href={event.ticket_url}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="inline-block bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 transition-colors"
                                    >
                                        Get Tickets
                                    </a>
                                </div>
                            ))
                        ) : (
                            <p className="text-center text-gray-600 col-span-full">No events found.</p>
                        )}
                    </div>
                )}
            </div>

            {/* Footer */}
            <footer className="mt-12 py-4 bg-gray-800 text-white text-center">
                <p>© 2025 Sydney Events. Built with ❤️ by Ravikant.</p>
            </footer>
        </div>
    );
}

export default App;