# regras simples de alerta
# Exemplo: se enterococos > 104 -> vermelho, > 35 -> amarelo
def avalia_leituras_e_gera_alerta(session, Praia, Leitura, Alerta):
    praias = session.query(Praia).all()
    for praia in praias:
        # 1. Buscar ultima leitura de enterococos (como antes)
        leitura_enterococos = (
            session.query(Leitura)
            .filter(Leitura.praia_id == praia.id, Leitura.parametro == "enterococos")
            .order_by(Leitura.timestamp.desc())
            .first()
        )

        if leitura_enterococos:
            # 2. Determinar o nível do alerta (como antes)
            nivel = "verde"
            if leitura_enterococos.valor > 104:
                nivel = "vermelho"  # Imprópria
            elif leitura_enterococos.valor > 35:
                nivel = "amarelo"   # Atenção

            # 3. Se o nível justificar um alerta, construir a nova mensagem
            if nivel != "verde":
                # --- LÓGICA MODIFICADA PARA CRIAR A MENSAGEM ---

                # Buscar a última temperatura da água para a mesma praia
                leitura_temperatura = (
                    session.query(Leitura)
                    .filter(Leitura.praia_id == praia.id, Leitura.parametro == "temperatura_agua")
                    .order_by(Leitura.timestamp.desc())
                    .first()
                )
                
                # Formatar a temperatura para a mensagem (ou usar um valor padrão)
                temp_str = f"{leitura_temperatura.valor:.1f}" if leitura_temperatura else "N/A"
                
                # Extrair o nome da cidade da descrição da praia
                cidade = praia.descricao.replace("Praia localizada em ", "") if praia.descricao else "Local não informado"

                # Construir a nova mensagem amigável
                mensagem_final = (
                    f"Alerta em {praia.nome} ({cidade}): "
                    f"Qualidade da água está {nivel.upper()}! "
                    f"Temperatura: {temp_str}°C."
                )

                # Criar o alerta com a nova mensagem
                alerta = Alerta(praia_id=praia.id, nivel=nivel, mensagem=mensagem_final)
                session.add(alerta)

    session.commit()