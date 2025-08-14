@echo off
REM Ir al directorio del proyecto
cd /d C:\Aut_Bekilly\Extraccion_SII_BekillyAPP

REM Activar entorno virtual
call .venv\Scripts\activate

REM Ejecutar instalación (si es primera vez o quieres reinstalar)
python -m pip install -U pip
python -m pip install .

REM Ejecutar la app
python main.py --config config\sample_config.yaml
