import { useNavigate } from "react-router-dom";

function Language() {
  const navigate = useNavigate();

  const languages = [
    { name: "English", code: "en" },
    { name: "Kannada", code: "kn" },
    { name: "Tulu", code: "tcy" },
    
  ];

  const selectLanguage = (code) => {
    localStorage.setItem(
      "selectedLanguage",
      code
    );

    navigate("/chat", {
      state: {
        language: code,
      },
    });
  };

  return (
    <div className="language-page">
      <div className="language-container">

        <h1>Select Your Language</h1>

        <p>
          Choose the language you want to
          communicate in.
        </p>

        <div className="language-list">

          {languages.map((language) => (
            <button
              key={language.code}
              className="language-button"
              onClick={() =>
                selectLanguage(language.code)
              }
            >
              {language.name}
            </button>
          ))}

        </div>

      </div>
    </div>
  );
}

export default Language;