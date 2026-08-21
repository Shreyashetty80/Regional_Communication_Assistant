import { useNavigate } from "react-router-dom";

function Language() {
  const navigate = useNavigate();

  const languages = [
    "English",
    "Kannada",
    "Tulu",
    "Konkani"
  ];

  const selectLanguage = (language) => {
    localStorage.setItem("selectedLanguage", language);
    navigate("/chat");
  };

  return (
    <div className="language-page">
      <div className="language-container">
        <h1>Select Your Language</h1>

        <p>
          Choose the language you want to communicate in.
        </p>

        <div className="language-list">
          {languages.map((language) => (
            <button
              key={language}
              className="language-button"
              onClick={() => selectLanguage(language)}
            >
              {language}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

export default Language;