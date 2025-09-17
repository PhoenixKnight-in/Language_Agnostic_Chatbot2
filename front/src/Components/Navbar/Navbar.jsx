import React, { useState } from "react";
import { Link } from "react-router-dom";
import "./Navbar.css";
import logo from "../../assets/vitlogo1.png";

const Navbar = () => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  return (
    <>
      {/* Top utility bar */}
      <div className="navbar-top-bar">
        <div className="container">
          <div className="top-links">
            <Link to="/student-portal">Student Portal</Link>
            <Link to="/faculty">Faculty</Link>
            <Link to="/library">Library</Link>
            <Link to="/contact">Contact Us</Link>
          </div>
          <div className="top-actions">
            <Link to="/admissions" className="apply-now-btn">Apply Now</Link>
          </div>
        </div>
      </div>

      {/* Main navigation */}
      <nav className="main-navbar fixed top-0 left-0 w-full z-50 bg-blue-800">
        <div className="navbar-container">
          <div className="logo-section">
            <img src={logo} alt="VIT Logo" />
            <div className="university-text">
              <span className="university-name">VIT University</span>
              <span className="university-tagline">Excellence in Education</span>
            </div>
          </div>

          <ul className={`nav-menu ${isMobileMenuOpen ? 'mobile-active' : ''}`}>
            <li className="nav-item">
              <Link to="/" className="nav-link">
                <span>Home</span>
              </Link>
            </li>
            <li className="nav-item dropdown">
              <Link to="/about" className="nav-link">
                <span>About</span>
                
              </Link>
              
            </li>
            <li className="nav-item dropdown">
              <Link to="/academics" className="nav-link">
                <span>Academics</span>
                <i className="dropdown-icon">▾</i>
              </Link>
              <div className="dropdown-menu">
                <Link to="/academics/undergraduate">Undergraduate</Link>
                <Link to="/academics/graduate">Graduate</Link>
                <Link to="/academics/research">Research Programs</Link>
                <Link to="/academics/faculty">Faculty Directory</Link>
              </div>
            </li>
            <li className="nav-item">
              <Link to="/admissions" className="nav-link">
                <span>Admissions</span>
              </Link>
            </li>
            <li className="nav-item">
              <Link to="/campus-life" className="nav-link">
                <span>Campus Life</span>
              </Link>
            </li>
            <li className="nav-item">
              <Link to="/news" className="nav-link">
                <span>News</span>
              </Link>
            </li>
          </ul>

          <div className="nav-right">
            <div className="search-box">
              <input type="text" placeholder="Search..." />
              <button className="search-btn">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="11" cy="11" r="8"/>
                  <path d="m21 21-4.35-4.35"/>
                </svg>
              </button>
            </div>
            
            <button 
              className="mobile-menu-toggle" 
              onClick={toggleMobileMenu}
              aria-label="Toggle mobile menu"
            >
              <span className={`hamburger ${isMobileMenuOpen ? 'active' : ''}`}>
                <span></span>
                <span></span>
                <span></span>
              </span>
            </button>
          </div>
        </div>
      </nav>
    </>
  );
};

export default Navbar;