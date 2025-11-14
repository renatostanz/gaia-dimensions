from app.models.artifacts import Vector
from urllib.error import HTTPError
from space_timer import SpaceTimer
import requests

class Interactions:
    vectors: dict[str, Vector] = []
    base_path = 'http://localhost:8000/get'
    dimensions = ['i', 'j', 'k'] 
    space_timer = SpaceTimer()


    def check_vectors(self, v1, v2) -> bool:
        shared_dimensions = []
        v1_dimensions = [v1.cube.horizontal, v1.cube.vertical]
        if v2.cube.horizontal in v1_dimensions:
            shared_dimensions.append(v2.cube.horizontal)
        if v2.cube.vertical in v1_dimensions:
            shared_dimensions.append(v2.cube.vertical)

        if len(shared_dimensions) > 1:
            raise ValueError("Os dois vetores representam apenas 2 dimensões do mesmo espaço.")

        for u1, u2, d in zip(v1, v2, self.dimensions):
            if (d in shared_dimensions) and u1 != u2:
                raise ValueError("Os dois vetores devem manter a sua dimensão compartilhada com o mesmo valor")

        return True



    def sum_vectors(self, v1, v2):
        return [v1[n] + v2[n] for n, _ in enumerate(self.dimensions)]



    def get_number_of_dimensions(self):
        number = 0
        print("Pressione a barra de espaço para indicar o número de dimensões que serão representadas (2 ou 3).",
              "Para terminar basta precionar a barra de espaço após ao menos 1 segundo sem precionar alguma tecla.",
              "Caso hajam mais do que 3 dimensões será solicitada uma nova entrada."
        )
        while number < 1 and number > 3:
            print("Precione a barra de espaço para o número de dimensões desejadas (2 ou 3) para o vetor gerado·")
            number = self.space_timer.run()
        return number



    async def get_vector(self):
        response = await requests.get(self.base_path)
        response.raise_for_status
        data = response.json()
        return Vector(**data)



    async def run(self):
        is_required = True
        while is_required:
            number_of_dimensions = self.get_number_of_dimensions()

            try:
                v1 = await self.get_vector()
                has_2_vectors = False
            except ValueError as e:
                print(e)

            while not has_2_vectors or number_of_dimensions < 2:
                try:
                    v2 = await self.get_vector()
                except ValueError as e:
                    print(e)

                try:
                    has_2_vectors = self.check_vectors(v1, v2)
                except ValueError as e:
                    print(e)

            v = self.sum_vectors(v1, v2)
            is_required = self.one_more_time_check()
