import React from 'react'
import './Hero.css'
import { Link } from "react-router-dom";
import heroVideo from '../../assets/bgvideo.mp4'

const Hero = () => {
  return (
    <div className='hero'>
      <video src={heroVideo} autoPlay muted loop playsInline />
      
      {/* Side text overlay box */}
      <div className="hero-overlay-box">
        <h2>ADMISSIONS ARE OPEN</h2>
        <p>Become a VITian Today!</p>
        <Link to="/admissions"><button className="overlay-btn">GET STARTED</button></Link>
        
      </div>
      
      {/* Bottom action buttons */}
      <div className="hero-bottom-actions">
        <button className="action-btn">HOW TO APPLY</button>
        <button className="action-btn">VIRTUAL TOUR</button>
        <button className="action-btn">CAMPUS VISIT</button>
        <button className="action-btn">COST AND AID</button>
      </div>
    </div>
  )
}

export default Hero