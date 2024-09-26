# Traffic Simulation

El entorno de este proyecto es un mapa compuesto por casillas, que pueden representar, calles, acera, intersección, lugar de interés o nada.

Nuestros agentes son carros, semáforos y caminantes. Los caminantes y los carros desean trasladarse a lugarés de interés en la ciudad. 

Los lugares de interés se representan como una posición en el mapa. Todos los lugares de interés poseen una probabilidad de que un carro tenga como destino este lugar, estas probabilidades suman $1$. A través de procesamiento de lenguaje natural modificamos estas probabilidades.

Tenemos un circuito de calles y aceras con semáforos que representan el funcionamiento del tráfico, por estas calles se moverán carros, cuyo objetivo principal es llegar a algún lugar de interés. LLegar a este lugar de interés posee complicaciones, como escoger una calle que posee un semáforo cargado, o escoger un camino que puede ser muy largo existiendo uno más corto. 

Como el entorno es dinámico, modelamos la situación de la siguiente forma:
	- cada semáforo posee parámetros que ajusta el mismo de acuerdo a algunos criterios. El semáforo usa Fuzzy Logic para lograrlo.
	- el movimiento de un carro desde su posción inicial hasta el lugar de interés tiene que tratar de minimizar la distancia y evitar los semáforos sobre-cargados, porque sería una distancia corta, pero con mucha espera entre semáforos. 

Modelamos la situación de la siguiente forma, cada carro puede disponer de un camino, idealmente óptimo, desde su posición hasta su posición final. Si no dispone de esta información se moverá aleatoriamente. 

Cómo el carro obtiene esa información ?

Con propabilidad $p$ ejecutará un algoritmo para obtener este camino, con este camino, si se quedará estancado en una posición del mapa, lo desechará y se comportará sin información, si no se queda estancado usará, mientras, este camino para moverse, pudiendo con probabilidad $p$ recalcular este camino.

Qué algoritmo se usa para obtener esta información ?

Inicialmente es posible usar Dijsktra para obtener el camino más corto entre la posición inicial y el goal, pero esto no tendría en cuenta que tan cargados estárían las carreteras y semáforos de por medio, para incluir esto, a el peso de una arista de A -> B, en vez de ser $1$, uniformemente, lo modificamos de la siguiente forma:
	- si en $B$ hay un carro añadimos un peso adicional, pero dado que el entorno es dinámico, no tiene sentido que si $B$ se encuentra muy alejado de la posición inicial, tenga efecto que haya un carro en esta posición, dado que en el tiempo en que $A$ se translada a esa posición es posible que esta esté libre o sigua ocupada, para cuantificar esto, el peso adicional que le añadimos, es dividido entre la distancia de $B$ a la posición inicial, de esta forma solamente tendrían un efecto significativo los carros cercanos a la posición actual de el carro.
	- si en $B$ hay un semáforo añadimos un peso adicional, determinado por el semáforo, y como se explicó en la situación anterior lo dividimos por la distancia.
	
Este peso adicional es $1$ en el caso de un carro, y un número entre $[1, 5]$ en el caso de los semáforos. Cuando esto es dividido por la distancia da un número entre $[1, 5]$, pero una vez que $d \geq 5$ será un número entre $[0, 1]$ para asegurar que no le quite toda la importancia a la distancia original.
	  
