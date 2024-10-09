# Estadísticas

### General
Para analizar el problema planteado en este trabajo se realizó un análisis comparativo en cuanto a las operaciones de ambos tipos de semáforos (ya fueren inteligentes o estandar). Se llegó a ejecutar un promedio de 24 simulaciones en cada caso, permitiendo construir un dataframe de la biblioteca de Python Pandas para cada uno de los casos simulados, separando la información de cada simulación en los aspectos a analizar: peatones y vehículos. Con este trabajo nos plantearon como objetivo principal poder llegar a conocer la efectividad de los semáforos inteligentes en la actualidad, si con la implementación de estos los automóviles tienen realmente un recorrido más rápido hacia su destino y si disminuye el tiempo de los peatones en cada paso peatonal donde estos están.

#### Distribuciones
Implementando el uso de histogramas se graficaron cada una de las simulaciones realizadas para poder analizar la distribución de cada una de ellas. En el mismo gráfico estarán representadas ambas simulaciones simultáneamente (de semáforos tanto inteligentes como estandar).

A continuación los histogramas que representan el tiempo ocupado por los vehículos en semáforos inteligentes y estandar:

[![Image alt text](images/hist_cars_0.png)]()
[![Image alt text](images/hist_cars_1.png)]()
[![Image alt text](images/hist_cars_2.png)]()
[![Image alt text](images/hist_cars_3.png)]()
[![Image alt text](images/hist_cars_4.png)]()
[![Image alt text](images/hist_cars_5.png)]()
[![Image alt text](images/hist_cars_6.png)]()
[![Image alt text](images/hist_cars_7.png)]()
[![Image alt text](images/hist_cars_8.png)]()
[![Image alt text](images/hist_cars_9.png)]()
[![Image alt text](images/hist_cars_10.png)]()
[![Image alt text](images/hist_cars_11.png)]()
[![Image alt text](images/hist_cars_12.png)]()
[![Image alt text](images/hist_cars_13.png)]()
[![Image alt text](images/hist_cars_14.png)]()
[![Image alt text](images/hist_cars_15.png)]()
[![Image alt text](images/hist_cars_16.png)]()
[![Image alt text](images/hist_cars_17.png)]()
[![Image alt text](images/hist_cars_18.png)]()
[![Image alt text](images/hist_cars_19.png)]()
[![Image alt text](images/hist_cars_20.png)]()
[![Image alt text](images/hist_cars_21.png)]()
[![Image alt text](images/hist_cars_22.png)]()
[![Image alt text](images/hist_cars_23.png)]()

En este segundo grupo de gráficos los histogramas representan el tiempo que ocupan los peatones en semáforos inteligentes y estandar:

[![Image alt text](images/hist_walkers_0.png)]()
[![Image alt text](images/hist_walkers_1.png)]()
[![Image alt text](images/hist_walkers_2.png)]()
[![Image alt text](images/hist_walkers_3.png)]()
[![Image alt text](images/hist_walkers_4.png)]()
[![Image alt text](images/hist_walkers_5.png)]()
[![Image alt text](images/hist_walkers_6.png)]()
[![Image alt text](images/hist_walkers_7.png)]()
[![Image alt text](images/hist_walkers_8.png)]()
[![Image alt text](images/hist_walkers_9.png)]()
[![Image alt text](images/hist_walkers_10.png)]()
[![Image alt text](images/hist_walkers_11.png)]()
[![Image alt text](images/hist_walkers_12.png)]()
[![Image alt text](images/hist_walkers_13.png)]()
[![Image alt text](images/hist_walkers_14.png)]()
[![Image alt text](images/hist_walkers_15.png)]()
[![Image alt text](images/hist_walkers_16.png)]()
[![Image alt text](images/hist_walkers_17.png)]()
[![Image alt text](images/hist_walkers_18.png)]()
[![Image alt text](images/hist_walkers_19.png)]()
[![Image alt text](images/hist_walkers_20.png)]()
[![Image alt text](images/hist_walkers_21.png)]()
[![Image alt text](images/hist_walkers_22.png)]()

Los resultados obtenidos arrojaron que los histogramas no siguen distribuciones normales ni ninguna otra conocida. Con esto podríamos suponer que los semáforos en general brindan mejores resultados, pero esto podrá ser analizado a profundidad y comprobado a continuación.

### ScatterPlot
A continuación se realizará una representación usando el gráfico scatterplot de la biblioteca seaborn donde se analizarán valores que representan el tiempo total de tanto autos como peatones en un trayecto completo y qué tiempo de este es utilizado en la espera de los semáforos analizando cómo se comportan estas variables una con respecto a la otra. Verificándose representadas en cada caso:

En semáforos inteligentes;
[![Image alt text](images/scatter1.png)]()

[![Image alt text](images/scatter2.png)]()

En semáforos estandar;

[![Image alt text](images/scatter3.png)]()

[![Image alt text](images/scatter4.png)]()

Al observar los datos se puede inferir que existe una importante relación entre los datos, lo que nos indica que entre ellos cabe la existencia de una fuerte correlación; para lo cual se estarán realizando más pruebas.


### Matriz de correlación
Analizaremos para una misma simulación las matrices de correlación entre los datos de cada csv que formamos, toda esta información es analizada en los gráficos de scatterplot anteriores.
Como resultado se obtuvo que su correlación es de 1 lo que nos indica que dichos datos siguen una dependencia lineal.
[![Image alt text](images/coor1.png)]()

[![Image alt text](images/coor2.png)]()

[![Image alt text](images/coor3.png)]()

[![Image alt text](images/coor4.png)]()

### Test Wilcoxon signed-rank
Para comprobar la existencia o no de una diferencia significativa entre los datos analizados en las simulaciones de semáforos inteligentes y estandar se utilizó el Test Wilcoxon signed-rank.
Como podemos observar en la gráfica; los p_value son mayores que 0.05 por lo que no es posible llegar a ninguna conclusión.
[![Image alt text](images/test.png)]()


### Comparar medias
Por último se compararán las medias de cada conjunto de simulaciones de semáforos inteligentes y no inteligentes.

[![Image alt text](images/heap.png)]()

Todo esto parece indicar que los semáforos estandar optimizan el tiempo de espera de los carros y peatones.

### Conclusiones