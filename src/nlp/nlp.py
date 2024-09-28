from mistralai import Mistral

class Nlp:
    def __init__(self) -> None:
        self.api_key = "amk4WhcFI6dXBHJUzcjhQhwUhmgjMqlP"
        self.llm = Mistral(api_key=self.api_key)
        self.initial_prompt = 'dependiendo de la informacion que brinda la afirmacion analiza dependiendo de la actividad el lugar en el que se realiza y la hora especifica , en caso de no existir este ultimo debes suponerlo.Debes devolverme la respuesta en el formato                   {type: "actividad"            value: [lugar, hora]} el type siempre sera "actividad"    y que puedas reconocer si habla de eso varias veces       de la forma   de un array de ese objeto              y solo quiero ese array no me des mas  texto adicional                                  . La afirmacion es la siguiente :'
    
    def response(self, text):
        response = self.llm.chat.complete(
            model="mistral-large-latest",
            messages=[
                {"role": "user", "content": self.initial_prompt + text}
            ]
        )
        return response.choices[0].message.content
    

nlp = Nlp()

nlp.response(" a las diez habra aniversario en el estadio")