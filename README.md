# IA-BOT-UGR-23

[![](https://img.shields.io/badge/language-Python-green.svg)](https://www.python.org/)
[![](https://img.shields.io/badge/license-GPL-orange.svg)](https://www.gnu.org/licenses/gpl.html)
[![](https://img.shields.io/badge/subject-Inteligencia_Artificial-blue)]()
[![](https://img.shields.io/badge/university-Universidad_de_Granada-8A2BE2)]()
[![](https://img.shields.io/badge/year-2022/2023-yellow)]()


Bot utilizado en las prácticas de Inteligencia Artificial de la UGR durante el curso 2022/2023 🫡❤️

## Requisitos
- `python` (v 3.8)
- `python-telegram-bot` (v 20.2)
- `requests` (v 2.28.2)
- `bash`
- `slurm`
- ...

## Descripción

El bot está diseñado para ser ejecutado en un cluster que utilice `slurm` como gestor de colas. El bot es un proceso permanente (el script `bot.py`) que se ejecuta en un nodo del cluster, y que recibe las peticiones de los usuarios a través de `Telegram`. Este se encarga de gestionar las peticiones, y de enviarlas al gestor de colas para que se ejecuten en el cluster una por una.

## Agradecimientos

A @rbnuria, la mejor compañera de prácticas que se puede tener, y al resto de profesores de la asignatura por su colaboración.

Y, por supuesto, a mis alumnos y alumnas, que me han dado la ilusión y la motivación para hacer este proyecto. Gracias por este año.