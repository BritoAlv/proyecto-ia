# Traffic Simulation

El entorno de este proyecto es un mapa compuesto por casillas, que pueden representar, calles, acera, intersección, lugar de interés o nada.

Nuestros agentes son carros, semáforos y caminantes.

Tenemos un circuito de calles y aceras con semáforos que representan el funcionamiento del tráfico, por estas calles se moverán carros, cuyo objetivo principal es llegar a algún lugar de interés. LLegar a este lugar de interés posee complicaciones desde el punto de vista del carro, como escoger una calle que posee un semáforo cargado, o escoger un camino que puede ser muy largo existiendo uno corto. 

Como el entorno es dinámico, modelamos la situación de la siguiente forma:
	- cada semáforo posee parámetros que ajusta el mismo de acuerdo a algunos criterios. El semáforo usa Fuzzy Logic para lograrlo.
	- cuando un carro arriva a la simulación, es necesario desde su posición inicial, asignarle un camino a su posición final, teniendo en cuenta los parámetros de los semáforos en el momento de su arrivo, pero con el objetivo de no sobrecargar semáforos en específico. 
	
Se puede ver de la siguiente forma: cada carro poseerá un camino hacia su destino, este camino pasará por algunos semáforos, entonces por cada semáforo pasarán algunos carros, el objetivo es minimizar la suma over i: |Avg Carros por Semáforo - Carros por Semáforo i|.

Usando la suma anterior como fitness function, podemos dado un carro y el estado actual emplear un algoritmo genético para encontrar el camino que minimize esa suma.

Para lograr lo anterior es necesario modelar el problema como un grafo, convierto la matrix del mapa en un grafo, pero como represento las intersecciones, como vértices espećificos, asumiendo eso se le puede dar un peso a las aristas de estos vértices específicos, que sea por ejemplo la cantidad de carros que pasan por esa intersección, de esa forma, el peso de un camino es la suma de los pesos de los semáforos que pasan por ahí, notar que el grafo es dirigido. Pero entonces la estrategia puede ser escoger el camino menos pesado, y eso ya existe, eso es una greedy strategy. Pero no tiene porque ser la mejor, dejame ver la formulación exacta, 

every path should pass along some semaphors obligated, como logro la abstracción de 
