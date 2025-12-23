const fs = require('fs');

const filteredMessagesPath = './filtered_messages.json';

if (!fs.existsSync(filteredMessagesPath)) {
    console.error('Error: filtered_messages.json not found. Please run filter_data.js first.');
    return;
}

const messages = JSON.parse(fs.readFileSync(filteredMessagesPath, 'utf8'));

const analysis = {};
let totalMessageCount = 0;
let totalWordCount = 0;

messages.forEach(message => {
    const name = message.sender_name;
    const content = message.content || '';
    const wordCount = content.split(' ').filter(word => word !== '').length;

    if (!analysis[name]) {
        analysis[name] = {
            messageCount: 0,
            wordCount: 0,
        };
    }

    analysis[name].messageCount++;
    analysis[name].wordCount += wordCount;
    totalMessageCount++;
    totalWordCount += wordCount;
});

const analysisResults = {
    analysis_results: []
};

for (const name in analysis) {
    const participantData = analysis[name];
    const messagePercentage = (participantData.messageCount / totalMessageCount) * 100;
    const wordPercentage = (participantData.wordCount / totalWordCount) * 100;

    analysisResults.analysis_results.push({
        name: name,
        message_percentage: parseFloat(messagePercentage.toFixed(2)),
        word_percentage: parseFloat(wordPercentage.toFixed(2)),
        messageCount: participantData.messageCount,
        wordCount: participantData.wordCount,
        avgWordsPerMessage: parseFloat((participantData.wordCount / participantData.messageCount).toFixed(2))
    });
}

fs.writeFileSync('analysis_results.json', JSON.stringify(analysisResults, null, 2));
console.log('Analysis results saved to analysis_results.json');
