import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import apiClient from '../api'; 

const Dashboard = ({ token }) => {
    const [stories, setStories] = useState([]);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchStories = async () => {
            try {
                
                const response = await apiClient.get('/stories');
                setStories(response.data);
            } catch (error) {
                console.error("Failed to fetch stories:", error);
                
            } finally {
                setLoading(false);
            }
        };
        fetchStories();
    }, [token]);

    if (loading) {
        return <div className="loading-spinner">Loading your stories...</div>;
    }

    return (
        <div className="dashboard">
            <h1>Your Story Dashboard</h1>
            <Link to="/chat" className="new-story-btn">
                + Start a New Story
            </Link>
            <h2>Previous Stories - Indian Theme</h2>
            {stories.length === 0 ? (
                <p>You haven't created any stories yet.</p>
            ) : (
                <div className="story-list">
                    {stories.map(story => (
                        <div key={story.id} className="story-card" onClick={() => navigate(`/story/${story.id}`)}>
                            <h3>{story.title || 'Untitled Story'}</h3>
                            <p>Created on: {new Date(story.created_at).toLocaleDateString()}</p>
                            <p className="status">Status: {story.status}</p>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default Dashboard;