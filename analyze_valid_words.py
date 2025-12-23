import json
import re
import argparse
import nltk
from collections import Counter

# Words to explicitly exclude from the analysis, as they are often meta-commentary on the chat itself.
CUSTOM_EXCLUDE_WORDS = {'message', 'reacted', 'sent', 'photo', 'video', 'audio'}

def analyze_valid_words_by_pos(input_file, output_file):
    """
    Analyzes messages to find the top 5 most common nouns, verbs, and adjectives
    for each participant.
    """
    print("Starting valid word analysis by Part-of-Speech...")

    # --- Setup: Load data and dictionaries ---
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            messages = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: Input file not found at '{input_file}'. Please make sure it exists.")
        return
    except json.JSONDecodeError:
        print(f"ERROR: Could not decode JSON from '{input_file}'. The file might be corrupted.")
        return

    try:
        english_words = set(nltk.corpus.words.words())
        stopwords = set(nltk.corpus.stopwords.words('english'))
    except Exception as e:
        print(f"ERROR: Could not load NLTK data. Please ensure it's downloaded. Details: {e}")
        return
        
    # --- Analysis ---
    
    participants = sorted(list(set(msg['sender_name'] for msg in messages)))
    final_analysis = {}

    # Create a set of all words that make up participant names to exclude them
    participant_name_words = set()
    for name in participants:
        for word in name.lower().split():
            participant_name_words.add(word)
    
    # Combine custom exclusions with participant names
    exclusion_list = CUSTOM_EXCLUDE_WORDS.union(participant_name_words)

    print(f"Found {len(messages)} messages from {len(participants)} participants.")
    print(f"Excluding the following words from analysis: {sorted(list(exclusion_list))}")

    for name in participants:
        participant_messages = [msg for msg in messages if msg['sender_name'] == name]
        
        all_words = []
        for message in participant_messages:
            content = message.get('content', '').lower()
            content = re.sub(r'http\S+', '', content)
            words = re.findall(r'\b[a-z]{3,}\b', content)
            all_words.extend(words)

        # Filter for valid, non-stopword, non-excluded English words
        valid_words = [
            word for word in all_words 
            if word in english_words 
            and word not in stopwords 
            and word not in exclusion_list
        ]
        
        # Part-of-Speech (POS) tagging
        tagged_words = nltk.pos_tag(valid_words)
        
        # Categorize words by POS
        nouns = [word for word, tag in tagged_words if tag.startswith('NN')]
        adjectives = [word for word, tag in tagged_words if tag.startswith('JJ')]
        verbs = [word for word, tag in tagged_words if tag.startswith('VB')]
        
        # Count the frequency for each category and get the top 5
        top_5_nouns = Counter(nouns).most_common(5)
        top_5_adjectives = Counter(adjectives).most_common(5)
        top_5_verbs = Counter(verbs).most_common(5)

        # Find the longest valid word used by the participant
        longest_word = max(valid_words, key=len) if valid_words else ""
        
        final_analysis[name] = {
            "nouns": top_5_nouns,
            "adjectives": top_5_adjectives,
            "verbs": top_5_verbs,
            "longest_word": longest_word
        }
        
        print(f"  - Analyzed words for {name}. Longest word: '{longest_word}'")

    # --- Save Results ---
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_analysis, f, indent=4)

    print(f"\nValid word analysis complete! Results saved to '{output_file}'.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Analyze messages for the most common valid English words per participant, categorized by part of speech.'
    )
    parser.add_argument(
        '-i', '--input', 
        default='filtered_messages.json',
        help='Input JSON file containing messages (default: filtered_messages.json)'
    )
    parser.add_argument(
        '-o', '--output', 
        default='valid_word_analysis_by_pos.json',
        help='Output JSON file for the analysis results (default: valid_word_analysis_by_pos.json)'
    )
    args = parser.parse_args()

    # --- Download NLTK data if not already present ---
    print("Checking for NLTK data...")
    required_corpora = ['words', 'stopwords', 'averaged_perceptron_tagger', 'punkt']
    for corpus in required_corpora:
        try:
            nltk.data.find(f'corpora/{corpus}')
        except LookupError:
            print(f"Downloading NLTK '{corpus}' corpus...")
            nltk.download(corpus)
        # The tagger and tokenizer have a different path structure
        if corpus in ['averaged_perceptron_tagger', 'punkt']:
             try:
                nltk.data.find(f'taggers/{corpus}')
             except LookupError:
                print(f"Downloading NLTK '{corpus}'...")
                nltk.download(corpus)


    print("NLTK data is ready.")

    # Run the analysis
    analyze_valid_words_by_pos(args.input, args.output)
