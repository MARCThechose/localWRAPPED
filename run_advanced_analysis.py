import json
import re
from collections import Counter
import nltk
from nltk.corpus import stopwords
import emoji
import textstat
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from datetime import datetime
import argparse

# --- CONFIGURATION ---

# Top N most common words to find
TOP_N_WORDS = 20


# You can edit this list to search for your own words!
CUSTOM_WORDS_TO_COUNT = ['skibidi', 'rizz', 'gyatt', 'fanum tax']

# --- NEW ANALYSIS PARAMETERS ---
EXCUSE_WORDS = ['sorry', 'late', 'cant', 'wont', 'busy', 'forgot']
SELF_PRONOUNS = ['i', 'me', 'my', 'mine', 'myself']
INTERJECTIONS = ['uh', 'um', 'er', 'ah', 'oh', 'wow', 'hmm', 'huh']

# --- MAIN ANALYSIS LOGIC ---

def analyze_messages(input_file, output_file):
    """
    Main function to run all advanced analysis on the chat messages.
    """
    print("Starting advanced analysis...")

    # Load the filtered messages
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            messages = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: Input file not found at '{input_file}'. Please make sure it exists.")
        return
    except json.JSONDecodeError:
        print(f"ERROR: Could not decode JSON from '{input_file}'. The file might be corrupted.")
        return

    # It is recommended to fix encoding issues at the source, in the script that generates the JSON file.
    # The following code block is a temporary workaround for encoding issues.
    # It tries to decode the content with utf-8, and if it fails, it tries to fix it.
    # This is not a robust solution and may corrupt some messages.
    for message in messages:
        if 'content' in message and isinstance(message['content'], str):
            try:
                # Attempt to see if it's mis-encoded. This is a common pattern for fixing mojibake.
                message['content'].encode('latin1')
            except UnicodeEncodeError:
                # This suggests the string is already proper UTF-8, so we do nothing.
                pass
            else:
                # If latin1 encoding succeeds, it's likely it was double-encoded.
                try:
                    message['content'] = message['content'].encode('latin1').decode('utf-8')
                except (UnicodeEncodeError, UnicodeDecodeError):
                    pass # Leave as is if the fix fails.

    # Define a pattern for reaction messages. Note: this is language-dependent.
    reaction_pattern = re.compile(r"reacted .* to a message", re.IGNORECASE)

    # Filter out non-text and reaction messages
    text_messages = []
    for msg in messages:
        content = msg.get('content')
        if content and not reaction_pattern.search(content):
            text_messages.append(msg)
    
    # Setup participants
    participants = sorted(list(set(msg['sender_name'] for msg in text_messages)))
    analysis_by_participant = {name: {} for name in participants}

    print(f"Found {len(text_messages)} text messages from {len(participants)} participants.")

    # Run all analysis functions
    for name in participants:
        participant_messages = [msg for msg in text_messages if msg['sender_name'] == name]
        print(f"\nAnalyzing messages for {name}...")

        # 1. Word Frequency Analysis
        most_common, custom_counts = get_word_frequency(participant_messages, participants)
        analysis_by_participant[name]['most_common_words'] = most_common
        analysis_by_participant[name]['custom_word_counts'] = custom_counts
        print(f"  - Word frequency analysis complete.")

        # 2. Reading Level Analysis
        analysis_by_participant[name]['reading_level'] = get_reading_level(participant_messages)
        print(f"  - Reading level analysis complete.")

        # 3. Sentiment Analysis
        analysis_by_participant[name]['sentiment'] = get_sentiment(participant_messages)
        print(f"  - Sentiment analysis complete.")
        
        # 4. Emoji Analysis
        analysis_by_participant[name]['emoji_usage'] = get_emoji_usage(participant_messages)
        print(f"  - Emoji analysis complete.")

        # 5. New Analysis Parameters
        analysis_by_participant[name]['excuse_factor'] = get_excuse_factor(participant_messages)
        analysis_by_participant[name]['pos_counts'] = get_pos_counts(participant_messages)
        analysis_by_participant[name]['self_pronoun_counts'] = get_self_pronoun_counts(participant_messages)
        print(f"  - New analysis parameters complete.")

    # Run overall analysis
    overall_analysis = {}
    overall_analysis['top_emojis'] = get_overall_emoji_usage(text_messages)
    overall_analysis['chat_initiator'] = get_chat_initiator(text_messages)
    overall_analysis['night_owl_score'] = get_night_owl_score(text_messages, participants)
    overall_analysis['longest_monologues_per_participant'] = get_longest_monologues_per_participant(text_messages, participants)
    overall_analysis['question_askers'] = get_question_askers(text_messages, participants)
    overall_analysis['special_mentions'] = get_special_mentions(text_messages, participants)
    print(f"\nRunning overall analysis...")
    print(f"  - Chat initiator analysis complete.")
    print(f"  - Night owl score analysis complete.")
    print(f"  - Longest monologue analysis complete.")
    print(f"  - Question asker analysis complete.")
    print(f"  - Special mentions analysis complete.")

    # Run inter-participant analysis
    interaction_data = analyze_interactions(text_messages, participants)
    overall_analysis['interaction_analysis'] = interaction_data
    print(f"  - Interaction analysis complete.")

    # Final structure to be saved as JSON
    final_output = {
        'participants': participants,
        'analysis_by_participant': analysis_by_participant,
        'overall_analysis': overall_analysis,
    }

    # Generate inter-participant Christmas greetings
    final_output['inter_participant_christmas_greetings'] = generate_inter_participant_greetings(interaction_data, final_output)
    print(f"  - Christmas greetings generation complete.")

    # Save the results
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_output, f, indent=4)

    print(f"\nAdvanced analysis complete! Results saved to '{output_file}'.")


def get_word_frequency(messages, participants):
    """
    Calculates the most common words and counts of custom words.
    """
    # stop_words are already downloaded in __main__
    stop_words = set(stopwords.words('english'))
    
    # Create a set of lowercase participant names for efficient filtering
    participant_names = set()
    for name in participants:
        for word in name.lower().split():
            participant_names.add(word)

    all_words = []
    for message in messages:
        # Basic cleaning: lowercase, alphanumeric, and remove links
        content = message.get('content', '').lower()
        content = re.sub(r'http\S+', '', content) # remove links
        words = re.findall(r'\b\w+\b', content) # find words
        all_words.extend([word for word in words if word not in stop_words and not word.isdigit() and word not in participant_names and word not in INTERJECTIONS])

    word_counts = Counter(all_words)
    # Get most common words
    most_common = word_counts.most_common(TOP_N_WORDS)

    # Count custom words
    custom_word_counts = {word: word_counts[word] for word in CUSTOM_WORDS_TO_COUNT}
    
    return most_common, custom_word_counts

def get_reading_level(messages):
    """
    Calculates the Flesch-Kincaid Grade Level for all messages from a user.
    Note: Reading level scores are designed for formal text and may be misleading
    when applied to informal chat messages.
    """
    # Concatenate all messages into a single block of text
    full_text = ". ".join([msg.get('content', '') for msg in messages if msg.get('content')])
    
    if not full_text.strip():
        return {
            'grade_level': 0,
            'dale_chall': 0,
            'interpretation': 'No text to analyze.'
        }
        
    grade_level = textstat.flesch_kincaid_grade(full_text)
    dale_chall = textstat.dale_chall_readability_score(full_text)
    
    interp = "College Graduate"
    if grade_level <= 5:
        interp = "5th Grader"
    elif grade_level <= 8:
        interp = "8th Grader"
    elif grade_level <= 12:
        interp = "High School Student"

    return {
        'grade_level': round(grade_level, 2),
        'dale_chall': round(dale_chall, 2),
        'interpretation': interp,
        'age_estimate': round(grade_level + 5)
    }

def get_sentiment(messages):
    """
    Performs sentiment analysis on messages.
    """
    analyzer = SentimentIntensityAnalyzer()
    
    sentiments = {'pos': 0, 'neu': 0, 'neg': 0}
    count = 0
    most_positive_message = {'content': '', 'score': 0}
    most_negative_message = {'content': '', 'score': 0}
    
    for message in messages:
        content = message.get('content', '')
        if content:
            vs = analyzer.polarity_scores(content)
            if vs['compound'] >= 0.05:
                sentiments['pos'] += 1
                if vs['compound'] > most_positive_message['score']:
                    most_positive_message['content'] = content
                    most_positive_message['score'] = vs['compound']
            elif vs['compound'] <= -0.05:
                sentiments['neg'] += 1
                if vs['compound'] < most_negative_message['score']:
                    most_negative_message['content'] = content
                    most_negative_message['score'] = vs['compound']
            else:
                sentiments['neu'] += 1
            count += 1
            
    if count == 0:
        return {
            'positive_percent': 0,
            'neutral_percent': 0,
            'negative_percent': 0,
            'sentiment_examples': {
                'most_positive': 'No messages to analyze.',
                'most_negative': 'No messages to analyze.'
            }
        }

    return {
        'positive_percent': round((sentiments['pos'] / count) * 100, 2),
        'neutral_percent': round((sentiments['neu'] / count) * 100, 2),
        'negative_percent': round((sentiments['neg'] / count) * 100, 2),
        'sentiment_examples': {
            'most_positive': most_positive_message['content'],
            'most_negative': most_negative_message['content']
        }
    }

def get_emoji_usage(messages, top_n=5):
    """
    Finds the most used emojis for a participant.
    """
    all_emojis = []
    for message in messages:
        content = message.get('content', '')
        # The emoji library is great for this
        emojis_in_message = [emj['emoji'] for emj in emoji.emoji_list(content)]
        all_emojis.extend(emojis_in_message)
        
    return Counter(all_emojis).most_common(top_n)

def get_overall_emoji_usage(messages, top_n=5):
    """
    Finds the most used emojis across all messages.
    """
    all_emojis = []
    for message in messages:
        content = message.get('content', '')
        emojis_in_message = [emj['emoji'] for emj in emoji.emoji_list(content)]
        all_emojis.extend(emojis_in_message)
        
    return Counter(all_emojis).most_common(top_n)

def get_excuse_factor(messages):
    """
    Counts the occurrences of excuse words.
    """
    all_words = []
    for message in messages:
        content = message.get('content', '').lower()
        words = re.findall(r'\b\w+\b', content)
        all_words.extend(words)
    
    return {word: all_words.count(word) for word in EXCUSE_WORDS}

def get_pos_counts(messages):
    """
    Counts the occurrences of adjectives, verbs, and nouns.
    Note: Part-of-speech tagging is trained on formal English and may be inaccurate
    on informal chat text.
    """
    pos_counts = {'adjectives': 0, 'verbs': 0, 'nouns': 0}
    for message in messages:
        content = message.get('content', '').lower()
        tokens = nltk.word_tokenize(content)
        tagged = nltk.pos_tag(tokens)
        for word, tag in tagged:
            if tag.startswith('JJ'):
                pos_counts['adjectives'] += 1
            elif tag.startswith('VB'):
                pos_counts['verbs'] += 1
            elif tag.startswith('NN'):
                pos_counts['nouns'] += 1
    return pos_counts

def get_self_pronoun_counts(messages):
    """
    Counts the occurrences of self-pronouns.
    """
    pronoun_counts = {pronoun: 0 for pronoun in SELF_PRONOUNS}
    for message in messages:
        content = message.get('content', '')
        for pronoun in SELF_PRONOUNS:
            pronoun_counts[pronoun] += len(re.findall(r'\b' + re.escape(pronoun) + r'\b', content, re.IGNORECASE))
    return pronoun_counts


def get_chat_initiator(messages, threshold_hours=6):
    """
    Determines who starts the most conversations.
    A new conversation is defined as the first message after a period of inactivity.
    The threshold for inactivity is arbitrary and can be adjusted.
    """
    if not messages:
        return {}
        
    # Sort messages by timestamp
    messages.sort(key=lambda x: x['timestamp_ms'])
    
    initiators = []
    last_timestamp = 0
    
    for msg in messages:
        # Check for sufficient time gap to consider a new conversation
        # Assuming timestamps are in milliseconds
        if (last_timestamp != 0) and ((msg['timestamp_ms'] - last_timestamp) / 1000 / 3600 > threshold_hours):
            initiators.append(msg['sender_name'])
        elif last_timestamp == 0: # First message in the entire chat is always an initiator
            initiators.append(msg['sender_name'])
        last_timestamp = msg['timestamp_ms']
        
    return Counter(initiators).most_common()
    
def get_night_owl_score(messages, participants, night_start=22, night_end=6):
    """
    Counts how many messages each participant sends late at night.
    """
    night_owl_counts = {name: 0 for name in participants}
    for msg in messages:
        # timestamp_ms is in milliseconds, so divide by 1000
        dt_object = datetime.fromtimestamp(msg['timestamp_ms'] / 1000)
        if dt_object.hour >= night_start or dt_object.hour < night_end:
            night_owl_counts[msg['sender_name']] += 1
    
    return sorted(night_owl_counts.items(), key=lambda item: item[1], reverse=True)

def get_longest_monologues_per_participant(messages, participants):
    """
    Finds the longest streak of consecutive messages for each participant.
    """
    longest_monologues = {p: {'author': p, 'message_count': 0, 'monologue_content': [], 'start_time': None, 'end_time': None, 'message_intervals_seconds': []} for p in participants}

    if not messages:
        return longest_monologues

    current_run = 0
    current_author = None
    current_monologue_messages = [] # This will now store full message objects

    # Sort messages by timestamp to ensure consecutive messages are correctly identified
    messages.sort(key=lambda x: x.get('timestamp_ms', 0))

    for msg in messages:
        sender = msg.get('sender_name')
        
        if sender == current_author:
            current_run += 1
            current_monologue_messages.append(msg)
        else:
            # The monologue has been broken. Check if the previous one was a record for that author.
            if current_author is not None and current_run > longest_monologues.get(current_author, {}).get('message_count', 0):
                start_ts = current_monologue_messages[0]['timestamp_ms'] / 1000
                end_ts = current_monologue_messages[-1]['timestamp_ms'] / 1000
                start_time = datetime.fromtimestamp(start_ts).strftime('%Y-%m-%d %H:%M:%S')
                end_time = datetime.fromtimestamp(end_ts).strftime('%Y-%m-%d %H:%M:%S')
                
                intervals = []
                for i in range(1, len(current_monologue_messages)):
                    interval = (current_monologue_messages[i]['timestamp_ms'] - current_monologue_messages[i-1]['timestamp_ms']) / 1000
                    intervals.append(round(interval, 2))

                longest_monologues[current_author] = {
                    'author': current_author,
                    'message_count': current_run,
                    'monologue_content': [m.get('content', '') for m in current_monologue_messages],
                    'start_time': start_time,
                    'end_time': end_time,
                    'message_intervals_seconds': intervals
                }

            # Start a new monologue
            current_author = sender
            current_run = 1
            current_monologue_messages = [msg]

    # Check the very last monologue in the chat
    if current_author is not None and current_run > longest_monologues.get(current_author, {}).get('message_count', 0):
        start_ts = current_monologue_messages[0]['timestamp_ms'] / 1000
        end_ts = current_monologue_messages[-1]['timestamp_ms'] / 1000
        start_time = datetime.fromtimestamp(start_ts).strftime('%Y-%m-%d %H:%M:%S')
        end_time = datetime.fromtimestamp(end_ts).strftime('%Y-%m-%d %H:%M:%S')

        intervals = []
        for i in range(1, len(current_monologue_messages)):
            interval = (current_monologue_messages[i]['timestamp_ms'] - current_monologue_messages[i-1]['timestamp_ms']) / 1000
            intervals.append(round(interval, 2))
        
        longest_monologues[current_author] = {
            'author': current_author,
            'message_count': current_run,
            'monologue_content': [m.get('content', '') for m in current_monologue_messages],
            'start_time': start_time,
            'end_time': end_time,
            'message_intervals_seconds': intervals
        }

    # Sort the results by message count in descending order
    sorted_monologues = sorted(longest_monologues.values(), key=lambda x: x['message_count'], reverse=True)
    
    return {item['author']: item for item in sorted_monologues if item['author'] is not None}

def get_question_askers(messages, participants):
    """
    Counts how many questions each participant asks.
    """
    question_counts = {name: 0 for name in participants}
    for msg in messages:
        content = msg.get('content', '')
        if content and '?' in content:
            question_counts[msg['sender_name']] += 1
            
    return sorted(question_counts.items(), key=lambda item: item[1], reverse=True)

def get_special_mentions(messages, participants):
    """
    Counts how many times each participant is mentioned.
    """
    mention_counts = {name: 0 for name in participants}
    
    # Create a regex pattern to match any of the participant names preceded by an @
    # This is more robust than simple string checking.
    # We use word boundaries to avoid matching parts of names.
    participant_regex = r'(?<!\w)@(' + '|'.join(re.escape(p) for p in participants) + r')\b'
    mention_pattern = re.compile(participant_regex, re.IGNORECASE)

    for msg in messages:
        content = msg.get('content', '')
        if content and '@' in content:
            mentions = mention_pattern.findall(content)
            for mention in mentions:
                # Find the full name that matches the mention
                for participant in participants:
                    if participant.lower() == mention.lower():
                        mention_counts[participant] += 1
                        break
            
    return sorted(mention_counts.items(), key=lambda item: item[1], reverse=True)





def analyze_interactions(messages, participants):


    """


    Analyzes interactions between each pair of participants based on @mentions.


    """


    # Initialize a structure to hold raw messages for each interaction pair


    interaction_messages = {sender: {receiver: [] for receiver in participants if sender != receiver} for sender in participants}





    # Regex to find mentions of any participant


    # This is a complex regex to avoid matching names that are substrings of other names


    # and to ensure we're matching a mention that is likely a standalone word.


    participant_regex = r'@(' + '|'.join(re.escape(p.split()[0]) for p in sorted(participants, key=len, reverse=True)) + r')'


    mention_pattern = re.compile(participant_regex, re.IGNORECASE)


    


    # First pass: collect all messages from a sender that mention a receiver


    for msg in messages:


        sender = msg['sender_name']


        content = msg.get('content', '')


        


        # Find all unique mentions in the message


        mentions_found = set(mention_pattern.findall(content))


        


        for mention in mentions_found:


            # Find the full participant name that matches the mentioned first name


            for receiver in participants:


                if sender != receiver and receiver.lower().startswith(mention.lower()):


                    interaction_messages[sender][receiver].append(msg)


                    break # Assume first match is the correct one





    # Second pass: compute statistics for each interaction pair


    interaction_analysis = {sender: {receiver: {} for receiver in participants if sender != receiver} for sender in participants}


    for sender, receivers in interaction_messages.items():


        for receiver, specific_messages in receivers.items():


            if not specific_messages:


                interaction_analysis[sender][receiver] = {


                    'message_count': 0,


                    'sentiment': {'pos': 0, 'neu': 0, 'neg': 0},


                    'emojis': [],


                    'common_words': []


                }


                continue





            # Calculate sentiment, emojis, and common words for this specific interaction


            interaction_analysis[sender][receiver] = {


                'message_count': len(specific_messages),


                'sentiment': get_sentiment(specific_messages),


                'emojis': get_emoji_usage(specific_messages, top_n=3),


                'common_words': get_word_frequency(specific_messages, participants)[0][:5]


            }


            


    return interaction_analysis





def generate_inter_participant_greetings(interaction_data, individual_data):


    """


    Generates personalized Christmas greetings from each participant to every other participant.


    """


    greetings = {sender: {receiver: {} for receiver in individual_data['participants'] if sender != receiver} for sender in individual_data['participants']}


    


    for sender, receivers in interaction_data.items():


        for receiver, interaction in receivers.items():


            sender_profile = individual_data['analysis_by_participant'][sender]


            


            # --- Gift Logic ---


            gift = "A Pair of Cozy Socks" # Default


            if interaction['message_count'] == 0:


                gift = "A 'Thinking of You' Card (since we don't talk much!)"


            elif interaction.get('sentiment', {}).get('positive_percent', 0) > 80:


                gift = f"A Framed Photo of You and {sender}"


            elif interaction.get('sentiment', {}).get('negative_percent', 0) > 50:


                gift = "A Boxing Glove (for our next debate)"


            elif sender_profile.get('reading_level', {}).get('grade_level', 0) > 12:


                gift = "A Book Recommendation"


            


            # --- Greeting & Blessing Logic ---


            greeting = f"Merry Christmas, {receiver.split()[0]}!"


            blessing = "Wishing you all the best this holiday season."





            # If sender is very positive in general


            if sender_profile.get('sentiment', {}).get('positive_percent', 0) > 70:


                greeting += " Hope you have a wonderful time! 🎄"


                blessing = "May your Christmas sparkle with moments of love, laughter, and goodwill!"


            


            # If sender is very positive specifically towards the receiver


            if interaction.get('sentiment', {}).get('positive_percent', 0) > 70:


                emojis_to_receiver = ''.join([e[0] for e in interaction.get('emojis', [])])


                greeting = f"To my dear {receiver.split()[0]}, Merry Christmas! {emojis_to_receiver}"


                blessing = "So grateful for you this holiday season! Hope you have the best time."





            greetings[sender][receiver] = {


                'greeting': greeting,


                'blessing': blessing,


                'gift': gift


            }


            


    return greetings





if __name__ == '__main__':


    parser = argparse.ArgumentParser(description='Run advanced analysis on chat messages.')


    parser.add_argument('-i', '--input', default='filtered_messages.json', help='Input JSON file')


    parser.add_argument('-o', '--output', default='advanced_analysis.json', help='Output JSON file')


    args = parser.parse_args()





    # Download NLTK data if not already present


    try:


        nltk.data.find('corpora/vader_lexicon')


    except LookupError:


        print("Downloading NLTK VADER lexicon...")


        nltk.download('vader_lexicon')


    


    try:


        nltk.data.find('corpora/stopwords')


    except LookupError:


        print("Downloading NLTK stopwords...")


        nltk.download('stopwords')





    try:


        nltk.data.find('taggers/averaged_perceptron_tagger')


    except LookupError:


        print("Downloading NLTK averaged_perceptron_tagger...")


        nltk.download('averaged_perceptron_tagger')


    


    try:


        nltk.data.find('tokenizers/punkt')


    except LookupError:


        print("Downloading NLTK punkt tokenizer...")


        nltk.download('punkt')





    analyze_messages(args.input, args.output)

