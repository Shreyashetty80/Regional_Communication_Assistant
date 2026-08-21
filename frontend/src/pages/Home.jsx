import { useNavigate } from "react-router-dom";

function Home() {
  const navigate = useNavigate();

  return (
    <div className="home-page">
      <div className="home-container">
        <h1>Regional Communication Assistant</h1>

        <p>
          Communicate easily using your preferred regional language.
        </p>

        <p>
          Choose your language and start chatting with our AI assistant.
        </p>

        <button
          className="start-button"
          onClick={() => navigate("/language")}
        >
          Get Started
        </button>
      </div>
    </div>
  );
}

export default Home;