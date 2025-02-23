import nltk
import pickle
import numpy as np
import json
import random
from nltk.stem import WordNetLemmatizer
from tensorflow.keras.models import load_model

class TherapistChatbot:
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        self.intents = json.loads(open('myapp/chatbot_model/intents.json').read())
        self.words = pickle.load(open('myapp/chatbot_model/words.pkl', 'rb'))
        self.classes = pickle.load(open('myapp/chatbot_model/classes.pkl', 'rb'))
        self.model = load_model('myapp/chatbot_model/chatbot_model.h5')

    def clean_up_sentence(self, sentence):
        sentence_words = nltk.word_tokenize(sentence)
        sentence_words = [self.lemmatizer.lemmatize(word.lower()) for word in sentence_words]
        return sentence_words

    def bag_of_words(self, sentence):
        sentence_words = self.clean_up_sentence(sentence)
        bag = [0] * len(self.words)
        for w in sentence_words:
            for i, word in enumerate(self.words):
                if word == w:
                    bag[i] = 1
        return np.array(bag)

    def predict_class(self, sentence):
        bow = self.bag_of_words(sentence)
        res = self.model.predict(np.array([bow]))[0]
        ERROR_THRESHOLD = 0.25
        results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
        results.sort(key=lambda x: x[1], reverse=True)
        return_list = []
        for r in results:
            return_list.append({'intent': self.classes[r[0]], 'probability': str(r[1])})
        return return_list

    def get_response(self, message):
        ints = self.predict_class(message)
        if not ints:
            return "I'm not sure how to respond to that. Could you rephrase or ask something else?"
        
        tag = ints[0]['intent']
        list_of_intents = self.intents['intents']
        
        for i in list_of_intents:
            if i['tag'] == tag:
                return random.choice(i['responses'])
