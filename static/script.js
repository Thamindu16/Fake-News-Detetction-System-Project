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

    // Tabs
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            if (tab.dataset.tab === 'url') {
                newsInput.placeholder = "Enter article URL...";
            } else {
                newsInput.placeholder = "Paste news text...";
            }
        });
    });

    // Character count
    newsInput.addEventListener('input', () => {
        charCount.textContent = newsInput.value.length;
    });

    // Clear button
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
    }

    // 🔥 MAIN FIX: REAL API CALL
    analyzeBtn.addEventListener('click', async () => {
        const text = newsInput.value.trim();

        if (text.length < 15) {
            alert('Please enter valid text');
            return;
        }

        analyzeBtn.classList.add('loading');
        analyzeBtn.disabled = true;
        resultSection.classList.add('hidden');
        resetUI();

        try {
            const response = await fetch("https://fake-news-api-5lv4.onrender.com", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ text: text })
            });

            const data = await response.json();

            showResult(data);

        } catch (error) {
            alert("Backend connection error!");
            console.error(error);
        }

        analyzeBtn.classList.remove('loading');
        analyzeBtn.disabled = false;

        resultSection.classList.remove('hidden');
    });

    // 🔥 Update UI using REAL ML result
    function showResult(data) {
        const prediction = data.prediction.toLowerCase();
        const confidence = Math.round(data.confidence * 100);

        verdictBadge.textContent = prediction;
        verdictBadge.className = 'verdict-badge ' + prediction;

        summaryText.textContent = "Result generated using trained Machine Learning model.";

        const offset = 251.2 - (251.2 * (confidence / 100));
        gaugeFill.className.baseVal = 'gauge-fill ' + prediction;

        setTimeout(() => {
            gaugeFill.style.strokeDashoffset = offset;

            // Animate number
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

            // Bars (simple logic)
            sensationalismBar.style.width = (prediction === "fake" ? 80 : 20) + "%";
            objectivityBar.style.width = (prediction === "real" ? 80 : 30) + "%";
            emotionBar.style.width = (prediction === "fake" ? 70 : 30) + "%";

        }, 50);

        // Indicators
        indicatorList.innerHTML = `
            <li>Prediction from trained ML model</li>
            <li>Confidence based on probability score</li>
            <li>Processed using NLP vectorization</li>
        `;
    }
});
