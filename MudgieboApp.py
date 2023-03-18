import os
import openai
import requests
import shutil
import tempfile
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.loader import Loader
from PIL import Image as PilImage
from io import BytesIO

# get the users api key
openai.api_key = os.environ["OPENAI_API_KEY"]

class ImageGeneratorApp(App):

    def build(self):
        self.title = "Image Generator"
        root = BoxLayout(orientation="vertical", padding=10, spacing=10)

        # Prompt entry
        prompt_label = Label(text="Enter your prompt:")
        root.add_widget(prompt_label)

        self.prompt_entry = TextInput(hint_text="Your prompt here...", multiline=True, size_hint_y=None, height=100)
        root.add_widget(self.prompt_entry)

        # Generate button
        generate_button = Button(text="Generate Image", on_press=self.generate_image)
        root.add_widget(generate_button)

        # Status label
        self.status_label = Label(text="", size_hint_y=None, height=20)
        root.add_widget(self.status_label)

        # Image
        self.image_widget = Image(size_hint=(1, None), height=655)
        root.add_widget(self.image_widget)

        # Quit button
        quit_button = Button(text="Quit", on_press=lambda _: Window.close())
        root.add_widget(quit_button)

        return root

    def generate_image(self, _):
        MyPrompt = self.prompt_entry.text.strip()

        response = openai.Image.create(
            prompt=MyPrompt, n=1, size="1024x1024"
        )

        image_url = response['data'][0]['url']
        response = requests.get(image_url, stream=True)

        filename = "".join(
            c for c in MyPrompt if c.isalnum() or c in (' ', '_')
        ).rstrip() + ".png"

        with open(filename, "wb") as file:
            shutil.copyfileobj(response.raw, file)

        self.status_label.text = f"Image saved as {filename}"

        # Display the image
        self.display_image(filename)

    def display_image(self, filename):
        # Open the image using PIL
        image = PilImage.open(filename)

        # Resize the image to fit the widget
        max_size = (self.image_widget.width, self.image_widget.height)
        image.thumbnail(max_size, resample=PilImage.LANCZOS)

        # Save the resized image to a temporary file
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp:
            image.save(temp, format="png")
            temp_path = temp.name

        # Load the temporary file into the Kivy Image widget
        self.image_widget.source = temp_path
        self.image_widget.reload()

if __name__ == '__main__':
    ImageGeneratorApp().run()
