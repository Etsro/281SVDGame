from flask import Flask, render_template, request, redirect, url_for, session
import numpy as np
import cv2
import os
import random
import matplotlib.pyplot as plt
import uuid
import time

app = Flask(__name__)
app.secret_key = 'change_this_to_something_secure'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # prevent image caching

# Set of images
images = {
    "dog": "Doge.jpg",
    "cat": "Cat.jpg"
}

# Word list
word = """
the day was new and full of sun i got up from my bed pulled the rug back and placed my foot on the mat the cup i left near the pad was still warm my pen sat by the box right next to a tiny toy and an old cap it was time to pack my bag

i took a map and a tag id used on my last trip i checked the zip on my bin and dropped in a tin of wax i saw a bug crawl near the net by the tub my cat sat on the ledge tail twitching next to a big pot and a dusty jar she looked at me like she knew my plan

my dog wagged his tail at a man and ran past a hen that flew up as a fly buzzed near a bee by the rag i grabbed my hat and my kit the rod by the door fell so i used it to push the mop back into place a fan hummed above the pit where i kept old tools a saw an axe a cog a peg the rim of the can was bent but it still held gas i tapped the lid twice to be sure

outside the fog was low a van passed by a cab both stuck behind a big red bus i climbed into my car and placed a bun and a fig in the side pod i tapped my toe and turned the key the hum of the jet above made me glance up

on the road i saw a fox dash across the tar chasing a rat near a bin a guy waved at me from his hub he wore a wig and had an old arm band with a gem on it the dam down the way still leaked near the ash pit

at the lab i saw a dot on the screen a bug in the code i tapped my pen and took notes on a pad my boss came by with a jug of tea he wore a vest with a bow and a tiny pin he gave me a nod and a bun big day he said i gave a weak smile

we met in the main room with a cog chart on the wall the orb above the lab table gave off a soft glow i passed a nut to a pal and dropped oil in a pan he used a pip and a peg to hold it in place

later i saw a box of dye spill on a rag the mess hit the log book and stained a bag i cleaned it with a mop and a bit of soap the tap ran hot we laughed as a cat jumped onto the top shelf knocking a pan and a toy down into a bin

back home i set the jar down then pulled off my cap the tub filled up as the fan spun i placed a lid over the pot to keep it warm my cat again leapt into my lap she purred as i rubbed her leg she loves man

my dog slept by the door as the hen clucked in the yard a fly buzzed past the open window while a bee sat on a flower near the mat in the den i placed a bun on a tray and sipped from a cup i flipped through a mag and saw a wig ad i remembered my pal from the van i picked up my pen and wrote a few lines the ink ran low so i grabbed a new one from the bag

the bed looked so good i dropped onto it pulling the rug over my toe and letting the fog roll in through the open tap a fig sat on the stand next to a peg and a pad the box was full of gear tools toys and even a saw id used once to fix a rod

i felt at peace the map on the wall the bar i built with logs the nut jar in the orb light they all made it feel like home i set the fan to low checked the net once more and turned off the light just before sleep i thought of that cat and her leap
"""
wordList = word.split()

# Semantic difference function
def SemanticDif(w1, w2, wordList):
    if w1 not in wordList or w2 not in wordList:
        return "[Word Not Included]"
    w1_indices = [i for i, word in enumerate(wordList) if word == w1]
    w2_indices = [i for i, word in enumerate(wordList) if word == w2]
    if not w1_indices or not w2_indices:
        return "[Word Not Included]"
    diffs = [abs(i - min(w2_indices, key=lambda x: abs(x - i))) for i in w1_indices]
    return round(np.mean(diffs), 2)

# SVD image blur
def apply_svd(image_path, n, output_path):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    U, S, Vt = np.linalg.svd(img, full_matrices=False)
    reconstructed = np.dot(U[:, :n], np.dot(np.diag(S[:n]), Vt[:n, :]))
    plt.imsave(output_path, reconstructed, cmap='gray')

@app.route('/')
def index():
    # Start new game if needed
    if 'answer' not in session:
        answer, image = random.choice(list(images.items()))
        session['answer'] = answer
        session['image'] = image
        session['guesses'] = 0
        session['id'] = str(uuid.uuid4())

    # Generate image for current guess
    image_path = f"static/images/{session['image']}"
    guess_num = session['guesses']
    n = max(1, (guess_num + 1) ** 2)
    output_filename = f"{session['id']}_guess{guess_num}.png"
    output_path = f"static/temp/{output_filename}"
    apply_svd(image_path, n, output_path)

    return render_template('index.html',
                           image=f"temp/{output_filename}",
                           guess_count=guess_num,
                           max_guesses=30,
                           error=None,
                           timestamp=int(time.time()))

@app.route('/guess', methods=['POST'])
def guess():
    guess = request.form['guess'].strip().lower()
    session['guesses'] += 1

    if guess == session['answer']:
        return render_template('result.html',
                               correct=True,
                               image=f"images/{session['image']}",
                               answer=session['answer'])

    if session['guesses'] >= 30:
        return render_template('result.html',
                               correct=False,
                               image=f"images/{session['image']}",
                               answer=session['answer'],
                               finished=True)

    # Regenerate updated image for next round
    image_path = f"static/images/{session['image']}"
    n = max(1, (session['guesses']) ** 2)
    output_filename = f"{session['id']}_guess{session['guesses']}.png"
    output_path = f"static/temp/{output_filename}"
    apply_svd(image_path, n, output_path)

    diff = SemanticDif(guess, session['answer'], wordList)

    return render_template('index.html',
                           image=f"temp/{output_filename}",
                           guess_count=session['guesses'],
                           max_guesses=30,
                           n=n,
                           error=f"'{guess}' is {diff} away from the correct word.",
                           timestamp=int(time.time()))

@app.route('/reset')
def reset():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    os.makedirs('static/temp', exist_ok=True)
    app.run(host='0.0.0.0', port=81)
