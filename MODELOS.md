# Modelos de Entidade

## Cientista
- **id**: Inteiro, Chave Primária
- **nome**: String, Nome do pesquisador

## Agendamento
- **id**: Inteiro, Chave Primária
- **cientista_id**: Inteiro, Chave Estrangeira
- **data_horario**: DateTime, Horário reservado (ex: 2025-12-01T03:00:00Z)
- **telescopio**: String (ex: "Hubble-Acad")