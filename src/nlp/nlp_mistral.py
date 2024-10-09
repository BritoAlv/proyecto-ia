from mistralai import Mistral
import json
from nlp.nlp_abstraction import Nlp

class NlpMistral(Nlp):
    def __init__(self) -> None:
        with open("./src/nlp/mistral_instructions.txt") as file:
            self._instructions = file.read()

        self._api_key = ""
        try:
            with open("./src/nlp/key.txt") as file:
                self._api_key = file.read()
        except:
            self._api_key = "api_key"
            
        self._llm = Mistral(api_key=self._api_key)
            
    def process_place_description(self, text: str) -> str:
        response = self._llm.chat.complete(
            model = "mistral-large-latest",
            messages = [
                {"role": "user", "content": self._instructions + text}
            ]
        )

        response = response.choices[0].message.content
        return response[8:-3] if response[0] == '`' else response

if __name__ == '__main__':
    mistral = NlpMistral()
    output_str = mistral.process_place_description(
    '''
    {
        "Name": "Morro Cabaña",
        "Description": "Sitio histórico ubicado en la entrada de la bahía de la Habana. Utilizado actualmente como centro turístico. Mantiene abierta sus puertas todo el año desde las 8am hasta las 6pm. Las persona pueden recorrerlo y conocer sobre la historia detrás de la Habana y de Cuba"
    }                                                                                
    ''')

    output_object = json.loads(output_str)
    print(output_object)