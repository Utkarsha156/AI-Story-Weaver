import React, { useState, useEffect, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import apiClient from '../../api';
import "./storyviewer.css";

const StoryViewer = ({ token }) => {
    const { storyId } = useParams();
    const [story, setStory] = useState(null);
    const [pages, setPages] = useState([]);
    const [currentPageIndex, setCurrentPageIndex] = useState(0);
    const [status, setStatus] = useState('loading');
    const [error, setError] = useState('');
    const eventSourceRef = useRef(null); // Use a ref to hold the event source

    useEffect(() => {
        
        // This ensures the generation process is only ever started once.
        let isMounted = true; // Flag to check if component is still mounted

        const startEventSource = () => {
            if (eventSourceRef.current) {
                return; // Don't start a new one if it already exists
            }
            const newEventSource = new EventSource(`http://localhost:5000/api/story/${storyId}/generate?jwt=${token}`);
            eventSourceRef.current = newEventSource;
            setStatus('generating');

            newEventSource.onmessage = (event) => {
                if (!isMounted) return;
                const data = JSON.parse(event.data);
                if (data.error) {
                    setError(data.error);
                    setStatus('error');
                    newEventSource.close();
                } else if (data.status === 'completed') {
                    setStatus('completed');
                    newEventSource.close();
                } else if (data.page_no) {
                    setPages(prevPages => [...prevPages, data]);
                }
            };

            newEventSource.onerror = () => {
                if (!isMounted) return;
                setError('A connection error occurred during story generation.');
                setStatus('error');
                newEventSource.close();
            };
        };

        const fetchStoryDetails = async () => {
            try {
                const response = await apiClient.get(`/story/${storyId}`);
                if (!isMounted) return;
                const storyData = response.data;
                setStory(storyData);
                setPages(storyData.pages || []);
                setStatus(storyData.status);

                if (storyData.status === 'generating') {
                    startEventSource();
                }
            } catch (err) {
                if (isMounted && err.response?.status !== 401) {
                    setError('Could not load the story.');
                    setStatus('error');
                }
            }
        };

        fetchStoryDetails();

        
        return () => {
            isMounted = false;
            if (eventSourceRef.current) {
                eventSourceRef.current.close();
            }
        };
        
    }, [storyId, token]);

    const handleDownloadPdf = async () => {
        try {
            const response = await apiClient.get(`/story/${storyId}/pdf`, { responseType: 'blob' });
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `story_${storyId}.pdf`);
            document.body.appendChild(link);
            link.click();
            link.parentNode.removeChild(link);
        } catch (err) {
            setError("Could not download the PDF. Please try again later.");
        }
    };
    
    if (status === 'loading') return <div className="loading-spinner">Loading Story...</div>;
    if (status === 'generating' && pages.length === 0) return <div className="generating-notice">Hold tight! We're crafting your story... ✨</div>;
    if (error) return <div className="error-message">{error} <Link to="/">Go Home</Link></div>;
    if (!story || pages.length === 0) return <div className="loading-spinner">Oops! You didn't complete all the required inputs.. <Link to="/chat">Start a new story?</Link></div>;

    const currentPage = pages[currentPageIndex];

    const ImageDisplay = ({ imageUrl, pageNum }) => {
        if (imageUrl) {
            return <img src={`http://localhost:5000${imageUrl}`} alt={`Illustration for page ${pageNum}`} className="story-viewer-image" />;
        }
        return (
            <div className="story-viewer-image-placeholder">
                <p>Image could not be generated for this page.</p>
                <p>(This may be due to API rate limits or exhausted credits)</p>
            </div>
        );
    };

    return (
        <div className="story-viewer-container">
            <h2>{story.title}</h2>
            <p className="story-intro-text">Here is the 10-page illustrated story generated from your ideas:</p>
            
            <div className="story-viewer-page">
                <ImageDisplay imageUrl={currentPage.image_url} pageNum={currentPage.page_no} />
                <p className="story-viewer-text">{currentPage.text}</p>
            </div>
            
            <div className="story-viewer-nav">
                <button onClick={() => setCurrentPageIndex(p => p - 1)} disabled={currentPageIndex === 0}>&larr; Previous</button>
                <span>Page {currentPageIndex + 1} of {pages.length}</span>
                <button onClick={() => setCurrentPageIndex(p => p + 1)} disabled={currentPageIndex === pages.length - 1}>Next &rarr;</button>
            </div>
            
            {status === 'completed' && (
                <button onClick={handleDownloadPdf} className="story-download-btn">Download as PDF</button>
            )}
        </div>
    );
};

export default StoryViewer;