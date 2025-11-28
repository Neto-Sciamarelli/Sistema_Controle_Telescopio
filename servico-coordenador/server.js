const express = require('express');
const app = express();
app.use(express.json());

// Armazena os locks em memória: { "nome_recurso": true }
const locks = {};

app.post('/lock', (req, res) => {
    const { recurso } = req.body;
    
    console.log(`[Coordenador] Recebido pedido de lock para: ${recurso}`);

    if (locks[recurso]) {
        console.log(`[Coordenador] Recurso ${recurso} JÁ ESTÁ em uso. Negando.`);
        return res.status(409).json({ status: 'ocupado' });
    }

    locks[recurso] = true;
    console.log(`[Coordenador] Lock CONCEDIDO para: ${recurso}`);
    return res.status(200).json({ status: 'travado' });
});

app.post('/unlock', (req, res) => {
    const { recurso } = req.body;
    
    if (locks[recurso]) {
        delete locks[recurso];
        console.log(`[Coordenador] Lock LIBERADO para: ${recurso}`);
    } else {
        console.log(`[Coordenador] Pedido de unlock para recurso livre: ${recurso}`);
    }
    
    return res.status(200).json({ status: 'liberado' });
});

const PORT = 3000;
app.listen(PORT, () => {
    console.log(`Serviço Coordenador rodando na porta ${PORT}`);
});