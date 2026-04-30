document.addEventListener('DOMContentLoaded', () => {
    const newsInput = document.getElementById('news-input');
    const charCount = document.getElementById('char-count');
    const analyzeBtn = document.getElementById('analyze-btn');
    const clearBtn = document.getElementById('clear-btn');

    const resultSection = document.getElementById('result-section');
    const verdictBadge = document.getElementById('verdict-badge');
    const confidenceScore = document.getElementById('confidence-score');
    const gaugeFill = document.getElementById('gauge-fill');
    const indicatorList = document.getElementById('indicator-list');
    const summaryText = document.getElementById('summary-text');

    const sensationalismBar = document.getElementById('sensationalism-bar');
    const objectivityBar = document.getElementById('objectivity-bar');
    const emotionBar = document.getElementById('emotion-bar');

    // Character count
    newsInput.addEventListener('input', () => {
        charCount.textContent = newsInput.value.length;
    });

    // Clear button
    clearBtn.addEventListener('click', () => {
        newsInput.value = '';
        charCount.textContent = '0';
        resultSection.classList.add('hidden');
    });

    // MAIN FIXED API CALL
    analyzeBtn.addEventListener('click', async () => {
        const text = newsInput.value.trim();

        if (text.length < 15) {
            alert('Enter valid news text');
            return;
        }

        analyzeBtn.disabled = true;

        try {
            const response = await fetch("https://fake-news-api-5lv4.onrender.com/predict", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ text: text })
            });

            if (!response.ok) {
                throw new Error("API error");
            }

            const data = await response.json();

            showResult(data);

        } catch (error) {
            console.error(error);
            alert("Backend error or API not working!");
        }

        analyzeBtn.disabled = false;
        resultSection.classList.remove('hidden');
    });

    function showResult(data) {
        const prediction = data.prediction.toLowerCase();
        const confidence = Math.round(data.confidence * 100);

        verdictBadge.textContent = prediction;
        verdictBadge.className = 'verdict-badge ' + prediction;

        summaryText.textContent = "Prediction from ML model.";

        const offset = 251.2 - (251.2 * confidence / 100);
        gaugeFill.style.strokeDashoffset = offset;

        confidenceScore.textContent = confidence;

        sensationalismBar.style.width = (prediction === "fake" ? 80 : 20) + "%";
        objectivityBar.style.width = (prediction === "real" ? 80 : 30) + "%";
        emotionBar.style.width = (prediction === "fake" ? 70 : 30) + "%";

        indicatorList.innerHTML = `
            <li>ML prediction</li>
            <li>Confidence score</li>
            <li>NLP processed</li>
        `;
    }
});
