import React, { useState } from 'react';
import axios from 'axios';
import "./auth.css";

const API_URL = 'http://localhost:5000/api/auth';

const Auth = ({ setToken }) => {
    const [isLogin, setIsLogin] = useState(true);
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        const endpoint = isLogin ? '/login' : '/register';
        const payload = isLogin ? { username, password } : { username, email, password };

        try {
            if (!isLogin) {
                await axios.post(`${API_URL}${endpoint}`, payload);
                alert('Registration successful! Please log in.');
                setIsLogin(true);
            } else {
                const response = await axios.post(`${API_URL}${endpoint}`, payload);
                setToken(response.data.access_token);
            }
        } catch (err) {
            setError(err.response?.data?.msg || 'An error occurred.');
        }
    };

    return (
        <div className="auth-modal-backdrop">
            <div className="auth-container">
                <h2>{isLogin ? 'Login to create stories!' : 'Register to create stories!'}</h2>
                {error && <p className="error-message">{error}</p>}
                <form onSubmit={handleSubmit} className="auth-form">
                    <input
                        type="text"
                        placeholder="Username"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        required
                    />
                    {!isLogin && (
                        <input
                            type="email"
                            placeholder="Email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                        />
                    )}
                    <input
                        type="password"
                        placeholder="Password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                    />
                    <button type="submit">{isLogin ? 'Login' : 'Create Account'}</button>
                </form>
                <div className="auth-toggle">
                    <button onClick={() => setIsLogin(!isLogin)}>
                        {isLogin ? 'Need an account? Register' : 'Have an account? Login'}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default Auth;