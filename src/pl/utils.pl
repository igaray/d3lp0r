﻿:- [graph/map].
:- dynamic isGoal/1, isFail/1, isFail/2.

% pathSearch(-InitialNode, -FinalNode, -Energy, -ActionToBeDone, -CostOfAction, +Path, +Actions, +PathCost)
% wrapper para la uniform cost search.
% asserta isGoal y lo retracta al final.
% instancia todos los parametros para llamar a ucs
% ucs assertara todos los resultados que haya podido alcanzar, para minimizar el costo de la busqueda
pathSearch(InitialNode, FinalNode, Energy, ActionToBeDone, CostOfAction, Path, Plan, NewTurns2, RemainingEnergy1) :-
    retractall(isGoal(_)),	
    assert(isGoal(ucsNode(FinalNode, _, _, _, _))),
    singleton_heap(InitialFrontier, 0, ucsNode(InitialNode, Energy, [], [], 0)),
    %write('pathSearch, final node:'), writeln(FinalNode),
    ucsAux(InitialFrontier, [], Path, Actions, PathCost, NewEnergy), 
    length(ActionToBeDone, ActionToBeDoneTurns),
    NewTurns is PathCost + ActionToBeDoneTurns,
    calcRecharge(NewEnergy, CostOfAction, ActionToBeDone, NewActions, NewTurns, NewTurns2, RemainingEnergy1),
    append(Actions, NewActions, Plan),
    not(isFail(ucsNode(FinalNode, RemainingEnergy1, Path, Plan, NewTurns2))), !,
    assert(b(path(InitialNode, FinalNode, ActionToBeDone, Energy, Path, Plan, NewTurns2, RemainingEnergy1))).    

% ucs(-Frontier, -Visited, +Path, +Actions, +Path_Cost)
% Frontier: frontera del recorrido.
% Visited: conjunto de visitados.
% Energy : energia actual
% Path: camino retornado. (lo retornara al reverso)
% Actions: lista de acciones necesarias para llegar al nodo.
% Path_Cost: costo del camino encontrado.
ucsAux(_Frontier, _Visited, [Position | Path], Actions, PathCost, Energy) :-
    b(ucsNode(Position, Energy, Path, Actions, PathCost)),
    isGoal(ucsNode(Position, Energy, Path, Actions, PathCost)), !.
    
ucsAux(_Frontier, _Visited, _Path, _Actions, _PathCost, _Energy) :-
    b(lastUcs(Frontier1, _)),
    empty_heap(Frontier1), !, 
    fail.
    
ucsAux(_Frontier, _Visited, Path, Actions, PathCost, Energy) :-
    b(lastUcs(Frontier1, Visited)), !, 
    ucs(Frontier1, Visited, Path, Actions, PathCost, Energy).
    
ucsAux(Frontier, Visited, Path, Actions, PathCost, Energy) :-
    ucs(Frontier, Visited, Path, Actions, PathCost, Energy), !.

ucs(Frontier, Visited, [Position | Path], Actions, Path_Cost, Energy) :-
    ucsSelect(Frontier, Visited, ucsNode(Position, Energy, Path, Actions, Path_Cost), _Frontier1),
    retractall(b(lastUcs(_, _))),    
    isGoal(ucsNode(Position, Energy, Path, Actions, Path_Cost)), !,
    ucsNeighbors(ucsNode(Position, Energy, Path, Actions, Path_Cost), Neighbors),
    addToFrontier(Neighbors, Frontier, FrontierNew, Visited, NewVisited), %
    assert(b(lastUcs(FrontierNew, NewVisited))), 
    assert(b(ucsNode(Position, Energy, Path, Actions, Path_Cost))).
	
ucs(Frontier, Visited, SolutionPath, SolutionActions, Cost, Energy) :-
    ucsSelect(Frontier, Visited, SelectedNode, Frontier1),
    ucsNeighbors(SelectedNode, Neighbors),
    addToFrontier(Neighbors, Frontier1, FrontierNew, Visited, NewVisited), % !,
    assert(b(lastUcs(FrontierNew, NewVisited))), 
    assert(b(SelectedNode)),
    ucs(FrontierNew, [SelectedNode | NewVisited], SolutionPath, SolutionActions, Cost, Energy).

ucsSelect(OldFrontier, Visited, Node, NewFrontier) :-
    get_from_heap(OldFrontier, _P, Node2, Frontier),
    ucsSelectAux(Node2, Frontier, Visited, Node, NewFrontier).
    
ucsSelectAux(ucsNode(Position, _, _, _, _), Frontier, Visited, Node, NewFrontier) :-
    member(ucsNode(Position, _, _, _, _), Visited), !,
    ucsSelect(Frontier, Visited, Node, NewFrontier).

ucsSelectAux(Node, Frontier, _Visited, Node, Frontier).
    
addToFrontier([], Frontier, Frontier, Visited, Visited).
        
addToFrontier([Neighbor | Neighbors], OldFrontier, Frontier, OldVisited, Visited) :-
    Neighbor = ucsNode(Node,  _, _, _, _),
	foreach(member(ucsNode(N, _, _, _, _), OldVisited), Node \= N), !,
	insert_pq(Neighbor, OldFrontier, NewFrontier),
    addToFrontier(Neighbors, NewFrontier, Frontier, OldVisited, Visited).
    
addToFrontier([_Neighbor | Neighbors], OldFrontier, Frontier, OldVisited, Visited) :-
    !,
    addToFrontier(Neighbors, OldFrontier, Frontier, OldVisited, Visited).
    
insert_pq(ucsNode(Position, Energy, Path, Actions, Path_Cost), Old, New) :-
    add_to_heap(Old, Path_Cost, ucsNode(Position, Energy, Path, Actions, Path_Cost), New).

% ucsNeighbors(-UcsNode, -Energy, +Neighbors)
% UcsNode: el nodo actual.
% Energy: energia actual.
% Neighbors: lista con un ucsNodes por cada vecino.
ucsNeighbors(ucsNode(Position, Energy, Path, Actions, Path_Cost), Neighbors) :-
    findall(
        Node, 
        (
            k(edge(Position, Node, V)), 
            V \= unknown
        ), 
        Neigh
    ),
    calcActions(Position, Energy, Neigh, ListOfActions),
    calcUcsNodes(Position, Path, Actions, Path_Cost, ListOfActions, Neighbors).

% calcUcsNodes(-Position, -Path, -Actions, -PathCost, -ListOfCalcActions, +ListOfUcsNodes)
% Position: posicion actual
% Path: camino a la posicion actual
% Actions: lista de acciones hasta la posicion actual
% PathCost: costo del camino hasta la posicion actual
% ListOfCalcActions: lista que contiene, para cada vecino, una lista de la forma [nombre, turnos que lleva llegar, energía restante, lista de acciones necesarias].
% ListOfUcsNodes: lista con la informacion de cada nodo vecino con la forma ucsNode(_).
calcUcsNodes(_Position, _Path, _Actions, _PathCost, [], []).

calcUcsNodes(Position, Path, Actions, PathCost, [[Neigh, Turns, RemainingEnergy, ListOfActions] | ListOfListOfActions], Neighbors2) :-
    append(Actions, ListOfActions, NewActions),
    NewPathCost is PathCost + Turns,
    calcUcsNodesAux(Position, Path, Actions, PathCost, ListOfListOfActions, ucsNode(Neigh, RemainingEnergy, [Position | Path], NewActions, NewPathCost), Neighbors2).

calcUcsNodesAux(Position, Path, Actions, PathCost, ListOfListOfActions, UcsNode, Neighbors) :-
    isFail(UcsNode), !,
    calcUcsNodes(Position, Path, Actions, PathCost, ListOfListOfActions, Neighbors).
    
calcUcsNodesAux(Position, Path, Actions, PathCost, ListOfListOfActions, UcsNode, [UcsNode | Neighbors]) :-
    calcUcsNodes(Position, Path, Actions, PathCost, ListOfListOfActions, Neighbors).
    
% calcActions(-Pos, -Energy, -NeighborsList, +ListOfActions)
% Pos: posicion actual.
% Energy: energía actual.
% NeighborsList: lista de vecinos de la posición actual.
% ListOfActions: lista que contiene, para cada vecino, una lista de la forma [nombre, turnos que lleva llegar, energía restante, lista de acciones necesarias].
calcActions(_Pos, _Energy, [], []).

	
calcActions(Pos, Energy, [Neigh | Neighs], [[Neigh, Turns, RemainingEnergy, ListOfActions] | ListOfListOfActions]) :-
    k(edge(Pos, Neigh, Value)),
    calcRecharge(Energy, Value, [[goto, Neigh]], ListOfActions, 1, Turns, RemainingEnergy), !,
    calcActions(Pos, Energy, Neighs, ListOfListOfActions).
    
calcActions(Pos, Energy, [_Neigh | Neighs], ListOfListOfActions) :-
    calcActions(Pos, Energy, Neighs, ListOfListOfActions).
    

% calcRecharge(-Energy, -Value, -OldList, +NewList, -Turns, +NewTurns, +RemainingEnergy)
% Energy: energia actual del agente en la suposicion que se movio
% Value: valor del arco
% OldList: acciones actualmente calculadas
% NewList: acciones a devolver.
% Turns: turnos usados actualmente.
% NewTurns: turnos usados por todas las acciones.
% RemainingEnergy: Energia restante al terminar de ejecutar las acciones.
calcRecharge(Energy, _Value, _OldList, _OldList2, _Turns, _Turns2, _RemainingEnergy) :- 
    currentStep(Step),
    myName(Name),
    maxEnergy(Step, Name, Max),
    Energy > Max, !,
    fail.

calcRecharge(Energy, Value, OldList, OldList, Turns, Turns, RemainingEnergy) :-
    Energy >= Value, !,
    RemainingEnergy is Energy - Value.

calcRecharge(Energy, Value, OldList, NewList, OldTurns, NewTurns2, RemainingEnergy) :-
    myRechargeEnergy(RechargeEnergy),
    NewTurns is OldTurns + 1,
    NewEnergy is Energy + RechargeEnergy,
    calcRecharge(NewEnergy, Value, [[recharge] | OldList], NewList, NewTurns, NewTurns2, RemainingEnergy).

% wrapper para usar el BFS
breadthFirst(InitialNode, FinalNode, Path, Cost) :-
    bfs([bfsNode(InitialNode, [InitialNode], 0)], [InitialNode], bfsNode(FinalNode, Path, Cost)).

bfs([bfsNode(Node, Path, Cost) | _RestOfFrontier], _Visited, bfsNode(Node, Path, Cost)) :- 
    isGoal(Node, Cost).
    
bfs([bfsNode(Node, Path, Cost) | RestOfFrontier], Visited, Result) :- 
    findall(Neighbor,
            k(edge(Node, Neighbor, _)),
            Neighbors),
	filter(bfsNode(Node, Path, Cost), Neighbors, RestOfFrontier, Visited, FilteredNeighbors),
    add_list_to_queue(FilteredNeighbors, Path, Cost, RestOfFrontier, NewFrontier), 
    add_to_set(bfsNode(Node, Path, Cost), Visited, NewVisited),
    bfs(NewFrontier, NewVisited, Result).

filter(bfsNode(_Node, _Path, Cost), Neighbors, Frontier, Visited, FilteredNodes) :-
	Cost2 is Cost + 1,
	findall(
        Neigh, 
        (
            member(Neigh, Neighbors), 
            not(member(bfsNode(Neigh, _P, _C), Frontier)), 
            not(member(bfsNode(Neigh, _P2, _C2), Visited)),
			not(isFail(Neigh, Cost2))
        ),
        FilteredNodes).
	
add_list_to_queue([], _Path, _Cost, Queue, Queue).
add_list_to_queue([H|T], Path, Cost, Queue, NewQueue) :-
	NewCost is Cost + 1,
    add_to_queue(bfsNode(H, [H | Path], NewCost), Queue, TempQueue),
    add_list_to_queue(T, Path, Cost, TempQueue, NewQueue).

    add_to_queue(E, L, [E|L]).

remove_from_queue(E, [E|T], T).

append_queue(First, Second, Concatenation) :- 
    append(First, Second, Concatenation).
	
add_to_set(X, S, S) :- member(X, S), !.
add_to_set(X, S, [X|S]).	
