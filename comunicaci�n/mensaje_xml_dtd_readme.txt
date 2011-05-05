                               ______                             _                  _                 ____  ________    ____ 
                              / ____/____  ____ ___  __  ______  (_)_________ ______(_)____  ____     / __ \/ ____/ /   / __ \
                             / /    / __ \/ __ `__ \/ / / / __ \/ // ___/ __ `/ ___/ // __ \/ __ \   / / / / __/ / /   / /_/ /
                            / /___ / /_/ / / / / / / /_/ / / / / // /__/ /_/ / /__/ // /_/ / / / /  / /_/ / /___/ /___/ ____/ 
                            \____/ \____/_/ /_/ /_/\__,_/_/ /_/_/ \___/\__,_/\___/_/ \____/_/ /_/  /_____/_____/_____/_/      
                                                                                                                              
                                                                                                  
En el archivo <mensaje_xml_dtd.xml> cree un template DTD (Document Type Definition) en el cual declaro los campos que tentativamente podr�an llegar a tener los 
mensajes que se pasen por la red para la comunicaci�n y discusi�n de los agentes.
A nivel conceptual puse un agente origen y uno o varios agentes destino del mensaje, y posiblemente puede llegar a mantener el historial de discusi�n que se lleva hasta el momento para que un agente ajeno a la discusi�n pueda llegar a "opinar" en base a su conocimiento actual.

        ___ _____ ___  
  ___  |   \_   _|   \ 
 |___| | |) || | | |) |
       |___/ |_| |___/ 
       
El DTD que dise�� es el siguiente:

<!DOCTYPE Dialogo [ 
    <!ELEMENT Dialogo (Mensaje)*>
        <!ELEMENT Mensaje (Agente_Origen, Agente_Destino, Argumento*)>
            <!ELEMENT Agente_Origen (#PCDATA)>
            <!ELEMENT Agente_Destino (#PCDATA)>
              <!ATTLIST Agente_Destino broadcast (si | no) #REQUIRED>
              
            <!ELEMENT Argumento (Derivacion, Estado?)>
              <!ATTLIST Argumento id CDATA #REQUIRED>
              <!ATTLIST Argumento id_ataque CDATA #IMPLIED>
                
              <!ELEMENT Conclusion (#PCDATA)>
              <!ELEMENT Derivacion (Regla*)>
                <!ELEMENT Regla (#PCDATA)>
                    <!ATTLIST Regla tipo (Default | Estricta) #REQUIRED>
                    
              <!ELEMENT Estado ( #PCDATA | Derrotado | NoDerrotado )*>
                <!ATTLIST Estado cerrado (si | no) #REQUIRED>
]>

***********
* Dialogo *
*********** 
El elemento Dialogo es una estructura auxiliar, la cual se utiliza para mantener los mensajes enviados hasta el momento. Esto es una visi�n de alto nivel conceptual que mantendr�a un agente en el dialogo con otros agentes para saber cu�l es el tema de la discusi�n actual.

    ***********
    * Mensaje *
    *********** 
    Un Mensaje es la unidad b�sica de comunicaci�n entre dos entidades, el cual mantiene un emisor (Agente_Origen) y uno o varios receptores (Agente_Destino). El contenido que se mantiene en el mensaje es un conjunto de argumentos dados por el dialogo entre las entidades.
        
        *****************
        * Agente_Origen *
        *****************
        En este campo no se mantiene mas que el nombre del agente origen.
        
        ******************
        * Agente_Destino *
        ******************
        El agente destino es la entidad a la cual va dirigido el mensaje. Posee un atributo denominado broadcast, el cual debe ir seteado en alguno de los valores booleanos y permite saber si este mensaje puede ser interceptado por otro agente.
        Se coloca este campo con el objetivo de dar posibilidad a otros agentes de incorporarse a la discusi�n.
        Si se coloca el campo broadcast en verdadero (si), el nombre del agente destino puede colocarse vacio.
        
        *************
        * Argumento *
        *************
        Un argumento, b�sicamente es cada uno de las conclusiones alcanzadas hasta este momento. Por esto, en su interior se mantiene la conclusi�n, el argumento que lleg� a esa conclusi�n y el estado actual de ese argumento.
        Para poder identificar los ataques, se incorpor� un campo id, el cual identifica al argumento y un id_ataque, el cual define al argumento que est� atacando la conclusi�n y derivaci�n expuesta.
        
            **************
            * Conclusi�n *
            **************
            La conclusi�n del argumento, mantiene los extremos del argumento. Una conclusi�n seria de la forma:
            
                    A � B
                    
            Donde A es un literal logrado por un proceso argumentativo y B es el conjunto de argumentos base que lo sostiene.
            
            **************
            * Derivaci�n *
            **************
            La derivaci�n, est� constituida por un conjunto de reglas DeLP, las cuales unen el proceso de uni�n entre los extremos de la conclusi�n.
            
                    *********
                    * Regla *
                    *********
                    Una regla, es un elemento del conjunto Pi o Delta de DeLP. Cada regla tiene un atributo que la define como Estricta o Default.
                    
            **********
            * Estado *
            **********
            El estado es un etiquetado del argumento, el cual tendr�a un potencial uso como el dado en los arboles de dial�ctica. Podr�a darse que un argumento est� derrotado o no derrotado, o mantener alg�n valor intermedio como abierto a discusi�n u opiniones de un tipo de agente espec�fico.
            Cada estado posee un atributo de cerrado, el cual mantiene que si un argumento est� cerrado, se toma como hecho lo que dice y no permitir�a posibles ataques en ese punto.
            
            
            
Al final del archivo <mensaje_xml_dtd.xml hay un ejemplo en el cual Agente_1 propone que si es una gallina, entonces vuela y da un argumento a favor de c�mo lleg� a esa conclusi�n.
Por otro lado, como la comunicaci�n era de tipo broadcast, el agente Agente_2 expone un argumento en el cual concluye que si es una gallina, entonces no vuela.
Al final, el agente Agente_3 expone un argumento m�s espec�fico que el argumento dado por el agente Agente_1 donde dice que si una gallina est� asustada, entonces vuela.

En el momento siguiente, si no existen m�s argumentos, se pueden cerrar esos argumentos y determinar cu�les fueron derrotados y cu�les no y exponer lo concluido hasta ese momento para ponerse en sincronizaci�n toda la informaci�n com�n entre los agentes.
