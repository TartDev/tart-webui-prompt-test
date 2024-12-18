prompt = """
Based on the user's input "{user_input}", and the user's answer to the form question "{survey_questions}" , the user's answer to the form "{user_answers}" analysis of the user's interest in art and his current mood, 
the output must be in JSON format {{"art_interest": "xxx", "mood": "xxx","summary":"xxx"}}
1. Only JSON format output, no additional text
2. Artistic interest is the user's interest in the work of Art
3. Emotion is the user's current emotion, in sadness, depression, calm, cheerful choice
4. summary summarizes the user's current mood and interests, output a user is most likely to search the social network query
5. Based primarily on user input, rather than background information, user input largely reflects the current mood.
"""