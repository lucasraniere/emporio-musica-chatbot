# Informações gerais da loja: apresentação, endereço e horários

O agente se apresenta com a persona da loja e responde endereço, horários e contato a partir do manual de políticas, usando a data e a hora atuais para dizer se a loja ainda está aberta.

_Modelo: claude-sonnet-5-5 | Executado em: 13/11/2026 17:03_

---

**Cliente:** Ola, me chamo Lucas. Com quem eu falo?

**Clave:** Oi, Lucas! Aqui é a Clave, assistente virtual da Empório da Música, a loja de instrumentos musicais de Campo Grande/MS. 🎶

Posso te ajudar com informações sobre produtos, preços, promoções, pedidos, trocas, entregas e o que mais precisar. Como posso te ajudar hoje?

**Cliente:** Qual o endereco da loja?

> tool: `search_policies(query='endereço da loja')`

**Clave:** Lucas, a loja fica na Rua 14 de Maio, 3200, Centro, Campo Grande - MS, CEP 79202-333.

Horários de atendimento:
- Segunda a sexta: 09:00 às 18:00
- Sábado: 09:00 às 13:00
- Domingo e feriados: fechado

Hoje é sexta e ainda dá tempo: a loja fecha às 18:00. Se quiser falar com a gente, o telefone/WhatsApp é (67) 3341-4444.

Posso te ajudar em mais alguma coisa?

**Cliente:** Era so isso. Obrigado pelas informacoes!

**Clave:** Por nada, Lucas! Foi um prazer te ajudar. Quando precisar, é só chamar. Bom fim de semana e boa música! 🎸
