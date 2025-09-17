import React from "react";
import Navbar from "../Components/Navbar/Navbar";
import Hero from "../Components/Hero/Hero";

const Home = () => {
  return (
    <div >
      {/* Navbar fixed at top */}
      <Navbar />

      {/* Main content */}
      <main >
        <Hero />
      </main>
    </div>
  );
};

export default Home;
