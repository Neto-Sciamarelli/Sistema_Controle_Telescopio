# Padrão de Logs de Auditoria

```json
{
  "timestamp_utc": "ISO-8601",
  "level": "AUDIT",
  "event_type": "AGENDAMENTO_CRIADO", 
  "service": "servico-agendamento",
  "details": {
      "agendamento_id": 123,
      "cientista_id": 7,
      "horario_inicio_utc": "YYYY-MM-DDTHH:MM:SSZ"
  }
}