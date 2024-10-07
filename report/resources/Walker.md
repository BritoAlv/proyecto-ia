## Agente Caminante 

Los agentes caminantes están basados en la arquitectura $BDI$, estos se mueven a través de las aceras y pueden cruzar una calle siempre que el semáforo esté en rojo, ellos poseen varios lugares de interés a los que desean ir, (tienen una prioridad sobre cuales desean visitar primero), pero no saben inicialmente donde se encuentran estos, poseen una creencia de donde puedan estar. A medida que se mueven y visitan lugares de interés en el mapa guardan actualizan sus creencias sobre los lugares de interés en el mapa. A su vez actualizan las prioridades sobre los lugares que desean visitar, escogiendo para visitar ( intención) el de mayor prioridad, incorporan un factor social además.

Paso a paso su funcionamiento:

1 - Actualizan sus creencias: Si en su posición actual hay un lugar de interés añaden esta información a sus creencias (sabe donde está, por tanto es conocimiento). Si en su posición hay otro caminante se escoge un número aleatorio y si es menor que su factor social, este caminante actualiza sus beliefs además usando los beliefs del caminante con el que se encontró. O sea cada caminante tiene un factor social como un número entre $[0, 1]$, para decidir cuando ser social con otros caminantes. Además un caminante posee otro factor de confianza, si esta es baja es menos probable que escoja creencias de otro caminante que no sean certeras. Siempre escoge las que representen conocimiento. De esta forma un caminante actualiza sus creencias.

2 - Si ya visitó todos los lugares que deseaba entonces es removido de la simulación.

3 - Cada caminante posee un factor de reactivad, entonces si su plan se acabó ( el camino que estaba siguiendo ya lo culminó) o un número aleatorio es menor que este factor, el caminante actualiza sus deseos y ha de escoger un plan nuevo.

Actualiza sus deseos de la siguiente forma: Sus deseos son representados a través de un diccionario donde a cada lugar que desea visitar le es asignado una prioridad. Si hay un caminante en mi posición que también desea ir a un lugar en específico le es aumentada la prioridad, aquí nuevamente se tiene en cuenta el factor social. Si hay algún lugar entre mis deseos que se donde se encuentra le aumento la prioridad. Aleatoriamente escojo un lugar y le aumento la prioridad. Finalmente si un caminante lleva mucho tiempo en una posición en específico se igual todas las prioridades.

Escoge un plan de la siguiente forma: Escoge como lugar o intención a ir el de más prioridad entre sus deseos, si el caminante está seguro de donde está el lugar y posee suficiente deseo de visitarlo usará Dijkstra para determinar el camino. En caso contrario se moverá aleatoriamente.

4 - Finalmente escoge la siguiente posición en el camino determinado por su plan para moverse, si no le es posible moverse se mantiene en la posición actual.