document.addEventListener('DOMContentLoaded', () => {

    const newsInput = document.getElementById('news-input');
    const charCount = document.getElementById('char-count');
    const analyzeBtn = document.getElementById('analyze-btn');
    const clearBtn = document.getElementById('clear-btn');
    const tabs = document.querySelectorAll('.tab');

    const resultSection = document.getElementById('result-section');
    const verdictBadge = document.getElementById('verdict-badge');
    const confidenceScore = document.getElementById('confidence-score');
    const gaugeFill = document.getElementById('gauge-fill');
    const indicatorList = document.getElementById('indicator-list');
    const summaryText = document.getElementById('summary-text');

    const sensationalismBar = document.getElementById('sensationalism-bar');
    const objectivityBar = document.getElementById('objectivity-bar');
    const emotionBar = document.getElementById('emotion-bar');

    // IMPORTANT: change if your API endpoint changes
    const API_URL = "https://fake-news-api-5lv4.onrender.com/predict";

    // Tabs
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            newsInput.placeholder = tab.dataset.tab === 'url'
                ? "Enter article URL..."
                : "Paste news text...";
        });
    });

    // Character count
    newsInput.addEventListener('input', () => {
        charCount.textContent = newsInput.value.length;
    });

    // Clear
    clearBtn.addEventListener('click', () => {
        newsInput.value = '';
        charCount.textContent = '0';
        resultSection.classList.add('hidden');
        resetUI();
    });

    function resetUI() {
        gaugeFill.style.strokeDashoffset = '251.2';
        confidenceScore.textContent = '0';
        sensationalismBar.style.width = '0%';
        objectivityBar.style.width = '0%';
        emotionBar.style.width = '0%';
        summaryText.textContent = '';
        indicatorList.innerHTML = '';
        verdictBadge.textContent = '';
        verdictBadge.className = 'verdict-badge';
    }

    // MAIN ANALYZE
    analyzeBtn.addEventListener('click', async () => {

        const text = newsInput.value.trim();

        if (text.length < 15) {
            alert('Please enter valid text (min 15 chars)');
            return;
        }

        analyzeBtn.classList.add('loading');
        analyzeBtn.disabled = true;

        resetUI();
        resultSection.classList.add('hidden');

        try {
            const response = await fetch(API_URL, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ text })
            });

            // API down / cold start
            if (!response.ok) {
                throw new Error("API not responding");
            }

            const data = await response.json();

            // Validate response
            if (!data.prediction || data.confidence === undefined) {
                throw new Error("Invalid API response");
            }

            showResult(data);

        } catch (error) {

            console.error("API ERROR:", error);

            // 🔥 FALLBACK DEMO MODE
            showDemoResult();

        }

        analyzeBtn.classList.remove('loading');
        analyzeBtn.disabled = false;

        resultSection.classList.remove('hidden');
    });

    // REAL RESULT
    function showResult(data) {

        const prediction = data.prediction.toLowerCase();
        const confidence = Math.round(data.confidence * 100);

        verdictBadge.textContent = prediction.toUpperCase();
        verdictBadge.className = 'verdict-badge ' + prediction;

        summaryText.textContent = "Analyzed using Machine Learning model.";

        animateUI(prediction, confidence);

        indicatorList.innerHTML = `
            <li>ML prediction completed</li>
            <li>Confidence based on probability score</li>
            <li>Processed using NLP vectorization</li>
        `;
    }

    // DEMO FALLBACK
    function showDemoResult() {

        const prediction = "fake";
        const confidence = 85;

        verdictBadge.textContent = "DEMO (FAKE)";
        verdictBadge.className = 'verdict-badge fake';

        summaryText.textContent =
            "⚠️ Backend not reachable. Showing demo result.";

        animateUI(prediction, confidence);

        indicatorList.innerHTML = `
            <li>Demo mode activated</li>
            <li>Backend connection failed</li>
            <li>Check API deployment</li>
        `;
    }

    // COMMON UI ANIMATION
    function animateUI(prediction, confidence) {

        const offset = 251.2 - (251.2 * (confidence / 100));
        gaugeFill.className.baseVal = 'gauge-fill ' + prediction;

        setTimeout(() => {

            gaugeFill.style.strokeDashoffset = offset;

            let current = 0;
            const interval = setInterval(() => {
                current += 2;
                if (current >= confidence) {
                    clearInterval(interval);
                    confidenceScore.textContent = confidence;
                } else {
                    confidenceScore.textContent = current;
                }
            }, 20);

            sensationalismBar.style.width = (prediction === "fake" ? 80 : 20) + "%";
            objectivityBar.style.width = (prediction === "real" ? 80 : 30) + "%";
            emotionBar.style.width = (prediction === "fake" ? 70 : 30) + "%";

        }, 100);
    }

});
