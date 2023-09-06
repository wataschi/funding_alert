### Funding Alert

Busca los Funding Fee usando la API de coinglass

**Como usar el script**
- Crear una cuenta en coinglass [Aqui](https://www.coinglass.com/pricing/ "Aqui") y "Obtener clave de API gratuita"
- Instale las librerias necesarias con el siguiente comando:
```python
pip install -r requirements.txt
```
- Renombre o copie el archivo config.example.json y cambielo a config.json
- edite el archivo config.json
  - coinglass_apikey: aqui digite la api
  - funding: valor minimo de buscar monedas ej. 0.5 busca monedas con funding mayor a 0.5 o menor a -0.5
  - minutos_revision: tiempo en minutos para consultar por defecto esta en 5 minutos

- Para ejecutarlo abra una terminal y digite el siguiente comando:
`python main.py`
- Para editarlo les recomiendo VSCode [Aqui](https://code.visualstudio.com/ "Aqui")
