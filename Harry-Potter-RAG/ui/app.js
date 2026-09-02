const apiUrlInput = document.getElementById("api-url");
const healthButton = document.getElementById("health-button");
const healthDot = document.getElementById("health-dot");

const questionInput = document.getElementById("question");
const askButton = document.getElementById("ask-button");

const resultStatus = document.getElementById("result-status");
const emptyState = document.getElementById("empty-state");

const answerSection = document.getElementById("answer-section");
const answerQuestion = document.getElementById("answer-question");
const answerText = document.getElementById("answer-text");

const sourcesSection = document.getElementById("sources-section");
const sourcesList = document.getElementById("sources-list");

const errorBar = document.getElementById("error-bar");

const confidenceBadge =
  document.getElementById("confidence");

function getApiUrl() {
  return apiUrlInput.value
    .trim()
    .replace(/\/$/, "");
}

function showError(message) {
  errorBar.textContent = message;
  errorBar.classList.add("show");
}

function clearError() {
  errorBar.classList.remove("show");
}

async function typeAnswer(text) {
  answerText.textContent = "";

  for (const letter of text) {
    answerText.textContent += letter;

    await new Promise((resolve) =>
      setTimeout(resolve, 12)
    );
  }
}

healthButton.addEventListener("click", async () => {
  clearError();

  healthButton.textContent = "Checking...";
  healthButton.disabled = true;

  healthDot.className = "dot idle";

  try {
    const response = await fetch(
      `${getApiUrl()}/health`
    );

    const data = await response.json();

    healthDot.className =
      data.status === "ok"
        ? "dot ok"
        : "dot error";

    if (data.status !== "ok") {
      showError(
        "The API responded, but its health check was not OK."
      );
    }
  } catch {
    healthDot.className = "dot error";

    showError(
      "Could not reach the API. Check the URL and make sure FastAPI is running."
    );
  }

  healthButton.textContent = "Ping API";
  healthButton.disabled = false;
});

async function askQuestion() {
  clearError();

  const query = questionInput.value.trim();

  if (!query) {
    showError("Write a question first.");
    return;
  }

  askButton.disabled = true;
  askButton.textContent = "Searching the books...";

  resultStatus.textContent =
    "Retrieving pages...";

  emptyState.style.display = "none";
  answerSection.style.display = "block";

  answerQuestion.textContent =
    `Question: ${query}`;

  answerText.textContent =
    "The library is searching...";

  sourcesList.innerHTML = "";
  sourcesSection.style.display = "none";
  confidenceBadge.style.display = "none";

  try {
    const response = await fetch(
      `${getApiUrl()}/query`,
      {
        method: "POST",
        headers: {
          "Content-Type":
            "application/json",
        },
        body: JSON.stringify({
          query,
        }),
      }
    );

    if (!response.ok) {
      throw new Error(
        `Server error (${response.status})`
      );
    }

    const data = await response.json();

    await typeAnswer(data.answer);

    resultStatus.textContent =
      `Route: ${data.route}`;

    if (data.confidence !== undefined) {
      confidenceBadge.style.display =
        "inline-block";

      const confidencePercent =
        Math.round(
          data.confidence * 100
        );

      confidenceBadge.textContent =
        `Confidence: ${confidencePercent}%`;

      if (confidencePercent >= 80) {
        confidenceBadge.style.background =
          "#0f6d31";
      } else if (
        confidencePercent >= 50
      ) {
        confidenceBadge.style.background =
          "#ca8a04";
      } else {
        confidenceBadge.style.background =
          "#ad1d1d";
      }
    }

    sourcesSection.style.display =
      data.sources.length
        ? "block"
        : "none";

    data.sources.forEach((source) => {
      const item =
        document.createElement("div");

      item.className = "source";

      item.innerHTML = `
        <span class="page-number">
          ${source.page_number}
        </span>

        <span>
          ${source.book_name}
        </span>

        <small>
          Score: ${(source.score * 100).toFixed(1)}%
        </small>
      `;

      sourcesList.appendChild(item);
    });
  } catch (error) {
    answerSection.style.display = "none";
    emptyState.style.display = "grid";

    confidenceBadge.style.display = "none";

    resultStatus.textContent =
      "Waiting for a question";

    showError(
      error.message ||
        "Could not get an answer from the API."
    );
  }

  askButton.disabled = false;
  askButton.textContent =
    "Reveal the Answer";
}

askButton.addEventListener(
  "click",
  askQuestion
);

questionInput.addEventListener(
  "keydown",
  (event) => {
    if (
      event.key === "Enter" &&
      event.ctrlKey
    ) {
      askQuestion();
    }
  }
);

document
  .querySelectorAll(".chip")
  .forEach((chip) => {
    chip.addEventListener(
      "click",
      () => {
        questionInput.value =
          chip.textContent;

        questionInput.focus();
      }
    );
  });