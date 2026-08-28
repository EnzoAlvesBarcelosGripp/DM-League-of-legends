set -e # Interrompe caso qualquer etapa falhe

echo "Iniciando Pipeline ETL..."
python Src/01_Extraction/main.py
python Src/03_Transform/main.py
python Src/04_Validação/main.py
python Src/05_Load_final/main.py
echo "Pipeline concluído com sucesso!"