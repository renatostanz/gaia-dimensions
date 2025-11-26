from piper import PiperVoice
from pyaudio import PyAudio

class Voice:
    def __init__(self):
        self.voice = PiperVoice.load("voice/models/pt_BR-cadu-medium.onnx", use_cuda=True)
        self.pa = PyAudio()
        self.stream = None
        self.messages = {
            "select_instructions": "Pressione a barra de espaço para indicar o número de dimensões que serão representadas.",

            "select_dimensions": "Precione a barra de espaço duas vezes se deseja representar um vetor de duas dimensões; ou três vezes para representar um vetor de três dimensões.",

            "selected_2_dimensions": "Você selecionou que representará um vetor de duas dimensões.",
            "selected_3_dimensions": "Você selecionou que representará um vetor de três dimensões.",

            "ask_for_read": "Quando os artefatos estiverem prontos, pressione a barra de espaço para ler a representação de duas dimensões do vetor.",
            "ask_for_confirmation": "Se estiver correto, pressione a barra de espaço uma vez. Caso contrário, pressione a barra de espaço duas vezes para ler novamente.",
            "represent_missing_dimension": "Você já definiu duas dimensões do seu vetor, agora realize uma representação que contenha a terceira dimensão dele.",

            "one_more_time_check": "Deseja representar outro vetor? Em caso afirmativo pressione uma vez a barra de espaço, do contrário pressione a barra de espaço duas vezes.",
            
            "shared_dimension_error": "Os dois vetores devem manter a sua dimensão compartilhada com o mesmo valor. Por favor, tente novamente.",
            "same_space_error": "Os dois vetores representam apenas duas dimensões do mesmo espaço. Por favor, tente novamente.",
            "fatal_error": "Ocorreu um erro fatal. Encerrando o programa.",
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
        for chunk in self.voice.synthesize(message):
            self.set_audio_format(chunk.sample_rate, chunk.sample_width, chunk.sample_channels)
            self.write_raw_data(chunk.audio_int16_bytes)

    def close(self):
        if self.stream:
            self.stream.close()
        self.pa.terminate()


if __name__ == "__main__":
    voice_obj = Voice()
    voice_obj.write_audios()
    voice_obj.run()
    voice_obj.close()
