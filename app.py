from flask import Flask, render_template, request, redirect, url_for
import os
import random
import matplotlib.pyplot as plt
from PIL import Image, ImageFilter
import io
import base64
import pydub
from pydub.playback import play

# Flask app setup
app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Classes for generative art
class Shape:
    def __init__(self, color):
        self.color = color

    def draw(self):
        pass

class Circle(Shape):
    def __init__(self, x, y, radius, color):
        super().__init__(color)
        self.x = x
        self.y = y
        self.radius = radius

    def draw(self):
        return plt.Circle((self.x, self.y), self.radius, color=self.color)

class Square(Shape):
    def __init__(self, x, y, size, color):
        super().__init__(color)
        self.x = x
        self.y = y
        self.size = size

    def draw(self):
        return plt.Rectangle((self.x, self.y), self.size, self.size, color=self.color)

# Function to generate art
def generate_art():
    plt.figure(figsize=(5, 5))
    shapes = []
    for _ in range(20):
        shape_type = random.choice(['circle', 'square'])
        color = [random.random() for _ in range(3)]
        if shape_type == 'circle':
            shape = Circle(random.random(), random.random(), 0.1, color)
        else:
            shape = Square(random.random() - 0.05, random.random() - 0.05, 0.1, color)
        shapes.append(shape)
        plt.gca().add_artist(shape.draw())
    plt.axis('off')
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()
    buffer.seek(0)
    img_str = base64.b64encode(buffer.read()).decode('utf-8')
    return img_str

# Function to manipulate audio
def manipulate_audio(file_path):
    audio = pydub.AudioSegment.from_file(file_path)
    audio = audio.reverse()  # Reverse the audio
    output_path = os.path.join(UPLOAD_FOLDER, 'manipulated_audio.wav')
    audio.export(output_path, format="wav")
    return output_path

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generative-art')
def generative_art():
    art_image = generate_art()
    return render_template('generative_art.html', art_image=art_image)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            if file.filename.endswith(('.png', '.jpg', '.jpeg')):
                img = Image.open(filepath).filter(ImageFilter.CONTOUR)
                buffer = io.BytesIO()
                img.save(buffer, format="PNG")
                buffer.seek(0)
                img_str = base64.b64encode(buffer.read()).decode('utf-8')
                return render_template('upload.html', img_str=img_str)
            elif file.filename.endswith('.wav'):
                output_path = manipulate_audio(filepath)
                return f"Audio manipulated and saved at {output_path}"
    return render_template('upload.html')

@app.route('/data-visualization')
def data_visualization():
    data = [random.randint(1, 100) for _ in range(10)]
    plt.bar(range(len(data)), data, color=['r', 'g', 'b', 'y', 'c'] * 2)
    plt.title("Random Data Visualization")
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()
    buffer.seek(0)
    img_str = base64.b64encode(buffer.read()).decode('utf-8')
    return render_template('data_visualization.html', img_str=img_str)

# Main
if __name__ == '__main__':
    app.run(debug=True)

