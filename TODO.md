# TODO List

0- Pensar

1- Importar vocabularios SKOS usando [rdflib-neo4j](https://neo4j.
com/labs/rdflib-neo4j/), teniendo neo4j como store.

  - A todos los nodos de un vocabulario se les debe adicionar un tag que haga 
  referencia al vocabulario al que pertenece.
  - Crear un indice por cada vocabulario que tendrá los embbedings de ese 
    vocabulario. 
  - Crear un indice general para los embbedings de todos los vocabularios.

2- Por cada término de un vocabulario, se debe crear un texto que 
posteriormente se utiliza para los embbedings. Hay que hacer un modulo que 
permita parametrizar (o agregar al codigo) estrategias para la construccion 
de un texto 
por termino. 

3- 