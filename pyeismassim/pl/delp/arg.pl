:- [delp]. % int�rprete

:- consult('arg.delp'), % reglas de argumentaci�n
   consult('mundo3.delp'). % hechos asertados en una situaci�n del mundo particular

% criterios de comparaci�n

% greaterArgValue est� definido m�s abajo, y lo que hace es buscar los argValue de los argumentos, si es que existen, para compararlos
:- comparison_on(greaterArgValue),
% defeater2assumption es un criterio que establece derrota cuando uno de los argumentos es una asunci�n, es derrotado por cualquier otra cosa que tenga algo.
   comparison_on(defeater2assumption),
% more_specific es la espeficidad de siempre.
   comparison_on(more_specific).

% todos los predicados que siguen son operaciones aritm�ticas y de comparaci�n, para que los use delp.
is_a_built_in(mult(X,Y,Z)).
is_a_built_in(add(X,Y,Z)).
is_a_built_in(sust(X,Y,Z)).
is_a_built_in(power(X,Y,Z)).
is_a_built_in(greater(X,Y)).
is_a_built_in(less(X,Y)).
is_a_built_in(greaterEq(X,Y)).
is_a_built_in(lessEq(X,Y)).
is_a_built_in(equal(X,Y)).
is_a_built_in(notEqual(X,Y)).

% Operaciones aritm�ticas
mult(X,Y,Z)    :- Z is X * Y.
add(X,Y,Z)     :- Z is X + Y.
sust(X,Y,Z)    :- Z is X - Y.
power(X,Y,Z)   :- Z is X ** Y.
greater(X,Y)   :- X > Y.
less(X,Y)      :- X < Y.
greaterEq(X,Y) :- X >= Y.
lessEq(X,Y)    :- X =< Y.
equal(X,Y)     :- X =:= Y. % este es el igual, pero no instancia, s�lo chequea igualdad. (O sea, no es el mismo que el =, que si instancia.)
notEqual(X,Y)  :- X \= Y.


% posibleMeta(+Meta, -Prioridad)
% La Meta tendr� una prioridad �nica, que le dar� su orden de importancia
% Valor m�s alto => mayor prioridad.
posibleMeta(explorar(_), 1).
posibleMeta(expansion(_), 2).

% posibleMetaNeg(+Meta)
% Chequea que el par�metro ingresado sea una meta, as� est� negada.
posibleMetaNeg(explorar(_)).
posibleMetaNeg(expansion(_)).
posibleMetaNeg(~explorar(_)).
posibleMetaNeg(~expansion(_)).

% criterio de comparaci�n greaterArgValue
greaterArgValue(arg([Ac | Acs], _), arg([Bc | Bcs], _)) :-
    (
        Ac = s_rule(HeadA, _)
        ;
        Ac = d_rule(HeadA, _)
    ), !,
    posibleMetaNeg(HeadA), 
    (
        Bc = s_rule(HeadB, _)
        ;
        Bc = d_rule(HeadB, _)
    ), !,
    % member(HeadA, [explorar(_), expansion(_), ~explorar(_), ~expansion(_)]),
    % member(HeadB, [explorar(_), expansion(_), ~explorar(_), ~expansion(_)]), 
    
    posibleMetaNeg(HeadB), % con esto checkeo que s�lo entren las posibles metas
    % writeln([Ac | Acs]),
    % writeln([Bc | Bcs]),
    member(s_rule(argValue(ValA),true), Acs), !,
    % writeln(ValA),
    member(s_rule(argValue(ValB),true), Bcs), !,
    % writeln(ValB),
    % writeln('greater'),
    resolveConflict(ValA, ValB, [Ac | Acs], [Bc | Bcs]).
    
% resolveConflict(+ValA, +ValB, +Ac, +Bc)
% Los Vals son los argValues de los argumentos.
% Los otros son las secuencias argumentativas
resolveConflict(ValA, ValB, _, _) :-
    ValA > ValB, !.
    
resolveConflict(Val, Val, Ac, Bc) :- % este predicado toma las metas y con eso llama a equalArgValues
    member(d_rule(HeadA, _), Ac),
    posibleMeta(HeadA, _), !,
    member(d_rule(HeadB, _), Bc),
    posibleMeta(HeadB, _), !,
    equalArgValues(HeadA, HeadB).
     
equalArgValues(HeadA, HeadB) :- % Son la misma meta. Comparo por los argumentos
    HeadA =.. [Meta | ArgAs],
    HeadB =.. [Meta | ArgBs],
    ArgAs @<ArgBs. % esta es la comparaci�n de t�rminos.
 
% falta testear!!!
equalArgValues(HeadA, HeadB) :- % Son metas distintas. Veo cu�l est� primero en el orden de prioridad
    % write('hola'), % Quinto a�o de la carrera y write 'hola' (dir�a el vasco :P)
    % HeadA =.. [MetaA | ArgAs],
    % HeadB =.. [MetaB | ArgBs],
    posibleMeta(HeadA, ValueA),
    posibleMeta(HeadB, ValueB),
    
    ValueA > ValueB.