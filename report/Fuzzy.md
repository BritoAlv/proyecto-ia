## Fuzzy Logic 

Fuzzy Logic es una modificación a la lógica común donde solamente hay dos valores, verdad o falso. En Fuzzy Logic en vez de ser solamente $0$, $1$, se usa un grado de verdad cuantificado a través de un número real entre $0$, $1$.

Un sistema de lógica difusa recibe como entrada variables, cada variable posee un dominio de valores que puede tomar, por ejemplo de $0$ a $20$, o colores como rojo, azul, negro.

Para cada variable hay funciones cuyo dominio coincide con el de la variable y devuelven un número entre $0$ y $1$, representando un grado de pertenencia. Por ejemplo la temperatura va de $0$ a $10$ grados, (variable con su dominio). Si se quiere representar que la temperatura es alta de $8-10$ grados, se usaría una función que sea creciente, pero que en el intervalo de $[8, 10]$ alcance sus máximos valores. A la misma vez habrían otras funciones para otras clasificaciones de la temperatura como baja, normal, etc.

El sistema posee también variables de salida que poseen las mismas definiciones que las variables de entrada. El objetivo del sistema, es asignar a cada variable de salida un valor en su dominio original usando estimaciones de los grados de pertenencia de esta en cada una de sus características.

Al sistema se le añaden reglas lógicas que relacionan las características de las variables de entrada con las de salida, por ejemplo, si la temperatura es alta entonces la presión es baja. ( esto relaciona una característica (alta) de la variable de entrada temperatura, con una característica (baja) de la variable de salida presión)

Usando estas reglas se obtiene para cada variable de salida, para cada característica, un grado de pertenencia, el objetivo final es convertir este grado de pertenencia a un valor en el dominio de la de la variable. 

Un método para obtener esto es el siguiente: 

De cada variable, de cada función ( característica de la variable) se tiene un porciento que representa que tanto pertenece a esa característica, obtenido a través de las reglas añadidas, se considera ese porciento de área de la función. Juntando todas las áreas se obtiene una nueva área, el centroide de esta área se halla, el valor de la $x$ en el dominio de la variable que da lugar a este centroide se toma como el resultado final. 