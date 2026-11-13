# Produto sem estoque, promoção inexistente, acessórios e desconto no PIX

O cliente pergunta por um produto esgotado citando um desconto de 40% que não está ativo. O agente verifica estoque e promoções vigentes antes de responder, sugere alternativas disponíveis, explica que a loja não vende acessórios e esclarece a regra do desconto no PIX.

_Modelo: claude-sonnet-5-5 | Executado em: 13/11/2026 17:08_

---

**Cliente:** Tem o Giannini GF-3D? Vi que estava com 40% de desconto

> tool: `get_product_details(product='Giannini GF-3D')`

> tool: `list_active_promotions()`

> tool: `search_products(category='Violões', keywords='dreadnought', max_price=1500)`

**Clave:** Infelizmente o Giannini GF-3D Dreadnought Sunburst está sem estoque no momento. Também não achei promoção de 40% nele. Ele aparece por R$ 799,90 (no PIX: R$ 759,90), sem desconto. Hoje não tem nenhuma promoção de 40% ativa na loja.

Tenho alguns violões parecidos disponíveis:
- Shelby SGD-195E Elétrico Aço Sunburst: R$ 799,00 (no PIX: R$ 759,05), 6 em estoque
- Tagima Woodstock Dreadnought Natural: R$ 899,00 (no PIX: R$ 854,05), 11 em estoque
- Yamaha FG800 Dreadnought Natural: R$ 1.299,00 (no PIX: R$ 1.234,05), 7 em estoque

Quer que eu detalhe algum deles? Posso ajudar em mais alguma coisa?

**Cliente:** Vocês vendem cordas?

**Clave:** Não, a loja só vende instrumentos musicais, então não trabalhamos com cordas, nem com outros acessórios como cabos, palhetas, pedais, amplificadores e cases.

Se quiser, posso te ajudar a escolher um dos violões que te mostrei. Posso ajudar em mais alguma coisa?

**Cliente:** E no pix, tem desconto mesmo?

> tool: `search_policies(query='desconto no PIX')`

**Clave:** Tem sim! No PIX você ganha 5% de desconto sobre o preço de tabela, com pagamento à vista.

Esse desconto não vale para produtos que já estão em promoção. Nesses, vale só o preço promocional.

A loja também aceita:
- Cartão de débito, à vista
- Cartão de crédito, em até 12x sem juros, com parcela mínima de R$ 100,00
- Boleto bancário, à vista, com compensação em até 3 dias úteis

Posso ajudar em mais alguma coisa?

**Cliente:** Muito obrigado!

**Clave:** Por nada! Foi um prazer ajudar. Se quiser saber mais sobre algum violão, é só chamar. Bons acordes! 🎸
