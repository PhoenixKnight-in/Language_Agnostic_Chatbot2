import Widget from "./Components/Widget/widget";

function App() {
  return (
    <div>
      <Widget
        apiBaseUrl="http://0.0.0.0:8000"
        enableFeedback={true}
        enableAnalytics={true}
      />
    </div>
  );
}