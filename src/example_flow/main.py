#!/usr/bin/env python
from random import randint

from pydantic import BaseModel

from crewai.flow.flow import Flow, listen, start

from example_flow.crews.poem_crew.poem_crew import PoemCrew
from example_flow.crews.image_crew.image_crew import ImageCrew
from example_flow.crews.dale_crew.dale_crew import DaleCrew


class PoemState(BaseModel):
    sentence_count: int = 1
    poem: str = ""
    image_description: str = ""


class PoemFlow(Flow[PoemState]):
    @start()
    def generate_sentence_count(self):
        print("Generating sentence count")
        self.state.sentence_count = randint(3, 5)

    @listen(generate_sentence_count)
    def generate_poem(self):
        print("Generating poem")
        result = (
            PoemCrew()
            .crew()
            .kickoff(inputs={"sentence_count": self.state.sentence_count})
        )

        print("Poem generated", result.raw)
        self.state.poem = result.raw

    @listen(generate_poem)
    def save_poem(self):
        print("Saving poem")
        with open("poem.txt", "w") as f:
            f.write(self.state.poem)

    @listen(generate_poem)
    def generate_image_description(self):
        print("Generating image description")
        description = ImageCrew().crew().kickoff(inputs={"poem": self.state.poem})
        print("Image description generated", description.raw)
        self.state.image_description = description.raw

    @listen(generate_image_description)
    def save_image_description(self):
        print("Saving image description")
        with open("image_description.txt", "w") as f:
            f.write(self.state.image_description)

    # Generate Image using DALE
    @listen(generate_image_description)
    def generate_image(self):
        print("Generating image")
        image = (
            DaleCrew()
            .crew()
            .kickoff(inputs={"description": self.state.image_description})
        )
        print("Image generated")
        with open("image.txt", "w") as f:
            f.write(image.raw)


def kickoff():
    poem_flow = PoemFlow()
    poem_flow.kickoff()
    poem_flow.plot("my_plot_flow")


if __name__ == "__main__":
    kickoff()
