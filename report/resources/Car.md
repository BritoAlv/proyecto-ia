## Agente Carro

El carro se encuentra desplazándose por las carreteras sin poder haber dos carros en una misma posición, y respetando los semáforos, comienzan en una posición inicial y su objetivo es un lugar de interés localizado en el mapa, una vez lleguen a este lugar son eliminados de la simulación. 

El carro necesita una forma de encontrar un camino hacia su lugar de destino, ha de saber actuar cuando no puede seguir con su plan y desea evitar estancarse en un semáforo.

El carro posee una estrategia que seguirá para llegar a su destino ( carácter pro-activo) pero ya sea, porque no le es posible continuar o porque no le dio resultado la actualizará ( reconsiderar su estrategia), además de que debe moverse siempre si le es posible (carácter reactivo), o sea, porque no pueda seguir su plan no debe dejar de moverse porque si no obstruiría el tráfico.

Posee un método *emergency_act* que como el nombre indica, lo utiliza cuando su plan no es viable, por las condiciones del ambiente. 

En circunstancias normales empleará su estrategia para decidir que camino tomar.

### Estrategia:

El carro puede estar en dos estados : *Obstruido* y *Libre*, puede tomar cuatro acciones : *Random*, *Depth-DFS*, *Dijkstra*, *Dijkstra-Modified*, esto es representado a través de una matriz de probabilidades de $2*4$, en cada fila, está las probabilidades de que tome la acción de esa columna, las probabilidades de una fila han de sumar $1$. La idea es que a medida que el carro usa las acciones actualize estas probabilidades en función de si le fue útil o no utilizar esta acción.

El carro se encuentra en el estado *Obstruido* si sus últimas tres posiciones son las mismas.
El carro se encuentra en el estado *Libre* si sus últimas tres posiciones son diferentes.

En un estado, decide que acción tomar, escogiendo un número aleatorio entre $[0, 1]$ y en dependencia de que intervalo se encuentre escoge la acción.

Una acción en un estado es priorizada ( aumenta su probabilidad ) si permitió que el carro se moviera en las últimas dos iteraciones, en caso contrario su probabilidad  en ese estado es disminuida. Esto es una forma de implementar el método *reward*, puede ser escogida otra forma de *reward* una acción.

Cada una de las acciones mencionadas anteriormente consiste en:

#### Random:
Escoge una posición adyacente (pudiendo tener que cruzar un semáforo para moverse)
#### Dijkstra:
Halla el camino más corto de la posición actual a el destino ( notar que el grafo es dirigido), siendo todos los pesos $1$.


Las siguientes dos estrategias son basadas en una heurística, dado el dinamismo de el ambiente donde se encuentra el carro.

El carro desea llegar lo más rápido posible a su lugar de destino, debido a la presencia de semáforos el camino más corto no tiene porque ser el óptimo. Una idea inicial es darle un peso diferente a los semáforos dependiendo de que tan cargados estén, sería análogamente un Dijkstra en un grafo donde las aristas entre carreteras poseen peso $1$, y las que son entre carretera y semáforo poseen un peso dependiendo de el semáforo en cuestión. Para obtener el peso del semáforo añadimos una variable *OVERLOAD* de salida a el *FuzzySystem* del semáforo.

La idea anterior no es suficiente porque el entorno es dinámico, la carga de un semáforo varía, por ejemplo, si el carro traza una ruta en la que debe cruzar tres semáforos siendo el tercero el menos cargado, es posible que en el tiempo en que cruza los dos primeros semáforos el tercer semáforo se sobrecargue y no resulte efectiva la ruta.

Para evitar lo anterior :

#### DijkstraM:

En este mantenemos la idea de darle un peso a los semáforos determinado por su *OVERLOAD*, pero este peso lo dividimos entre la distancia de el semáforo a la posición actual de el carro. De esta forma los semáforos muy alejados no aportarían mucho a el peso del camino, mientras que los cercanos sí.

#### Depth-DFS:

Usamos un *DFS* de profundidad limitada, la idea es la siguiente, obtenemos un peso o distancia de que tan bueno es un camino de tamaño $k$ en términos de la sobre-carga de los semáforos, y después desde la posición en que acaba el camino hallamos la distancia de esta posición a el destino ($Dijkstra$), sumamos estos dos números y tenemos un peso a un camino, entre todos los pesos escogemos el menor. Notar que $k$ ha de ser pequeña, porque se consideran todos los caminos de tamaño $k$ que comienzan en la posición actual. Tiene como objetivo dividir el peso de un camino en dos partes : la cercanía al carro influenciado por los semáforos y la distancia a el objetivo.

Es posible añadir más acciones y más estados en los que se puede encontrar el carro, y análogamente otras heurísticas respecto a que con cuales condiciones priorizar o no una acción en un estado. Los carros no poseen factor social incorporado, solamente pro-activo y reactivo. Los carros no pueden constantemente re-plantearse su estrategia porque sería costoso por lo que deben tener un balance de que tanto se mantienen con su plan o lo reconsideran.