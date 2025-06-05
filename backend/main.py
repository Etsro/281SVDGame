from flask_cors import CORS
from flask import Flask, request, session, send_from_directory, jsonify
import numpy as np
import cv2
import os
import random
import matplotlib.pyplot as plt
import uuid

app = Flask(__name__)
app.secret_key = 'change_this_to_something_secure'
CORS(app) 

images = {
    "dog": "Doge.jpg",
    "cat": "Cat.jpg",
    "bee": "Bee.jpg",
    "van": "Van.jpg",
    "ng": "Ng.jpeg",
    "sun": "Sun.png",
    "nut": "Nut.jpg",
    "car": "Car.jpg",
    "log": "Log.jpg",
    "man": "Man.jpg",
    "fox": "Fox.jpg",
    "jet": "Jet.jpg",
}

with open("wordlist.txt", "r") as f:
    wordList = f.read().split()

@app.route("/image/<filename>")
def image(filename):
    return send_from_directory("static/temp", filename)

@app.route("/")
def new_game():
    answer, image = random.choice(list(images.items()))
    session.clear()
    session['answer'] = answer
    session['image'] = image
    session['guesses'] = 0
    session['id'] = str(uuid.uuid4())
    n = 1
    file = generate_image(image, n, session['id'], 0)
    return jsonify({"image": file, "guess_count": 0, "max_guesses": 30})

def generate_image(img_name, n, uid, guess_num):
    img_path = f"static/images/{img_name}"
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    U, S, Vt = np.linalg.svd(img, full_matrices=False)
    rec = np.dot(U[:, :n], np.dot(np.diag(S[:n]), Vt[:n, :]))
    os.makedirs("static/temp", exist_ok=True)
    outname = f"{uid}_g{guess_num}.png"
    plt.imsave(f"static/temp/{outname}", rec, cmap='gray')
    return outname

def semantic_diff(w1, w2):
    if w1 not in wordList or w2 not in wordList:
        return -1
    i1 = [i for i, w in enumerate(wordList) if w == w1]
    i2 = [i for i, w in enumerate(wordList) if w == w2]
    return round(np.mean([abs(i - min(i2, key=lambda x: abs(x - i))) for i in i1]), 2)

@app.route("/guess", methods=["POST"])
def guess():
    data = request.get_json()
    user_guess = data.get("guess", "").strip().lower()
    session['guesses'] += 1
    n = (session['guesses']) ** 2
    file = generate_image(session['image'], n, session['id'], session['guesses'])
    correct = user_guess == session['answer']
    finished = session['guesses'] >= 30
    diff = semantic_diff(user_guess, session['answer'])
    return jsonify({
        "image": file,
        "correct": correct,
        "finished": finished,
        "guess_count": session['guesses'],
        "max_guesses": 30,
        "diff": diff,
        "answer": session['answer'] if correct or finished else None
    })

@app.route("/reset")
def reset():
    return new_game()

