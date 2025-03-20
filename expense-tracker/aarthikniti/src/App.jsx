import React from 'react'
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";

import Login from './pages/Auth/Login';
import Signup from './pages/Auth/Signup';
import Income from './pages/Dashboard/Income';
import Expense from './pages/Dashboard/Expense';
import ForgotPassword from './pages/Auth/forgotpassword';
import DashboardPage from './pages/Dashboard/DashboardPage';

const App = () => {
  return (
    <div>
      <Router>
        <Routes>
          <Route path='/' element={<Root />} />
          <Route path='/login' element={<Login />} />
          <Route path='/signup' element={<Signup />} />
          <Route path='/dashboard' element={<DashboardPage />} />
          <Route path='/income' element={<Income />} />
          <Route path='/expense' element={<Expense />} />
          <Route path='/forgotpw' element={<ForgotPassword />} />
        </Routes>
      </Router>
    </div>
  );
}

const Root = () => {
  const isAuthenticated = !!localStorage.getItem("token");

  return isAuthenticated ? (
    <Navigate to="/dashboard" />
  ) : (
    <Navigate to="/login" />
  );
};

export default App;
