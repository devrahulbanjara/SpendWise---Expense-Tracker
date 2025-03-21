import React, { useState } from 'react';

const DashboardPage = () => {
    const [darkMode, setDarkMode] = useState(false);
    const [accountType, setAccountType] = useState('Personal');
    const [transactions, setTransactions] = useState([]);

    const toggleDarkMode = () => {
        setDarkMode(!darkMode);
    };

    return (
        <div className={darkMode ? 'dark' : ''}>
            <div>
                <img src="" alt="Dashboard" className='' />
                <select 
                    className='' 
                    value={accountType} 
                    onChange={(e) => setAccountType(e.target.value)}
                >
                    <option value="Personal">Personal</option>
                    <option value="Business">Business</option>
                    <option value="Travel">Travel</option>
                    <option value="Others">Others</option>
                </select>
            </div>
            <button onClick={toggleDarkMode}>
                Toggle Dark Mode
            </button>
        </div>
    );
}

export default DashboardPage;
