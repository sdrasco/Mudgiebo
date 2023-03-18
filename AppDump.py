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
from kivy.core.window import Window
from PIL import Image as PilImage
from io import BytesIO

# Set the API key
openai.api_key = os.environ["OPENAI_API_KEY"]

class ImageGeneratorApp(App):

    def build(self):
        # Create root widget
        self.title = "Mudgiebo Image Generator"
        root = BoxLayout(orientation="vertical", padding=10, spacing=10)

        # Add widgets in a more modular way
        #root.add_widget(Label(text="Image description"))
        root.add_widget(self.create_prompt_entry())
        root.add_widget(Button(text="Generate Image", on_press=self.generate_image))
        root.add_widget(self.create_status_label())
        root.add_widget(self.create_image_widget())
        root.add_widget(Button(text="Quit", on_press=lambda _: Window.close()))

        return root

    def create_prompt_entry(self):
        self.prompt_entry = TextInput(hint_text="Tell me about the image that you want to create ...", multiline=True, size_hint_y=None, height=100)
        return self.prompt_entry

    def create_status_label(self):
        self.status_label = Label(text="", size_hint_y=None, height=20)
        return self.status_label

    def create_image_widget(self):
        self.image_widget = Image(size_hint=(1, None), height=655)
        return self.image_widget

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
