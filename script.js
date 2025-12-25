document.addEventListener('DOMContentLoaded', () => {
    const slides = document.querySelectorAll('.slide');
    const nextBtn = document.getElementById('next-btn');
    const prevBtn = document.getElementById('prev-btn');
    const music = document.getElementById('background-music');
    let currentSlide = 0;
    let musicStarted = false;
    let analysisData = {};
    let advancedAnalysisData = {};
    let validWordAnalysisData = {};

    // Function to fetch data
    async function fetchData() {
        try {
            const [analysisRes, advancedAnalysisRes, validWordAnalysisRes] = await Promise.all([
                fetch('analysis_results.json'),
                fetch('advanced_analysis.json'),
                fetch('valid_word_analysis_by_pos.json')
            ]);
            analysisData = await analysisRes.json();
            advancedAnalysisData = await advancedAnalysisRes.json();
            validWordAnalysisData = await validWordAnalysisRes.json(); // Store new data
            console.log('Analysis Data:', analysisData);
            console.log('Advanced Analysis Data:', advancedAnalysisData);
            console.log('Valid Word Analysis Data:', validWordAnalysisData);
            populateData();
        } catch (error) {
            console.error('Error fetching analysis data:', error);
        }
    }

    function showSlide(index) {
        slides.forEach(slide => slide.classList.remove('active'));
        slides[index].classList.add('active');

        prevBtn.style.display = index === 0 ? 'none' : 'inline-block';
        nextBtn.textContent = index === slides.length - 1 ? 'Finish' : 'Next';
    }

    function populateData() {
        // Populate Total Messages
        const totalMessagesElement = document.getElementById('total-messages');
        if (totalMessagesElement) {
            const totalMessagesCount = analysisData.analysis_results.reduce((sum, p) => sum + p.messageCount, 0);
            totalMessagesElement.textContent = totalMessagesCount.toLocaleString();
        }

        // Populate Top Emojis
        const topEmojisContainer = document.getElementById('top-emojis-container');
        if (topEmojisContainer && advancedAnalysisData.overall_analysis && advancedAnalysisData.overall_analysis.top_emojis) {
            topEmojisContainer.innerHTML = ''; // Clear placeholders
            advancedAnalysisData.overall_analysis.top_emojis.forEach(emojiItem => {
                const div = document.createElement('div');
                div.classList.add('emoji-item');
                div.innerHTML = `<span class="emoji-char">${emojiItem[0]}</span><span class="emoji-count">${emojiItem[1].toLocaleString()}</span>`;
                topEmojisContainer.appendChild(div);
            });
        }

        // Populate Top Yapper
        const topYapper = analysisData.analysis_results.reduce((prev, current) => (prev.messageCount > current.messageCount) ? prev : current);
        const topYapperName = document.getElementById('top-yapper-name');
        const topYapperMessageCount = document.getElementById('top-yapper-message-count');
        const topYapperProgressBar = document.getElementById('top-yapper-progress-bar');
        if (topYapperName) topYapperName.textContent = topYapper.name;
        if (topYapperMessageCount) topYapperMessageCount.textContent = `${topYapper.messageCount.toLocaleString()} Messages`;
        if (topYapperProgressBar) {
            const totalMessagesCount = analysisData.analysis_results.reduce((sum, p) => sum + p.messageCount, 0);
            const percentage = (topYapper.messageCount / totalMessagesCount) * 100;
            topYapperProgressBar.style.width = `${percentage}%`;
            topYapperProgressBar.title = `${percentage.toFixed(2)}% of total messages`;
        }

        // Populate Reading Level
        const readingLevelContainer = document.getElementById('reading-level-container');
        if (readingLevelContainer && advancedAnalysisData.analysis_by_participant) {
            readingLevelContainer.innerHTML = '';
            for (const participantName in advancedAnalysisData.analysis_by_participant) {
                const data = advancedAnalysisData.analysis_by_participant[participantName].reading_level;
                if (data) {
                    const div = document.createElement('div');
                    div.classList.add('participant-stat');
                    div.innerHTML = `
                        <h3>${participantName}</h3>
                        <p>Grade Level: <strong>${data.grade_level}</strong></p>
                        <p>Interpretation: ${data.interpretation}</p>
                    `;
                    readingLevelContainer.appendChild(div);
                }
            }
        }

        // Populate Sentiment Analysis
        const sentimentContainer = document.getElementById('sentiment-container');
        if (sentimentContainer && advancedAnalysisData.analysis_by_participant) {
            sentimentContainer.innerHTML = '';
            for (const participantName in advancedAnalysisData.analysis_by_participant) {
                const data = advancedAnalysisData.analysis_by_participant[participantName].sentiment;
                if (data) {
                    const div = document.createElement('div');
                    div.classList.add('participant-stat');
                    div.innerHTML = `
                        <h3>${participantName}</h3>
                        <p>Positive: ${data.positive_percent}%</p>
                        <p>Neutral: ${data.neutral_percent}%</p>
                        <p>Negative: ${data.negative_percent}%</p>
                    `;
                    sentimentContainer.appendChild(div);
                }
            }
        }

        // Populate Top Words (choosing the top yapper for this slide)
        const topWordsPersonName = document.getElementById('top-words-person-name');
        const topWordsList = document.getElementById('top-words-list');
        if (topWordsPersonName && topWordsList && topYapper && advancedAnalysisData.analysis_by_participant[topYapper.name]) {
            topWordsPersonName.textContent = topYapper.name;
            topWordsList.innerHTML = '';
            advancedAnalysisData.analysis_by_participant[topYapper.name].most_common_words.forEach(wordItem => {
                const li = document.createElement('li');
                li.textContent = `${wordItem[0]} (${wordItem[1]})`;
                topWordsList.appendChild(li);
            });
        }

        // Populate Overall Chat Insights
        const chatInitiator = document.getElementById('chat-initiator');
        if (chatInitiator && advancedAnalysisData.overall_analysis && advancedAnalysisData.overall_analysis.chat_initiator.length > 0) {
            chatInitiator.textContent = advancedAnalysisData.overall_analysis.chat_initiator[0][0];
        }

        const longestMonologueAuthor = document.getElementById('longest-monologue-author');
        const longestMonologueCount = document.getElementById('longest-monologue-count');
    
       
        if (longestMonologueAuthor && longestMonologueCount && advancedAnalysisData.overall_analysis && advancedAnalysisData.overall_analysis.longest_monologues_per_participant) {
            const allMonologues = Object.values(advancedAnalysisData.overall_analysis.longest_monologues_per_participant);
            if (allMonologues.length > 0) {
                const overallLongest = allMonologues.reduce((prev, current) => (prev.message_count > current.message_count) ? prev : current);
                longestMonologueAuthor.textContent = overallLongest.author;
                longestMonologueCount.textContent = overallLongest.message_count.toLocaleString();
            }
        }


        const questionAsker = document.getElementById('question-asker');
        if (questionAsker && advancedAnalysisData.overall_analysis && advancedAnalysisData.overall_analysis.question_askers.length > 0) {
            questionAsker.textContent = advancedAnalysisData.overall_analysis.question_askers[0][0];
        }

        // Populate Custom Words
        const customWordsContainer = document.getElementById('custom-words-container');
        if (customWordsContainer && advancedAnalysisData.analysis_by_participant) {
            customWordsContainer.innerHTML = '';
            const allCustomWords = {};
            for (const participantName in advancedAnalysisData.analysis_by_participant) {
                const customCounts = advancedAnalysisData.analysis_by_participant[participantName].custom_word_counts;
                for (const word in customCounts) {
                    if (!allCustomWords[word]) {
                        allCustomWords[word] = 0;
                    }
                    allCustomWords[word] += customCounts[word];
                }
            }
            
            for (const word in allCustomWords) {
                const div = document.createElement('div');
                div.classList.add('custom-word-item');
                div.innerHTML = `<strong>${word}:</strong> ${allCustomWords[word].toLocaleString()} times`;
                customWordsContainer.appendChild(div);
            }
        }
        
        // Populate Night Owls
        const nightOwlsContainer = document.getElementById('night-owls-container');
        if (nightOwlsContainer && advancedAnalysisData.overall_analysis && advancedAnalysisData.overall_analysis.night_owl_score) {
            nightOwlsContainer.innerHTML = '';
            advancedAnalysisData.overall_analysis.night_owl_score.forEach(item => {
                const div = document.createElement('div');
                div.classList.add('participant-stat');
                div.innerHTML = `<h3>${item[0]}</h3><p>${item[1].toLocaleString()} messages between 10 PM and 6 AM</p>`;
                nightOwlsContainer.appendChild(div);
            });
        }

        // Populate Top Words by Part of Speech and Longest Word
        const posPersonName = document.getElementById('pos-person-name');
        const posNounsList = document.getElementById('pos-nouns-list');
        const posAdjectivesList = document.getElementById('pos-adjectives-list');
        const posVerbsList = document.getElementById('pos-verbs-list');
        const longestWordDisplay = document.getElementById('longest-word-display');

        // Display data for the top yapper on this slide for now
        if (posPersonName && validWordAnalysisData && topYapper) {
            const participantPosData = validWordAnalysisData[topYapper.name];
            if (participantPosData) {
                posPersonName.textContent = topYapper.name;

                // Nouns
                posNounsList.innerHTML = '';
                participantPosData.nouns.forEach(item => {
                    const li = document.createElement('li');
                    li.textContent = `${item[0]} (${item[1]})`;
                    posNounsList.appendChild(li);
                });

                // Adjectives
                posAdjectivesList.innerHTML = '';
                participantPosData.adjectives.forEach(item => {
                    const li = document.createElement('li');
                    li.textContent = `${item[0]} (${item[1]})`;
                    posAdjectivesList.appendChild(li);
                });

                // Verbs
                posVerbsList.innerHTML = '';
                participantPosData.verbs.forEach(item => {
                    const li = document.createElement('li');
                    li.textContent = `${item[0]} (${item[1]})`;
                    posVerbsList.appendChild(li);
                });

                // Longest Word
                longestWordDisplay.textContent = participantPosData.longest_word;
            }
        }


    }


    nextBtn.addEventListener('click', () => {
        if (currentSlide < slides.length - 1) {
            currentSlide++;
            showSlide(currentSlide);

            // Play music for the first time when we move to the 2nd slide (index 1)
            // (assuming music is part of the existing HTML structure)
            if (currentSlide === 1 && music && !musicStarted) {
                music.play().catch(e => console.error("Audio playback failed:", e));
                musicStarted = true;
            }
        } else {
            alert('Merry Christmas!');
            currentSlide = 0;
            showSlide(currentSlide);
            if (music && musicStarted) {
                music.pause();
                music.currentTime = 0;
            }
            musicStarted = false;
        }
    });

    prevBtn.addEventListener('click', () => {
        if (currentSlide > 0) {
            currentSlide--;
            showSlide(currentSlide);
        }
    });

    const greetingsBtn = document.getElementById('greetings-btn');
    if (greetingsBtn) {
        const links = [
            'https://youtube.com/shorts/sA16WrAe_30',
            'https://youtube.com/shorts/Q9xc5Odzgsw?feature=share',
            'https://youtube.com/shorts/8gZpRjHa1uw?feature=share',
            'https://youtube.com/shorts/TuqEvUT6WrQ?feature=share',
            'https://youtube.com/shorts/PNV1r7eYAq0'
        ];

        greetingsBtn.addEventListener('click', () => {
            console.log('Greetings button clicked!');
            const randomIndex = Math.floor(Math.random() * links.length);
            const randomLink = links[randomIndex];
            console.log('Redirecting to:', randomLink);
            window.location.href = randomLink;
        });
    } else {
        console.error('Greetings button not found!');
    }

    // Initial load
    fetchData();
    showSlide(0);
});