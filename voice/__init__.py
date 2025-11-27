from random import randrange, choice
from piper import PiperVoice
from pyaudio import PyAudio
from time import sleep

import pygame

class NotificationSound:
    def __init__(self):
        self.notification_file = "voice/recordings/audio_2025-11-26_04-27-05.ogg"
        pygame.mixer.init()
        pygame.mixer.music.load(self.notification_file)

    def play(self):
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.wait(100)

class Guide:
    def __init__(self):
        self.voice = PiperVoice.load("voice/models/pt_BR-jeff-medium.onnx", use_cuda=True)
        self.pa = PyAudio()
        self.stream = None
    
    def get_vector_message(self, vector):
        msg = ''
        for dimension, value in vector.items():
            if value == 0:
                msg += f"{dimension} nulo, "
            elif value == 1:
                msg += f"{dimension} positivo, "
            else:
                msg += f"{dimension} negativo, "
                
        msg = msg[:-2] + '.'
        return msg
    
    def generate_random_2D_vector(self):
        dimensions = ['i', 'j', 'k']
        v1 = choice([-1, 1])
        i = randrange(2)
        d1 = dimensions[i]
        dimensions = dimensions[i+1:]

        v2 = choice([-1, 1])
        d2 = choice(dimensions)

        vector = {
            d1: v1,
            d2: v2,
        }
        return self.get_vector_message(vector)

    def propose_2D_problem(self):
        vector = self.generate_random_2D_vector()
        print("Proposed vector:", vector)
        self.speak(vector)


    def generate_random_3D_vector(self):
        dimensions = ['i', 'j', 'k']
        vector = {}
        for d in dimensions:
            vector[d] = choice([-1, 1])
            
        return self.get_vector_message(vector)

    def propose_3D_problem(self):
        vector = self.generate_random_3D_vector()
        print("Proposed vector:", vector)
        self.speak(vector)

    
    def set_audio_format(self, sample_rate, sample_width, sample_channels):
        if self.stream:
            self.stream.close()

        self.stream = self.pa.open(
            format=self.pa.get_format_from_width(sample_width),
            channels=sample_channels,
            rate=sample_rate,
            output=True
        )

    def write_raw_data(self, audio_bytes):
        self.stream.write(audio_bytes)


    def speak(self, vector):
        problem = f"Represente o vetor com as seguintes componentes: {vector}"
        message = f"{problem}. Repetindo. {problem}."
        
        for chunk in self.voice.synthesize(message):
            self.set_audio_format(chunk.sample_rate, chunk.sample_width, chunk.sample_channels)
            self.write_raw_data(chunk.audio_int16_bytes)
        
    def close(self):
        if self.stream:
            self.stream.close()
        self.pa.terminate()
        

class Voice:
    def __init__(self):
        self.voice = PiperVoice.load("voice/models/pt_BR-cadu-medium.onnx", use_cuda=True)
        self.pa = PyAudio()
        self.stream = None
        self.messages = {
            "select_instructions": "Pressione a barra de espaço para indicar o número de dimensões não nulas que serão representadas.",

            "select_dimensions": "Caso deseje representar um vetor em duas dimensões precione a barra de espaço duas vezes; ou se deseja representar um vetor em três dimensões precione três vezes.",

            "selected_2_dimensions": "Você selecionou que representará um vetor em duas dimensões.",
            "selected_3_dimensions": "Você selecionou que representará um vetor em três dimensões.",

            "ask_for_read": "Quando os artefatos estiverem prontos, pressione a barra de espaço para ler a representação de duas dimensões do vetor.",
            "ask_for_confirmation": "Se estiver correto, pressione a barra de espaço uma vez. Caso contrário, pressione a barra de espaço duas vezes para ler novamente.",
            "represent_missing_dimension": "Você já definiu duas dimensões do seu vetor, agora realize uma representação que contenha a terceira dimensão dele.",

            "one_more_time_check": "Deseja representar outro vetor? Em caso afirmativo pressione uma vez a barra de espaço, do contrário pressione a barra de espaço duas vezes.",
            
            "shared_dimension_error": "Os dois vetores devem manter a sua dimensão compartilhada com o mesmo valor. Por favor, tente novamente.",
            "same_space_error": "Os dois vetores representam apenas duas dimensões do mesmo espaço. Por favor, tente novamente.",
            "fatal_error": "Ocorreu um erro interno do programa. Encerrando!",
            "bye": "Certo, até mais!",
        }

    def set_audio_format(self, sample_rate, sample_width, sample_channels):
        if self.stream:
            self.stream.close()

        self.stream = self.pa.open(
            format=self.pa.get_format_from_width(sample_width),
            channels=sample_channels,
            rate=sample_rate,
            output=True
        )

    def write_raw_data(self, audio_bytes):
        self.stream.write(audio_bytes)


    def speak(self, message):
        sleep(0.5)
        for chunk in self.voice.synthesize(message):
            self.set_audio_format(chunk.sample_rate, chunk.sample_width, chunk.sample_channels)
            self.write_raw_data(chunk.audio_int16_bytes)

    def close(self):
        if self.stream:
            self.stream.close()
        self.pa.terminate()


if __name__ == "__main__":
    notification_obj = Guide()
    notification_obj.propose_2D_problem()
    notification_obj.propose_3D_problem()
