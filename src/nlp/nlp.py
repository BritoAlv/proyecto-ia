from mistralai import Mistral

class Nlp:
    def __init__(self) -> None:
        self.api_key = "amk4WhcFI6dXBHJUzcjhQhwUhmgjMqlP"
        self.llm = Mistral(api_key=self.api_key)
        self.initial_prompt = '''te voy a dar algo asi ( "Universidad de La Habana", "Principal centro de Educación Superior del país. Presenta cinco facultades y una capacidad de 1500 alumnos tanto de pregrado como postgrado." ) y de este texto se extrae esto son que contiene las siguiente propiedades:

        walkers: Probabilidad que lo visite un peatón. Número entre 0 y 1
        cars: Probabilidad que lo visite un auto. Número entre 0 y 1
        months: Meses en los que está activo
        hours: Intervalo de horas (hora militar) al día en que está activo. Lista de dos elementos. ([7, 17] significa de 7am a 5pm)
        Ejemplo:

        {
            "walkers": 0.8,
            "cars": 0.4,
            "months": ["September", "October", "November", "December", "January", "February", "March", "April", "May", "June"],
            "hours": [7, 17]
        } 
        entonces yo te voy a dar otro texto y quiero que me devuelvas un json como el que te enseñe para el texto que te dare'''

    def response(self, text):
        response = self.llm.chat.complete(
        model = "mistral-large-latest",
        messages = [
                {"role": "user", "content": self.initial_prompt + text}
            ]
        )
        return response.choices[0].message.content
    

nlp = Nlp()

nlp.response(" a las diez habra aniversario en el estadio")