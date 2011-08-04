Estas clases proveen funcionalidad para la comunicacion con el MASSim-server
via sockets. 
El agente que haga uso de estas clases debera instanciar la conexion, 
conectarse, y usar los metodos provistos para recibir percepciones y enviar
acciones.



###############################################################################

ROLES

###############################################################################

Cada archivo .pl para cada rol deber� tener:
    - rolSetBeliefs: aserta todas las beliefs necesarias para que las metas propias del rol puedan calcularse
    - rolMetas: calcula todas las metas propias del rol
    
Cada archivo podr� importar un archivo .delp que puede tener reglas de delp propias.