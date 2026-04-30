const vocabulary = [
    { word: "crime", hint: "An illegal act for which someone can be punished by the government." },
    { word: "steal", hint: "To take something that belongs to someone else without permission." },
    { word: "break into", hint: "To enter a building or car by force, usually to steal something." },
    { word: "break the law", hint: "To do something illegal." },
    { word: "catch", hint: "To capture a person, especially a criminal." },
    { word: "criminal", hint: "A person who has committed a crime." },
    { word: "witness", hint: "A person who sees an event, typically a crime, take place." },
    { word: "burglary", hint: "The crime of illegally entering a building to steal things." },
    { word: "cybercrime", hint: "Criminal activities carried out by means of computers or the internet." },
    { word: "prosecute", hint: "To institute legal proceedings against a person." },
    { word: "give evidence", hint: "To provide information in a court of law to prove something." },
    { word: "punish", hint: "To inflict a penalty on someone for committing an offense." },
    { word: "challenge", hint: "To dispute the truth or validity of something." },
    { word: "proof", hint: "Evidence or argument establishing a fact or the truth of a statement." },
    { word: "trial", hint: "A formal examination of evidence in a court to decide guilt in a case." },
    { word: "lawyer", hint: "A professional who practices or studies law." }
];

// State
let selectedWord = "";
let selectedHint = "";
let correctLetters = [];
let wrongGuesses = 0;
const maxWrong = 6;
let playerCount = 1;
let currentPlayer = 1;
let scores = {};
let availableWords = [...vocabulary];

// DOM Elements
const setupScreen = document.getElementById('setup-screen');
const gameScreen = document.getElementById('game-screen');
const endScreen = document.getElementById('end-screen');

const playerCountInput = document.getElementById('player-count');
const btnDecrease = document.getElementById('btn-decrease');
const btnIncrease = document.getElementById('btn-increase');
const btnStart = document.getElementById('btn-start');

const wordDisplay = document.getElementById('word-display');
const keyboard = document.getElementById('keyboard');
const figureParts = document.querySelectorAll('.figure-part');
const notificationContainer = document.getElementById('notification-container');
const notificationText = document.getElementById('notification-text');

const btnHint = document.getElementById('btn-hint');
const clueText = document.getElementById('clue-text');
const playerTurnBadge = document.getElementById('player-turn-badge');
const scoreBoard = document.getElementById('score-board');

const endTitle = document.getElementById('end-title');
const endWordReveal = document.getElementById('end-word-reveal');
const finalScores = document.getElementById('final-scores');
const btnRestart = document.getElementById('btn-restart');

// Event Listeners for Setup
btnDecrease.addEventListener('click', () => {
    let val = parseInt(playerCountInput.value);
    if (val > 1) playerCountInput.value = val - 1;
});

btnIncrease.addEventListener('click', () => {
    let val = parseInt(playerCountInput.value);
    if (val < 4) playerCountInput.value = val + 1;
});

btnStart.addEventListener('click', startGame);
btnRestart.addEventListener('click', resetGame);
btnHint.addEventListener('click', showHint);

function initGame() {
    availableWords = [...vocabulary];
    scores = {};
    for (let i = 1; i <= playerCount; i++) {
        scores[i] = 0;
    }
    currentPlayer = 1;
}

function startGame() {
    playerCount = parseInt(playerCountInput.value);
    initGame();
    setupScreen.classList.remove('active');
    gameScreen.classList.add('active');
    startTurn();
}

function startTurn() {
    if (availableWords.length === 0) {
        // Game Over - No more words
        endGame(false, true);
        return;
    }

    correctLetters = [];
    wrongGuesses = 0;
    
    // Pick random word
    const randomIdx = Math.floor(Math.random() * availableWords.length);
    selectedWord = availableWords[randomIdx].word.toLowerCase();
    selectedHint = availableWords[randomIdx].hint;
    
    // Remove from available
    availableWords.splice(randomIdx, 1);

    // Update UI
    if (playerCount > 1) {
        playerTurnBadge.textContent = `Player ${currentPlayer}'s Turn`;
        playerTurnBadge.style.display = 'block';
    } else {
        playerTurnBadge.style.display = 'none';
    }
    updateScoreBoard();
    
    // Reset Graphics & Hint
    figureParts.forEach((part) => {
        part.style.display = 'none';
    });
    
    clueText.textContent = selectedHint;
    btnHint.disabled = false;

    displayWord();
    generateKeyboard();
}

function updateScoreBoard() {
    scoreBoard.innerHTML = '';
    for (let i = 1; i <= playerCount; i++) {
        const div = document.createElement('div');
        div.classList.add('player-score');
        if (i === currentPlayer) div.classList.add('active-score');
        div.innerHTML = `P${i}: <strong>${scores[i]}</strong>`;
        scoreBoard.appendChild(div);
    }
}

function displayWord() {
    wordDisplay.innerHTML = `
        ${selectedWord
            .split('')
            .map(letter => {
                if (letter === ' ') {
                    return `<span class="letter-box" style="border: none;"></span>`;
                }
                return `
                    <span class="letter-box">
                        ${correctLetters.includes(letter) ? letter : ''}
                    </span>
                `;
            })
            .join('')}
    `;

    const innerWord = wordDisplay.innerText.replace(/\n/g, '');
    const cleanSelectedWord = selectedWord.replace(/\s/g, '');
    
    if (innerWord.toLowerCase() === cleanSelectedWord) {
        // Win
        scores[currentPlayer] += 10;
        setTimeout(() => endGame(true), 500);
    }
}

function generateKeyboard() {
    keyboard.innerHTML = '';
    const letters = 'abcdefghijklmnopqrstuvwxyz';
    letters.split('').forEach(letter => {
        const button = document.createElement('button');
        button.innerText = letter;
        button.classList.add('key');
        button.addEventListener('click', () => handleGuess(letter, button));
        keyboard.appendChild(button);
    });
}

function handleGuess(letter, button) {
    button.disabled = true;

    if (selectedWord.includes(letter)) {
        button.classList.add('correct');
        correctLetters.push(letter);
        displayWord();
    } else {
        button.classList.add('wrong');
        wrongGuesses++;
        updateFigure();

        if (wrongGuesses === maxWrong) {
            setTimeout(() => endGame(false), 500);
        }
    }
}

function updateFigure() {
    if (wrongGuesses <= maxWrong) {
        figureParts[wrongGuesses - 1].style.display = 'block';
    }
}

function showHint() {
    // Reveal a random letter
    const unrevealedLetters = selectedWord.split('').filter(l => l !== ' ' && !correctLetters.includes(l));
    if (unrevealedLetters.length > 0) {
        const randomLetter = unrevealedLetters[Math.floor(Math.random() * unrevealedLetters.length)];
        
        // Find the button for this letter and click it
        const keys = document.querySelectorAll('.key');
        keys.forEach(key => {
            if (key.innerText.toLowerCase() === randomLetter && !key.disabled) {
                key.click();
            }
        });
        
        scores[currentPlayer] = Math.max(0, scores[currentPlayer] - 2); // Penalty for hint
        updateScoreBoard();
    }
    
    // Disable button if no more letters to reveal or only 1 left
    const remainingAfter = selectedWord.split('').filter(l => l !== ' ' && !correctLetters.includes(l));
    if (remainingAfter.length <= 1) {
        btnHint.disabled = true;
    }
}

function showNotification(msg) {
    notificationText.innerText = msg;
    notificationContainer.classList.add('show');
    setTimeout(() => {
        notificationContainer.classList.remove('show');
    }, 2000);
}

function endGame(isWin, isOutOfWords = false) {
    gameScreen.classList.remove('active');
    endScreen.classList.add('active');

    if (isOutOfWords) {
        endTitle.innerText = "MISSION COMPLETE";
        endTitle.className = 'win';
        endWordReveal.innerText = "All vocabulary words have been reviewed.";
    } else {
        if (isWin) {
            endTitle.innerText = "SUCCESS!";
            endTitle.className = 'win';
            endWordReveal.innerText = `You solved it: ${selectedWord.toUpperCase()}`;
        } else {
            endTitle.innerText = "FAILED!";
            endTitle.className = 'lose';
            endWordReveal.innerText = `The word was: ${selectedWord.toUpperCase()}`;
        }
    }

    // Build final scores
    finalScores.innerHTML = '<h3>Final Scores</h3>';
    for (let i = 1; i <= playerCount; i++) {
        finalScores.innerHTML += `
            <div class="final-score-item">
                <span>Player ${i}</span>
                <span>${scores[i]} pts</span>
            </div>
        `;
    }

    // Change btn to "NEXT TURN" if not out of words
    if (!isOutOfWords && availableWords.length > 0) {
        btnRestart.innerText = "NEXT TURN";
        btnRestart.onclick = () => {
            currentPlayer = (currentPlayer % playerCount) + 1;
            endScreen.classList.remove('active');
            gameScreen.classList.add('active');
            startTurn();
        };
    } else {
        btnRestart.innerText = "PLAY AGAIN";
        btnRestart.onclick = () => {
            initGame();
            endScreen.classList.remove('active');
            setupScreen.classList.add('active');
            playerCountInput.value = 1;
        };
    }
}

// Handle keyboard press
window.addEventListener('keydown', e => {
    if (gameScreen.classList.contains('active')) {
        if (e.key >= 'a' && e.key <= 'z') {
            const keys = document.querySelectorAll('.key');
            keys.forEach(key => {
                if (key.innerText.toLowerCase() === e.key && !key.disabled) {
                    key.click();
                }
            });
        }
    }
});
