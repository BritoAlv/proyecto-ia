# Estadisticas

### General
Simulamos 24 veces con semáforos inteligentes y con semáforos normales con ello construimos un csv por cada simulacion. El objetivo principal es ver si con un semáforos inteligente los carros llegan mas rapido a su destino y si se demoran menos en los semáforos igualmente para los peatones.

#### Distribuciones
Vamos a graficar cada simulacion para ver que distribucion siguen. Para ello usamos histogramas y lo que haremos sera cojer una simulacion de los semáforos inteligente y compararlas con los semáforos normales todo en un mismo grafico.

[![Image alt text](images/hist_cars_0.png)](https://example.com/link)
[![Image alt text](images/hist_cars_1.png)](https://example.com/link)
[![Image alt text](images/hist_cars_2.png)](https://example.com/link)
[![Image alt text](images/hist_cars_3.png)](https://example.com/link)
[![Image alt text](images/hist_cars_4.png)](https://example.com/link)
[![Image alt text](images/hist_cars_5.png)](https://example.com/link)
[![Image alt text](images/hist_cars_6.png)](https://example.com/link)
[![Image alt text](images/hist_cars_7.png)](https://example.com/link)
[![Image alt text](images/hist_cars_8.png)](https://example.com/link)
[![Image alt text](images/hist_cars_9.png)](https://example.com/link)
[![Image alt text](images/hist_cars_10.png)](https://example.com/link)
[![Image alt text](images/hist_cars_11.png)](https://example.com/link)
[![Image alt text](images/hist_cars_12.png)](https://example.com/link)
[![Image alt text](images/hist_cars_13.png)](https://example.com/link)
[![Image alt text](images/hist_cars_14.png)](https://example.com/link)
[![Image alt text](images/hist_cars_15.png)](https://example.com/link)
[![Image alt text](images/hist_cars_16.png)](https://example.com/link)
[![Image alt text](images/hist_cars_17.png)](https://example.com/link)
[![Image alt text](images/hist_cars_18.png)](https://example.com/link)
[![Image alt text](images/hist_cars_19.png)](https://example.com/link)
[![Image alt text](images/hist_cars_20.png)](https://example.com/link)
[![Image alt text](images/hist_cars_21.png)](https://example.com/link)
[![Image alt text](images/hist_cars_22.png)](https://example.com/link)
[![Image alt text](images/hist_cars_23.png)](https://example.com/link)

Y la referente a los datos de los peatones
[![Image alt text](images/hist_walkers_0.png)](https://example.com/link)
[![Image alt text](images/hist_walkers_1.png)](https://example.com/link)
[![Image alt text](images/hist_walkers_2.png)](https://example.com/link)
[![Image alt text](images/hist_walkers_3.png)](https://example.com/link)
[![Image alt text](images/hist_walkers_4.png)](https://example.com/link)
[![Image alt text](images/hist_walkers_5.png)](https://example.com/link)
[![Image alt text](images/hist_walkers_6.png)](https://example.com/link)
[![Image alt text](images/hist_walkers_7.png)](https://example.com/link)
[![Image alt text](images/hist_walkers_8.png)](https://example.com/link)
[![Image alt text](images/hist_walkers_9.png)](https://example.com/link)
[![Image alt text](images/hist_walkers_10.png)](https://example.com/link)
[![Image alt text](images/hist_walkers_11.png)](https://example.com/link)
[![Image alt text](images/hist_walkers_12.png)](https://example.com/link)
[![Image alt text](images/hist_walkers_13.png)](https://example.com/link)
[![Image alt text](images/hist_walkers_14.png)](https://example.com/link)
[![Image alt text](images/hist_walkers_15.png)](https://example.com/link)
[![Image alt text](images/hist_walkers_16.png)](https://example.com/link)
[![Image alt text](images/hist_walkers_17.png)](https://example.com/link)
[![Image alt text](images/hist_walkers_18.png)](https://example.com/link)
[![Image alt text](images/hist_walkers_19.png)](https://example.com/link)
[![Image alt text](images/hist_walkers_20.png)](https://example.com/link)
[![Image alt text](images/hist_walkers_21.png)](https://example.com/link)
[![Image alt text](images/hist_walkers_22.png)](https://example.com/link)
[![Image alt text](images/hist_walkers_23.png)](https://example.com/link)

Obtuvimos que no siguen distribuciones normales ni ninguna otra conocida tambien pareciera que los semáforos inteligentes en general dan mejores resultados, pero esto proximamente lo comprobaremos mejor.

### Matriz de correlacion
Analizemos para una misma simulacion las matrices de correlacion entre los datos de cada csv que formamos.
Obtenemos que su correlacion es de 1 y tambien los graficamos usando un scatter plot y vemos que siguen una dependencia lineal.
[![Image alt text](images/coor1.png)](https://example.com/link)

[![Image alt text](images/coor2.png)](https://example.com/link)

[![Image alt text](images/coor3.png)](https://example.com/link)

[![Image alt text](images/coor4.png)](https://example.com/link)

### Test wilcoxon
Vamos a realizar un test wilcoxon para comprobar si hay diferencia significativa entre los datos de las simulaciones de semáforos inteligentes y normales.
Como podemos ver en la grafica los p_value son mayores que 0.05 entonces no podemos llegar a ninguna conclusion
[![Image alt text](images/test.png)](https://example.com/link)


### Comparar Medias
Por ultimo compararemos las medias de cada conjunto de simulaciones de semáforos inteligentes y no inteligentes.

[![Image alt text](images/heap.png)](https://example.com/link)

Parece indicar que los semáforos no inteligentes minimizan mejor el tiempo de espera de los carros y peatones.

### Conclusiones