const fs = require('fs');
const path = require('path');

const pharseDataDir = './pharseDATA';

const targetParticipants = ['Pocholo James Abon', 'Marc Joel', 'Julian Shaun M. Viloria', "Lance Calasag"];
let aggregatedMessages = [];

fs.readdir(pharseDataDir, { withFileTypes: true }, (err, dirents) => {
    if (err) {
        console.error('Error reading pharseDATA directory:', err);
        return;
    }

    const subdirs = dirents.filter(dirent => dirent.isDirectory()).map(dirent => dirent.name);

    subdirs.forEach(subdir => {
        const jsonPath = path.join(pharseDataDir, subdir, 'message_1.json');
        if (fs.existsSync(jsonPath)) {
            try {
                const data = fs.readFileSync(jsonPath, 'utf8');
                const chat = JSON.parse(data);
                if (chat.messages) {
                    const filteredMessages = chat.messages.filter(message =>
                        targetParticipants.includes(message.sender_name)
                    );
                    aggregatedMessages = aggregatedMessages.concat(filteredMessages);
                }
            } catch (error) {
                console.error(`Error processing file ${jsonPath}:`, error);
            }
        }
    });

    fs.writeFileSync('filtered_messages.json', JSON.stringify(aggregatedMessages, null, 2));
    console.log('Filtered messages saved to filtered_messages.json');
});
