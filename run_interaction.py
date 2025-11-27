from app.models import Vector, CubeDimensions, GridPositions
from space_timer import SpaceTimer
from voice import Voice, Guide
from time import sleep
import requests

class Interactions:
    vectors: dict[str, Vector] = []
    base_path = 'http://localhost:8000/get'
    dimensions = ['i', 'j', 'k'] 
    space_timer = SpaceTimer()
    voice = Voice()
    guide = Guide()

    def check_vectors(self, v1, v2) -> bool:
        shared_dimensions = []
        v1_dimensions = [v1.cube.horizontal, v1.cube.vertical]
        print(v1_dimensions + [v2.cube.horizontal, v2.cube.vertical])
        if v2.cube.horizontal in v1_dimensions:
            shared_dimensions.append(v2.cube.horizontal)
        if v2.cube.vertical in v1_dimensions:
            shared_dimensions.append(v2.cube.vertical)

        if len(shared_dimensions) > 1:
            message = self.voice.messages.get("shared_dimension_error")
            self.voice.speak(message)
            #raise ValueError(message)
            return False

        for r1, r2, d in zip(v1.reading, v2.reading, self.dimensions):
            print(shared_dimensions, r1, r2, d)
            if (d in shared_dimensions) and r1 != r2:
                message = self.voice.messages.get("same_space_error")
                self.voice.speak(message)
                #raise ValueError(message)
                return False

        return True


    def sum_vectors_message(self, v1, v2):
        v1_simple = v1.reading
        v2_simple = v2.reading
        v = [v1_simple[n] + v2_simple[n] for n, _ in enumerate(self.dimensions)]

        msg = 'Vetor com componentes: '
        for value, dimension in zip(v, ['i', 'j', 'k']):
            if value == 0:
                msg += f"{dimension} nulo, "
            elif value > 0:
                msg += f"{dimension} positivo, "
            else:
                msg += f"{dimension} negativo, "

        msg = msg[:-2] + '.'
        return msg


    def get_number_of_dimensions(self):
        number = 0
        while number < 2 or number > 3:
            message = self.voice.messages.get("select_dimensions")
            self.voice.speak(message)
            number = self.space_timer.run()
        return number


    def get_vector(self):
        has_vector = False
        while not has_vector:
            message = self.voice.messages.get("ask_for_read")
            self.voice.speak(message)
            self.space_timer.run()

            response = requests.get(self.base_path)
            response.raise_for_status
            vector_dict = response.json()
            vector = Vector(**vector_dict)
            print("[interaction] Got a vector:", vector.message)
            
            self.voice.speak(vector.message)
            message = self.voice.messages.get("ask_for_confirmation")
            self.voice.speak(message)
            n = self.space_timer.run()
            if n == 1:
                return vector


    def one_more_time_check(self):
        message = self.voice.messages.get("one_more_time_check")
        self.voice.speak(message)
        number_of_spaces = self.space_timer.run()
        return number_of_spaces == 1


    def run(self):
        is_required = True
        is_odd_iteration = True
        while is_required:
            if is_odd_iteration:
                self.guide.propose_2D_problem()
                is_odd_iteration = False
            else:
                self.guide.propose_3D_problem()
                is_odd_iteration = True

            number_of_dimensions = self.get_number_of_dimensions()

            try:
                v1 = self.get_vector()
            except ValueError as e:
                message = self.voice.messages.get("fatal_error")
                self.voice.speak(message)
                raise e

            if number_of_dimensions == 3:
                message = self.voice.messages.get("represent_missing_dimension")
                self.voice.speak(message)
                sleep(1)
                has_2_vectors = False
                while not has_2_vectors:
                    try:
                        v2 = self.get_vector()
                    except ValueError as e:
                        message = self.voice.messages.get("fatal_error")
                        self.voice.speak(message)
                        raise e

                    try:
                        has_2_vectors = self.check_vectors(v1, v2)
                    except ValueError as e:
                        message = self.voice.messages.get("fatal_error")
                        self.voice.speak(message)
                        raise e

                try:
                    message = self.sum_vectors_message(v1, v2)
                    self.voice.speak("Representação de um vetor em três dimensões completa.")
                    sleep(1)
                    self.voice.speak(message)
                except Exception as e:
                    message = self.voice.messages.get("fatal_error")
                    self.voice.speak(message)
                    raise e

            is_required = self.one_more_time_check()
        
        message = self.voice.messages.get("bye")
        self.voice.speak(message)

    def test(self):
        vector = Vector(
            cube = CubeDimensions(
                vertical='i',
                horizontal='k',
                positive_in_i=True,
                positive_in_k=False
            ),
            grid = GridPositions(
                vertical_position=1,
                horizontal_position=-1
            )
        )
        self.voice.speak(vector.message)

def main():
    interaction = Interactions()
    #import asyncio
    #asyncio.run(interaction.run())
    interaction.run()

if __name__ == "__main__":
    main()