# Especificação da API

## POST /agendamentos
Cria um novo agendamento.
- **Input**: JSON { "cientista_id": 1, "data_horario": "2025...", "telescopio": "Hubble" }
- **Output**: 201 Created ou 409 Conflict

## GET /agendamentos
Lista agendamentos.
- **HATEOAS**: Cada item deve conter links para "self" e "delete".

## DELETE /agendamentos/<id>
Remove um agendamento.

## GET /time
Retorna o horário atual do servidor para sincronização (Algoritmo de Cristian).