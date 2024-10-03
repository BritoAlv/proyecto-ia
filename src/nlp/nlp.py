from mistralai import Mistral
import json

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
        entonces yo te voy a dar otro texto y quiero que me devuelvas un json como el que te enseñe pero si algun de los campos no lo puedes obtener del texto no te inventes datos y en la respuesta solo quiero ese json para el texto que te dare: '''

    def response(self, text):
        data = self.api_request(text)
        if data.get('walkers'):
            if data['walkers'] == None:
                data['walkers'] = 0.3
        else:
            data['walkers'] = 0.3
        if data.get('cars'):
            if data['cars'] == None:
                data['cars'] = 0.3
        else:
            data['cars'] = 0.3
        if data.get('months'):
            if data['months'] == None:
                data['months'] = ["January, February"]
        else:
            data['months'] = ["January, February"]
        if data.get('hours'):
            if data['hours'] == None:
                data['hours'] = [4, 6]
        else:
            data['hours'] = [4, 6]
        return data
    
    def api_request(self, text):
        response = self.llm.chat.complete(
            model = "mistral-large-latest",
            messages = [
                {"role": "user", "content": self.initial_prompt + text}
            ]
        )
        return self.convert_json(response.choices[0].message.content)
    def convert_json(self, text):
        cleaned_json_string = text[8:-3]
        try:
            data_structure = json.loads(cleaned_json_string)
            return data_structure

        except json.JSONDecodeError:
            return None

nlp = Nlp()
print(nlp.response("Gran lugar, abierto de cinco a seis de la madrugada, un mes si otro no en los meses pares o sea enero febrero marzo mayo"))