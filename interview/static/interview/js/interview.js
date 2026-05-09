const cameraPreview = document.getElementById('cameraPreview');
const startCameraButton = document.getElementById('startCamera');
const toggleSpeechButton = document.getElementById('toggleSpeech');
const questionText = document.getElementById('questionText');
const answerText = document.getElementById('answerText');
const currentIndexElement = document.getElementById('currentIndex');
const progressFill = document.getElementById('progressFill');
const previousBtn = document.getElementById('previousBtn');
const nextBtn = document.getElementById('nextBtn');
const evaluateBtn = document.getElementById('evaluateBtn');
const resultBlock = document.getElementById('resultBlock');
const resultScore = document.getElementById('resultScore');
const resultStrength = document.getElementById('resultStrength');
const resultWeakness = document.getElementById('resultWeakness');
const resultImprovement = document.getElementById('resultImprovement');
const saveScoreBtn = document.getElementById('saveScoreBtn');

let currentIndex = 0;
let timerInterval = null;
let timeLeft = 60;
const answers = new Array(questions.length).fill('');
let recognition = null;
let isRecognizing = false;

function safeText(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function updateProgress() {
    currentIndexElement.textContent = currentIndex + 1;
    const percent = ((currentIndex + 1) / questions.length) * 100;
    progressFill.style.width = `${percent}%`;
}

function updateQuestion() {
    answerText.value = answers[currentIndex] || '';
    questionText.textContent = questions[currentIndex].text;
    updateProgress();
    resetTimer();
    resultBlock.classList.remove('visible');
}

function resetTimer() {
    clearInterval(timerInterval);
    timeLeft = 60;
    document.getElementById('timerValue').textContent = timeLeft;
    timerInterval = setInterval(() => {
        timeLeft -= 1;
        document.getElementById('timerValue').textContent = timeLeft;
        if (timeLeft <= 0) {
            clearInterval(timerInterval);
            evaluateAnswer();
        }
    }, 1000);
}

function requestCamera() {
    navigator.mediaDevices.getUserMedia({ video: true, audio: false })
        .then((stream) => {
            cameraPreview.srcObject = stream;
        })
        .catch((error) => {
            alert('Unable to access camera: ' + error.message);
        });
}

function initSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        toggleSpeechButton.disabled = true;
        toggleSpeechButton.textContent = 'Speech Not Supported';
        return;
    }
    recognition = new SpeechRecognition();
    recognition.lang = 'en-US';
    recognition.interimResults = true;
    recognition.continuous = true;
    recognition.onresult = (event) => {
        let transcript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
            transcript += event.results[i][0].transcript;
        }
        answerText.value = answers[currentIndex] = transcript;
    };
    recognition.onerror = (event) => {
        console.error('Speech recognition error', event.error);
        if (event.error === 'no-speech') {
            recognition.stop();
            isRecognizing = false;
            toggleSpeechButton.textContent = 'Start Speech';
        }
    };
}

function toggleSpeech() {
    if (!recognition) return;
    if (isRecognizing) {
        recognition.stop();
        isRecognizing = false;
        toggleSpeechButton.textContent = 'Start Speech';
        answers[currentIndex] = answerText.value;
        return;
    }
    recognition.start();
    isRecognizing = true;
    toggleSpeechButton.textContent = 'Stop Speech';
}

function getCsrfToken() {
    const cookieValue = document.cookie.match('(^|;)\\s*csrftoken\\s*=\\s*([^;]+)');
    return cookieValue ? cookieValue.pop() : '';
}

function evaluateAnswer() {
    const answer = answerText.value.trim();
    if (!answer) {
        alert('Please provide an answer before submission.');
        return;
    }
    const formData = new FormData();
    formData.append('question_id', questions[currentIndex].id);
    formData.append('answer_text', answer);
    fetch('/evaluate_answer/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCsrfToken(),
        },
        body: formData,
        credentials: 'same-origin',
    })
        .then((response) => response.json())
        .then((data) => {
            answers[currentIndex] = answer;
            resultScore.textContent = `${data.score}/10`;
            resultStrength.textContent = data.strength;
            resultWeakness.textContent = data.weakness;
            resultImprovement.textContent = data.improvement;
            resultBlock.classList.add('visible');
        })
        .catch((error) => {
            console.error(error);
            alert('Unable to evaluate answer at the moment.');
        });
}

function saveScore() {
    const formData = new FormData();
    formData.append('interview_id', interviewId);
    fetch('/save_score/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCsrfToken(),
        },
        body: formData,
        credentials: 'same-origin',
    })
        .then((response) => response.json())
        .then((data) => {
            window.location.href = '/view_scores/';
        })
        .catch((error) => {
            console.error(error);
            alert('Unable to save score.');
        });
}

previousBtn.addEventListener('click', () => {
    answers[currentIndex] = answerText.value;
    if (currentIndex > 0) {
        currentIndex -= 1;
        updateQuestion();
    }
});

nextBtn.addEventListener('click', () => {
    answers[currentIndex] = answerText.value;
    if (currentIndex < questions.length - 1) {
        currentIndex += 1;
        updateQuestion();
    }
});

evaluateBtn.addEventListener('click', evaluateAnswer);
saveScoreBtn.addEventListener('click', saveScore);
startCameraButton.addEventListener('click', requestCamera);
toggleSpeechButton.addEventListener('click', toggleSpeech);

initSpeechRecognition();
updateQuestion();
