import { Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import About from "./pages/About";
import Academics from "./pages/Academics";
import Admissions from "./pages/Admissions";
import Widget from "./Components/Widget/widget";

const App = () => {
  return (
    <div className="pt-32 min-h-screen">
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/about" element={<About />} />
        <Route path="/academics" element={<Academics />} />
        <Route path="/admissions" element={<Admissions />} />
      </Routes>
      <Widget
        apiBaseUrl="http://localhost:8000"
        enableFeedback={true}
        enableAnalytics={true}
      />
    </div>
  );
};

export default App;
