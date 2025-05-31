import nltk
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
import pickle
import numpy as np
from gtts import gTTS
import os

from keras.models import load_model
model = load_model('Chatbot/chatbot_model(N).h5')
import json
import random
from googletrans import Translator
import pyttsx3
from pygame import mixer
import os


intents = json.loads(open('Chatbot/intents.json', encoding='utf-8').read())
words = pickle.load(open('Chatbot/words(N).pkl','rb'))
classes = pickle.load(open('Chatbot/classes(N).pkl','rb'))




def clean_up_sentence(sentence, source_lang='en', target_lang='en'):
    translator = Translator()
    translation = translator.translate(sentence, src=source_lang, dest=target_lang).text
    sentence_words = nltk.word_tokenize(translation)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    print("This is the input text ",sentence_words)
    print(type(sentence_words))
    return sentence_words



# return bag of words array: 0 or 1 for each word in the bag that exists in the sentence

def bow(sentence, words, show_details=True):
    # tokenize the pattern
    sentence_words = clean_up_sentence(sentence)
    # bag of words - matrix of N words, vocabulary matrix
    bag = [0]*len(words)
    for s in sentence_words:
        for i,w in enumerate(words):
            if w == s:
                # assign 1 if current word is in the vocabulary position
                bag[i] = 1
                if show_details:
                    print ("found in bag: %s" % w)
    return(np.array(bag))

def predict_class(sentence, model):
    # filter out predictions below a threshold
    p = bow(sentence, words, show_details=False)
    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i,r] for i,r in enumerate(res) if r>ERROR_THRESHOLD]
    # sort by strength of probability
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    return return_list





# def getResponse(ints, intents_json, source_lang='en', target_lang='te'):
#     tag = ints[0]['intent']
#     list_of_intents = intents_json['intents']
#     translator = Translator()
#     engine = pyttsx3.init()
    
#     for i in list_of_intents:
#         if(i['tag']== tag):
#             result = random.choice(i['responses'])
#             translation = translator.translate(result, src=source_lang, dest=target_lang).text
#             tts = gTTS(text=translation, lang=target_lang)
#             result = tts
#             result.save("G:/JAYASURYA/NEW OWN IN 2023/POSSIBILITIES/VOICE COMMAND SYSTEM/ITPCB01 - FINAL CODING/DEPLOY/Responses/response.mp3")
    
            
#             path = "G:/JAYASURYA/NEW OWN IN 2023/POSSIBILITIES/VOICE COMMAND SYSTEM/ITPCB01 - FINAL CODING/DEPLOY/Responses/response.mp3"
#             mixer.init()  # Initialize mixer
#             mixer.music.load(path)  # Load the file
#             mixer.music.play()
#         else:
#             result = "You must ask the right questions"
            
#     return result


def getResponse(ints, intents_json, source_lang='en', target_lang='en', save_path="C:/Users/DELL/OneDrive/Desktop/project2/ITPML37-FINAL CODING/Deployment/Responses/response.mp3"):
    tag = ints[0]['intent']
    list_of_intents = intents_json['intents']
    translator = Translator()
    for i in list_of_intents:
        if i['tag'] == tag:
            result = random.choice(i['responses'])
            translation = translator.translate(result, src=source_lang, dest=target_lang).text
            result = translation
            tts = gTTS(text=result, lang=target_lang)
            results = tts
            results.save(save_path)
            mixer.init()  # Initialize mixer
            sound = mixer.Sound(save_path)  # Load the file
            sound.play()
            return result  # Return the path after saving and playing
        else:
            result = "You must ask the right questions"

    return result

def chatbot_response(msg):
    ints = predict_class(msg, model)
    res = getResponse(ints, intents)
    return res
